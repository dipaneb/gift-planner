<template>
  <UApp :toaster="toaster" :locale="uiLocale">
    <RouterView />
  </UApp>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { RouterView } from "vue-router";
import { useI18n } from "vue-i18n";
import { useHead } from "@unhead/vue";
import * as locales from "@nuxt/ui/locale";

const { locale } = useI18n();

// Map vue-i18n locale codes to Nuxt UI component locales
const localeMap: Record<string, typeof locales.en> = {
  en: locales.en,
  fr: locales.fr,
};

const uiLocale = computed(() => localeMap[locale.value] || locales.en);

useHead({
  htmlAttrs: {
    lang: computed(() => (localeMap[locale.value] || locales.fr).code),
    dir: computed(() => (localeMap[locale.value] || locales.fr).dir),
  },
});

const toaster = { position: "top-center" as const };
</script>
