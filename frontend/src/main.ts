import "./assets/main.css";

import { createApp } from "vue";
import { createPinia } from "pinia";
import ui from "@nuxt/ui/vue-plugin";
import { createHead } from "@unhead/vue/client";

import App from "./App.vue";
import router from "./router";
import i18n from "./i18n";

const app = createApp(App);
const head = createHead();

app.use(createPinia()); // Pinia initialized before Router because
app.use(router); // global navigation guard needs the store.
app.use(i18n);
app.use(ui);
app.use(head);

app.mount("#app");
