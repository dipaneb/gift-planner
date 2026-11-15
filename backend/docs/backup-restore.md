# Database backups: check and restore

The production database is the `db` service of `docker-compose.prod.yml` (Postgres 16).
Its data lives in the Docker volume `gift-planner-backend-sbvqd0_postgres_data_prod`.

Dokploy backs this volume up every night at 4:00 (Volume Backups of the compose service):
it stops the container, archives the volume, starts it again, and uploads the archive to the
configured S3 destination. Copying the files of a *stopped* Postgres gives a consistent backup.

> A backup that was never restored is a hope, not a backup. Check one every month,
> and after any change to the backup settings, the volume or the Postgres version.

## What must stay true

- **The destination is off the server** (S3, R2, B2...). A backup on the same disk dies with it.
- **Retention covers a mistake noticed late**: keep at least 14 daily backups.
- **Same Postgres major version to restore**: a data directory only opens with the version
  that wrote it (16 today). Before upgrading Postgres, take a `pg_dump` (portable) as well.

## Monthly check (5 minutes, production untouched)

On any machine with Docker (your laptop works):

1. Download the latest archive from the S3 destination.
2. Run, with `POSTGRES_USER` and `POSTGRES_DB` from the production `.env`:

   ```bash
   backend/scripts/check-backup.sh ~/Downloads/<archive> <POSTGRES_USER> <POSTGRES_DB>
   ```

3. It restores the archive into a throwaway volume, starts Postgres 16 on it and prints the
   schema version and the number of users, recipients and gifts. Compare with the app:
   the numbers should match the state of the night of the backup. Everything is removed after.

If it fails, the backups are not usable: fix that before anything else.

## Restoring production

Only after the monthly check above succeeded **on the archive you are about to restore**:
it also tells you where the data is inside the archive (`Data directory:` line).

On the server, as root:

```bash
VOLUME=gift-planner-backend-sbvqd0_postgres_data_prod
mkdir -p /root/restore && cd /root/restore
# Put the archive here, named backup.tar.gz (any of .tar, .tar.gz, .tar.zst works with the same name)
```

1. **Stop the compose service** in Dokploy (API and database): nothing may write during the restore.
2. **Keep a copy of the current state**, in case the restore makes things worse:

   ```bash
   docker run --rm -v "$VOLUME":/source -v /root/restore:/backup postgres:16 \
     tar czf "/backup/before-restore-$(date +%F-%H%M).tar.gz" -C /source .
   ```

3. **Replace the volume content with the backup.** If the check printed
   `Data directory: /restore`, use `STRIP=0`; if it printed `/restore/<folder>`, use `STRIP=1`.

   ```bash
   STRIP=0
   docker run --rm -v "$VOLUME":/target -v /root/restore:/backup postgres:16 sh -c \
     "find /target -mindepth 1 -delete && tar xf /backup/backup.tar.gz -C /target --strip-components=$STRIP"
   ```

4. **Start the compose service** in Dokploy. The API runs `alembic upgrade head` on start,
   which brings an older backup up to the current schema.
5. **Check in the app** that the data is back, then delete `/root/restore` once you are sure.

To undo: same step 3 with the `before-restore-*.tar.gz` archive.
