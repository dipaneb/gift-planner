<template>
  <div class="flex h-screen">
    <div class="flex-1" />
    <div class="flex flex-1 flex-col items-center justify-center gap-10">
      <h1>Email verification.</h1>
      <UCard class="min-w-100">
        <div class="flex flex-col items-center gap-4">
          <template v-if="status === 'loading'">
            <UIcon name="i-lucide-loader-circle" class="size-10 animate-spin text-primary" />
            <p class="text-sm text-muted">Verifying your email...</p>
          </template>

          <template v-else-if="status === 'success'">
            <UAlert
              color="success"
              variant="subtle"
              icon="i-lucide-circle-check"
              title="Email verified!"
              :description="message"
              class="w-full"
            />
            <UButton :to="{ name: 'login' }" color="primary" block>
              Go to sign in
            </UButton>
          </template>

          <template v-else>
            <UAlert
              color="error"
              variant="subtle"
              icon="i-lucide-circle-alert"
              title="Verification failed"
              :description="errorMessage"
              class="w-full"
            />
            <UButton :to="{ name: 'login' }" color="primary" variant="outline" block>
              Back to sign in
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

import { useAuth } from "@/composables/useAuth";

const route = useRoute();
const { verifyEmail, error } = useAuth();

const rawToken = route.query.token;
const token = Array.isArray(rawToken) ? rawToken[0] : rawToken;

type Status = "loading" | "success" | "error";
const status = ref<Status>("loading");
const message = ref("");
const errorMessage = ref("");

onMounted(async () => {
  if (typeof token !== "string" || !token) {
    errorMessage.value = "Verification token is missing.";
    status.value = "error";
    return;
  }

  const response = await verifyEmail(token);

  if (response.success) {
    message.value = response.message ?? "Your email has been verified.";
    status.value = "success";
  } else {
    errorMessage.value = error.value ?? "The verification link may be invalid or expired.";
    status.value = "error";
  }
});
</script>
