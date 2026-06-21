<template>
  <USelect
    v-model="currentLocale"
    :items="localeOptions"
    @update:model-value="changeLocale"
    size="sm"
    class="w-fit"
  />
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { useI18n } from "vue-i18n";

const { locale } = useI18n();

const currentLocale = ref(locale.value);

const localeOptions = [
  { label: "English", value: "en" },
  { label: "Français", value: "fr" },
];

function changeLocale(newLocale: string) {
  locale.value = newLocale;
  currentLocale.value = newLocale;
  localStorage.setItem("locale", newLocale);
}

watch(locale, (newLocale) => {
  currentLocale.value = newLocale;
});
</script>
