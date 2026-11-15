#!/usr/bin/env bash
# Prove that a database backup can be restored, without touching production.
#
# Restores a Dokploy volume backup of the Postgres volume into a throwaway Docker volume,
# starts Postgres 16 on it (same major version as production: a data directory only opens
# with the version that wrote it), and prints what it contains.
#
# Usage:
#   ./check-backup.sh <archive> <POSTGRES_USER> <POSTGRES_DB>
#
#   <archive>        backup downloaded from the S3 destination (.tar, .tar.gz/.tgz or .tar.zst)
#   POSTGRES_USER/DB values from the production .env (no password needed: local connection)
#
# Requires Docker. Nothing is published on the network, and everything is removed at the end.
set -euo pipefail

if [[ $# -ne 3 ]]; then
  sed -n '2,15p' "$0"
  exit 1
fi

ARCHIVE="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
DB_USER="$2"
DB_NAME="$3"
PG_IMAGE="postgres:16"
NAME="giftplanner-backup-check-$$"

cleanup() {
  docker rm -f "$NAME" >/dev/null 2>&1 || true
  docker volume rm "$NAME" >/dev/null 2>&1 || true
}
trap cleanup EXIT

[[ -f "$ARCHIVE" ]] || { echo "Archive not found: $ARCHIVE" >&2; exit 1; }

# The archive format is detected from its content, not trusted from its name.
case "$(head -c 4 "$ARCHIVE" | od -An -tx1 | tr -d ' \n')" in
  1f8b*)    DECOMPRESS="gzip -dc" ;;
  28b52ffd) DECOMPRESS="zstd -dc" ;;
  *)        DECOMPRESS="cat" ;;
esac
echo "==> Archive: $ARCHIVE ($(du -h "$ARCHIVE" | cut -f1), ${DECOMPRESS%% *})"

echo "==> Extracting into a throwaway volume"
docker volume create "$NAME" >/dev/null
# postgres:16 is Debian-based: GNU tar keeps the original owners (uid 999 = postgres).
docker run --rm -i -v "$NAME":/restore --entrypoint sh "$PG_IMAGE" -c '
  set -e
  if [ "$1" = "zstd -dc" ]; then
    apt-get update -qq >/dev/null && apt-get install -y -qq zstd >/dev/null
  fi
  $1 | tar -x -C /restore
' sh "$DECOMPRESS" < "$ARCHIVE"

# Find the data directory inside the archive (it may be at the root or in a subfolder).
PGDATA_IN_VOLUME="$(docker run --rm -v "$NAME":/restore --entrypoint sh "$PG_IMAGE" -c \
  'f=$(find /restore -maxdepth 4 -name PG_VERSION -path "*/PG_VERSION" | head -1); [ -n "$f" ] && dirname "$f"')" || {
  echo "No Postgres data directory (PG_VERSION) in this archive. Is it the right volume?" >&2
  exit 1
}
VERSION="$(docker run --rm -v "$NAME":/restore --entrypoint cat "$PG_IMAGE" "$PGDATA_IN_VOLUME/PG_VERSION")"
echo "==> Data directory: $PGDATA_IN_VOLUME (written by Postgres $VERSION)"
[[ "$VERSION" == "16" ]] || { echo "This script starts Postgres 16, the archive needs Postgres $VERSION." >&2; exit 1; }

echo "==> Starting Postgres on the restored data"
docker run -d --name "$NAME" -v "$NAME":/restore -e PGDATA="$PGDATA_IN_VOLUME" \
  --entrypoint sh "$PG_IMAGE" -c "chown -R postgres:postgres '$PGDATA_IN_VOLUME' && exec gosu postgres postgres" >/dev/null

for _ in $(seq 1 60); do
  docker exec "$NAME" pg_isready -q -U "$DB_USER" -d "$DB_NAME" 2>/dev/null && break
  sleep 1
done
docker exec "$NAME" pg_isready -q -U "$DB_USER" -d "$DB_NAME" || {
  echo "Postgres did not start on this data:" >&2
  docker logs --tail 30 "$NAME" >&2
  exit 1
}

echo "==> Content"
docker exec "$NAME" psql -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 -P pager=off -c "
  SELECT 'schema (alembic)' AS what, version_num AS value FROM alembic_version
  UNION ALL SELECT 'users',      count(*)::text FROM users
  UNION ALL SELECT 'recipients', count(*)::text FROM recipients
  UNION ALL SELECT 'gifts',      count(*)::text FROM gifts
  UNION ALL SELECT 'last gift added', coalesce(max(created_at)::text, '-') FROM gifts;
"
echo "==> OK: this backup restores. Compare the numbers with what you expect, then it is cleaned up."
