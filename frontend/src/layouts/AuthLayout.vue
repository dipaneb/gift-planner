<template>
  <div class="flex min-h-screen flex-col">
    <UHeader >
      <template #left>
        <RouterLink :to="{name: 'recipients'}" class="font-decorative text-2xl">
          {{ t('common.appName') }}
        </RouterLink>
      </template>

      <UNavigationMenu :items="navItems" variant="link" />

      <template #right>
        <USelect 
          v-model="currentLocale" 
          :items="localeOptions" 
          @update:model-value="changeLocale"
          size="sm"
        />

        <UDropdownMenu :items="userMenuItems">
          <UButton icon="i-lucide-circle-user" color="neutral" variant="ghost" />
        </UDropdownMenu>
      </template>
    </UHeader>

    <main class="mx-auto w-full flex-1 px-4 md:px-6 lg:px-10 py-8">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import type { DropdownMenuItem, NavigationMenuItem } from "@nuxt/ui";

import { useAuthStore } from "@/stores/auth";
import { useAuth } from "@/composables/useAuth";

const { t, locale } = useI18n();
const authStore = useAuthStore();
const { logout } = useAuth();

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

const navItems = computed<NavigationMenuItem[]>(() => [
  {
    label: t('nav.recipients'),
    icon: "i-lucide-person-standing",
    to: { name: "recipients" },
  },
  {
    label: t('nav.gifts'),
    icon: "i-lucide-gift",
    to: { name: "gifts" },
  },
  {
    label: t('nav.budget'),
    icon: "i-lucide-wallet",
    to: { name: "budget" },
  },
]);

const userMenuItems = computed<DropdownMenuItem[][]>(() => [
  [
    {
      label: authStore.user?.email ?? "",
      type: "label",
    },
  ],
  [
    {
      label: t('nav.settings'),
      icon: "i-lucide-settings",
      to: { name: "settings" },
    },
  ],
  [
    {
      label: t('nav.logout'),
      icon: "i-lucide-log-out",
      color: "error",
      onSelect: () => logout(),
    },
  ],
]);
</script>
