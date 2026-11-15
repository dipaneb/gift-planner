import { fileURLToPath, URL } from "node:url";

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import vueDevTools from "vite-plugin-vue-devtools";
import ui from "@nuxt/ui/vite";

import { serveHeaders } from "./vite.serve-headers";

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
    ui({
      // Bundle the icons the app uses (found by scanning the source) instead of fetching them
      // at runtime from api.iconify.design: no third-party request, no blank icons if it is
      // slow, down or blocked (ad blocker, strict network).
      icon: {
        clientBundle: {
          scan: true,
        },
      },
      ui: {
        colors: {
          primary: "emerald",
          neutral: "zinc",
        },
      },
    }),
    serveHeaders(),
  ],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  css: {
    devSourcemap: true,
  },
});
