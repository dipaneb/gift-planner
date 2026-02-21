<template>
  <div class="flex h-screen">
    <div class="flex-1" />
    <div class="flex flex-1 flex-col items-center justify-center gap-10">
      <h1>Forgot password.</h1>
      <UCard class="min-w-100">
        <UForm
          :schema="forgotPasswordSchema"
          :state="state"
          @submit="onSubmit"
          class="flex flex-col gap-6"
        >
          <UFormField label="Email" name="email" required>
            <UInput
              v-model="state.email"
              type="email"
              name="email"
              id="email"
              inputmode="email"
              autocomplete="email"
              class="w-full"
              :disabled="loading"
            />
          </UFormField>

          <UAlert
            v-if="error"
            color="error"
            variant="subtle"
            icon="i-lucide-circle-alert"
            :description="error"
          />

          <UButton
            type="submit"
            color="primary"
            block
            :loading="loading"
            :disabled="cooldown > 0"
          >
            {{ loading ? "Sending..." : cooldown > 0 ? `Retry in ${cooldown}s` : "Send reset link" }}
          </UButton>
        </UForm>

        <template #footer>
          <p class="text-center text-sm text-muted">
            Remember your password?
            <RouterLink :to="{ name: 'login' }" class="font-medium text-primary">
              Sign in<UIcon class="inline align-middle" name="i-lucide-move-up-right" />
            </RouterLink>
          </p>
        </template>
      </UCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onUnmounted, reactive, ref } from "vue";
import * as z from "zod";
import type { FormSubmitEvent } from "@nuxt/ui";

import { useAuth } from "@/composables/useAuth";

const { forgotPassword, loading, error } = useAuth();
const toast = useToast();

const COOLDOWN_SECONDS = 60;
const cooldown = ref(0);
let cooldownInterval: ReturnType<typeof setInterval> | null = null;

const forgotPasswordSchema = z.object({
  email: z.email(),
});

type Schema = z.infer<typeof forgotPasswordSchema>;

const state = reactive<Partial<Schema>>({
  email: "",
});

function startCooldown(): void {
  const endTime = Date.now() + COOLDOWN_SECONDS * 1000;
  cooldown.value = COOLDOWN_SECONDS;
  cooldownInterval = setInterval(() => {
    cooldown.value = Math.max(0, Math.ceil((endTime - Date.now()) / 1000));
    if (cooldown.value <= 0) {
      clearInterval(cooldownInterval!);
      cooldownInterval = null;
    }
  }, 250);
}

onUnmounted(() => {
  if (cooldownInterval) clearInterval(cooldownInterval);
});

const onSubmit = async (event: FormSubmitEvent<Schema>): Promise<void> => {
  const success = await forgotPassword({ email: event.data.email });
  if (success) {
    toast.add({
      title: "Email sent",
      description: "If this address is registered, a reset link has been sent.",
      color: "success",
      icon: "i-lucide-circle-check",
    });
    startCooldown();
  }
};
</script>
