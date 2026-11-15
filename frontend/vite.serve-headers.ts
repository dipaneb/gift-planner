import { loadEnv, type Plugin } from "vite";

/**
 * Production HTTP headers for the built site.
 *
 * In production (Dokploy), `dist/` is served by `serve` (https://github.com/vercel/serve),
 * which reads `serve.json` from the folder it serves. This plugin writes that file at build
 * time, so the Content-Security-Policy always allows the API the bundle actually calls
 * (VITE_BACKEND_URL), instead of a copy of that URL that would drift.
 *
 * Careful: `serve` validates serve.json against a schema and refuses to start if it is
 * invalid. Check any change with `pnpm build-only && npx serve@14 -s dist`.
 */
export function buildServeConfig(apiOrigin: string) {
  const contentSecurityPolicy = [
    "default-src 'self'",
    // No inline script and no eval: an injected <script> will not run.
    "script-src 'self'",
    // Vue and Nuxt UI set inline style attributes.
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data:",
    "font-src 'self'",
    `connect-src 'self' ${apiOrigin}`,
    "object-src 'none'",
    "base-uri 'self'",
    "form-action 'self'",
    "frame-ancestors 'none'",
  ].join("; ");

  const header = (key: string, value: string) => ({ key, value });

  return {
    headers: [
      {
        source: "**",
        headers: [
          header("Content-Security-Policy", contentSecurityPolicy),
          // Only ever reach the site over HTTPS (1 year)
          header("Strict-Transport-Security", "max-age=31536000"),
          // No framing by other sites (clickjacking), for browsers ignoring frame-ancestors
          header("X-Frame-Options", "DENY"),
          header("X-Content-Type-Options", "nosniff"),
          // Reset and verification links carry their token in the URL: never send it elsewhere
          header("Referrer-Policy", "no-referrer"),
          header("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=()"),
          // index.html must be revalidated, or visitors keep the previous version after a deploy
          header("Cache-Control", "no-cache"),
        ],
      },
      {
        // Vite puts a content hash in these names: a changed file gets a new name.
        // Listed after "**" so this Cache-Control wins.
        source: "assets/**",
        headers: [header("Cache-Control", "public, max-age=31536000, immutable")],
      },
    ],
  };
}

export function serveHeaders(): Plugin {
  let apiOrigin = "";

  return {
    name: "serve-headers",
    apply: "build",
    configResolved(config) {
      const { VITE_BACKEND_URL } = loadEnv(config.mode, config.envDir || config.root, "VITE_");
      if (!VITE_BACKEND_URL) {
        // Fail the build rather than ship a CSP that blocks every API call.
        throw new Error("VITE_BACKEND_URL must be set to build the production headers (serve.json).");
      }
      apiOrigin = new URL(VITE_BACKEND_URL).origin;
    },
    generateBundle() {
      this.emitFile({
        type: "asset",
        fileName: "serve.json",
        source: `${JSON.stringify(buildServeConfig(apiOrigin), null, 2)}\n`,
      });
    },
  };
}
