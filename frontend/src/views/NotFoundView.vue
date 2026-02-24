<template>
  <div class="flex min-h-screen items-center justify-center p-4">
    <UCard class="max-w-2xl w-full">
      <div class="flex flex-col items-center text-center gap-6 py-8">
        <div class="flex items-center justify-center w-32 h-32 rounded-full bg-gradient-to-br from-red-50 to-red-100 border border-red-200">
          <UIcon name="i-lucide-search-x" class="text-6xl text-red-600" />
        </div>

        <div class="flex flex-col gap-2">
          <h1 class="text-6xl font-bold text-gray-900">404</h1>
          <h2 class="text-2xl font-semibold text-gray-700">Page Not Found</h2>
        </div>

        <p class="text-gray-600 max-w-md">
          The page you're looking for doesn't exist or has been moved. Let's get you back on
          track.
        </p>

        <div class="flex flex-col sm:flex-row gap-3 w-full sm:w-auto mt-4">
          <UButton
            :to="{ name: 'recipients' }"
            color="primary"
            size="lg"
            icon="i-lucide-home"
            class="justify-center"
          >
            Go to Recipients
          </UButton>
          <UButton
            @click="goBack"
            color="neutral"
            variant="outline"
            size="lg"
            icon="i-lucide-arrow-left"
            class="justify-center"
          >
            Go Back
          </UButton>
        </div>

        <USeparator class="my-4" />

        <div class="flex flex-col gap-3 w-full">
          <p class="text-sm font-semibold text-gray-600 uppercase tracking-wide">
            Quick Links
          </p>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-2">
            <UButton
              :to="{ name: 'recipients' }"
              color="neutral"
              variant="soft"
              icon="i-lucide-person-standing"
              class="justify-start"
            >
              Recipients
            </UButton>
            <UButton
              :to="{ name: 'gifts' }"
              color="neutral"
              variant="soft"
              icon="i-lucide-gift"
              class="justify-start"
            >
              Gifts
            </UButton>
            <UButton
              :to="{ name: 'budget' }"
              color="neutral"
              variant="soft"
              icon="i-lucide-wallet"
              class="justify-start"
            >
              Budget
            </UButton>
          </div>
        </div>
      </div>
    </UCard>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";

const router = useRouter();

const goBack = () => {
  if (window.history.length > 1) {
    router.back();
  } else {
    router.push({ name: "recipients" });
  }
};
</script>
