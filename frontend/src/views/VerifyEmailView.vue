<template>
  <div class="flex h-screen">
    <div class="flex-1" />
    <div class="flex flex-1 flex-col items-center justify-center gap-10">
      <h1>{{ t('verifyEmail.title') }}</h1>
      <UCard class="min-w-100">
        <div class="flex flex-col items-center gap-4">
          <template v-if="status === 'loading'">
            <UIcon name="i-lucide-loader-circle" class="size-10 animate-spin text-primary" />
            <p class="text-sm text-muted">{{ t('verifyEmail.verifying') }}</p>
          </template>

          <template v-else-if="status === 'success'">
            <UAlert
              color="success"
              variant="subtle"
              icon="i-lucide-circle-check"
              :title="t('verifyEmail.successTitle')"
              :description="message"
              class="w-full"
            />
            <UButton :to="{ name: 'login' }" color="primary" block>
              {{ t('verifyEmail.goToSignIn') }}
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
              {{ t('verifyEmail.backToSignIn') }}
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

const route = useRoute();
const { t } = useI18n();
const { verifyEmail, error } = useAuth();

const rawToken = route.query.token;
const token = Array.isArray(rawToken) ? rawToken[0] : rawToken;

type Status = "loading" | "success" | "error";
const status = ref<Status>("loading");
const message = ref("");
const errorMessage = ref("");

onMounted(async () => {
  if (typeof token !== "string" || !token) {
    errorMessage.value = t('verifyEmail.tokenMissing');
    status.value = "error";
    return;
  }

  const response = await verifyEmail(token);

  if (response.success) {
    message.value = response.message ?? t('verifyEmail.successFallback');
    status.value = "success";
  } else {
    errorMessage.value = error.value ?? t('verifyEmail.failedFallback');
    status.value = "error";
  }
});
</script>
