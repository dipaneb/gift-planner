<template>
  <div class="flex min-h-screen flex-col">
    <UHeader >
      <template #left>
        <RouterLink :to="{name: 'recipients'}">
          Gift Planner
        </RouterLink>
      </template>

      <UNavigationMenu :items="navItems" variant="link" />

      <template #right>
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
import { computed } from "vue";
import type { DropdownMenuItem, NavigationMenuItem } from "@nuxt/ui";

import { useAuthStore } from "@/stores/auth";
import { useAuth } from "@/composables/useAuth";

const authStore = useAuthStore();
const { logout } = useAuth();

const navItems: NavigationMenuItem[] = [
  {
    label: "Recipients",
    icon: "i-lucide-person-standing",
    to: { name: "recipients" },
  },
  {
    label: "Gifts",
    icon: "i-lucide-gift",
    to: { name: "gifts" },
  },
  {
    label: "Budget",
    icon: "i-lucide-wallet",
    to: { name: "budget" },
  },
];

const userMenuItems = computed<DropdownMenuItem[][]>(() => [
  [
    {
      label: authStore.user?.email ?? "",
      type: "label",
    },
  ],
  [
    {
      label: "Settings",
      icon: "i-lucide-settings",
      to: { name: "settings" },
    },
  ],
  [
    {
      label: "Logout",
      icon: "i-lucide-log-out",
      color: "error",
      onSelect: () => logout(),
    },
  ],
]);
</script>
