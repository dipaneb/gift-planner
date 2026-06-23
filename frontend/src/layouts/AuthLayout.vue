<template>
  <div class="flex min-h-screen flex-col">
    <UHeader>
      <template #left>
        <RouterLink :to="{ name: 'recipients' }" class="font-decorative text-2xl">
          {{ t("common.appName") }}
        </RouterLink>
      </template>

      <UNavigationMenu :items="navItems" variant="link" class="hidden lg:flex" />

      <template #right>
        <LanguageSelector />

        <UDropdownMenu :items="userMenuItems">
          <UButton icon="i-lucide-circle-user" color="neutral" variant="ghost" />
        </UDropdownMenu>
      </template>

      <template #body>
        <UNavigationMenu :items="navItems" orientation="vertical" class="lg:hidden" />
      </template>
    </UHeader>

    <main class="mx-auto w-full flex-1 px-4 md:px-6 lg:px-10 py-8">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import type { DropdownMenuItem, NavigationMenuItem } from "@nuxt/ui";

import { useAuthStore } from "@/stores/auth";
import { useAuth } from "@/composables/useAuth";
import LanguageSelector from "@/components/LanguageSelector.vue";

const { t } = useI18n();
const authStore = useAuthStore();
const { logout } = useAuth();

const navItems = computed<NavigationMenuItem[]>(() => [
  {
    label: t("nav.recipients"),
    icon: "i-lucide-person-standing",
    to: { name: "recipients" },
  },
  {
    label: t("nav.gifts"),
    icon: "i-lucide-gift",
    to: { name: "gifts" },
  },
  {
    label: t("nav.budget"),
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
      label: t("nav.settings"),
      icon: "i-lucide-settings",
      to: { name: "settings" },
    },
  ],
  [
    {
      label: t("nav.logout"),
      icon: "i-lucide-log-out",
      color: "error",
      onSelect: () => logout(),
    },
  ],
]);
</script>
