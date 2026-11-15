import "./assets/main.css";

import { createApp } from "vue";
import { createPinia } from "pinia";
import ui from "@nuxt/ui/vue-plugin";
import { createHead } from "@unhead/vue/client";
import { z } from "zod";

import App from "./App.vue";
import router from "./router";
import i18n from "./i18n";
import { trackVisit } from "./composables/useVisitTracking";

// Zod compiles validators with `new Function` when eval is allowed. Our Content-Security-Policy
// (nixpacks.toml) forbids eval, so Zod would only probe, fail and fall back, while the browser
// reports a CSP violation on every form page. Use the eval-free validators from the start.
z.config({ jitless: true });

const app = createApp(App);
const head = createHead();

app.use(createPinia()); // Pinia initialized before Router because
app.use(router); // global navigation guard needs the store.
app.use(i18n);
app.use(ui);
app.use(head);

app.mount("#app");

trackVisit();
