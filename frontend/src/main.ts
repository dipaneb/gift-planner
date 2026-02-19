import "./assets/main.css";

import { createApp } from "vue";
import { createPinia } from "pinia";
import ui from "@nuxt/ui/vue-plugin";

import App from "./App.vue";
import router from "./router";

const app = createApp(App);

app.use(createPinia()); // Pinia initialized before Router because
app.use(router); // global navigation guard needs the store.
app.use(ui);

app.mount("#app");
