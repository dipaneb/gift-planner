<template>
  <div class="h-screen relative">
    <AuroraBackground
      :color-stops="['#f4fff8', '#ccffe0', '#f4fff8']"
      :color-stops-dark="['#0a1f12', '#0d3d1f', '#0a1f12']"
      :blend="0.18"
      :amplitude="0.5"
      :speed="0.5"
      height="8rem"
      class="absolute top-0 left-0 right-0 -z-10"
    />
    <div class="flex flex-col items-center justify-center gap-10 relative h-full">
      <div class="absolute top-4 right-4">
        <LanguageSelector />
      </div>
      <h1>{{ t("verifyEmail.title") }}</h1>
      <UCard class="min-w-100">
        <div class="flex flex-col items-center gap-4">
          <template v-if="status === 'loading'">
            <UIcon name="i-lucide-loader-circle" class="size-10 animate-spin text-primary" />
            <p class="text-sm text-muted">{{ t("verifyEmail.verifying") }}</p>
          </template>

          <template v-else-if="status === 'success'">
            <UAlert
              color="success"
              variant="subtle"
              icon="i-lucide-circle-check"
              :title="t('verifyEmail.successTitle')"
              :description="t('verifyEmail.successDescription')"
              class="w-full"
            />
            <UButton :to="{ name: 'login' }" color="primary" block>
              {{ t("verifyEmail.goToSignIn") }}
            </UButton>
          </template>

          <template v-else>
            <UAlert
              color="error"
              variant="subtle"
              icon="i-lucide-circle-alert"
              :title="t('verifyEmail.failedTitle')"
              :description="errorMessage"
              class="w-full"
            />
            <UButton :to="{ name: 'login' }" color="primary" variant="outline" block>
              {{ t("verifyEmail.backToSignIn") }}
            </UButton>
          </template>
        </div>
      </UCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { useI18n } from "vue-i18n";

import { useAuth } from "@/composables/useAuth";
import LanguageSelector from "@/components/LanguageSelector.vue";
import AuroraBackground from "@/components/AuroraBackground.vue";

const route = useRoute();
const { t, locale } = useI18n();
const { verifyEmail, error } = useAuth();

const rawToken = route.query.token;
const token = Array.isArray(rawToken) ? rawToken[0] : rawToken;

type Status = "loading" | "success" | "error";
const status = ref<Status>("loading");
const errorMessage = ref("");

onMounted(async () => {
  // Handle locale parameter from URL (from email link)
  const urlLocale = route.query.locale as string;
  if (urlLocale && ["en", "fr"].includes(urlLocale) && locale.value !== urlLocale) {
    locale.value = urlLocale;
    localStorage.setItem("locale", urlLocale);
  }

  if (typeof token !== "string" || !token) {
    errorMessage.value = t("verifyEmail.tokenMissing");
    status.value = "error";
    return;
  }

  const response = await verifyEmail(token);

  if (response.success) {
    status.value = "success";
  } else {
    errorMessage.value = error.value ?? t("verifyEmail.failedFallback");
    status.value = "error";
  }
});
</script>
