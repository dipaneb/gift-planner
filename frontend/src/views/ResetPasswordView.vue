<template>
  <div class="flex h-screen">
    <div class="flex-1" />
    <div class="flex flex-1 flex-col items-center justify-center gap-10">
      <h1>Reset your password.</h1>
      <UCard class="min-w-100">
        <UAlert
          v-if="!isValidToken"
          color="error"
          variant="subtle"
          icon="i-lucide-circle-alert"
          title="Invalid link"
          description="This password reset link is invalid or has expired. Please request a new one."
        />

        <UForm
          v-else
          :schema="resetPasswordSchema"
          :state="state"
          @submit="onSubmit"
          class="flex flex-col gap-6"
        >
          <UFormField label="New password" name="password" required>
            <UInput
              v-model="state.password"
              :type="isPasswordVisible ? 'text' : 'password'"
              name="password"
              id="password"
              autocomplete="new-password"
              class="w-full"
              :disabled="loading"
            >
              <template #trailing>
                <UIcon
                  :name="isPasswordVisible ? 'i-lucide-eye' : 'i-lucide-eye-closed'"
                  class="cursor-pointer"
                  @click="isPasswordVisible = !isPasswordVisible"
                />
              </template>
            </UInput>
          </UFormField>

          <UFormField label="Confirm password" name="confirmed_password" required>
            <UInput
              v-model="state.confirmed_password"
              :type="isPasswordVisible ? 'text' : 'password'"
              name="confirmed_password"
              id="confirmed_password"
              autocomplete="new-password"
              class="w-full"
              :disabled="loading"
            >
              <template #trailing>
                <UIcon
                  :name="isPasswordVisible ? 'i-lucide-eye' : 'i-lucide-eye-closed'"
                  class="cursor-pointer"
                  @click="isPasswordVisible = !isPasswordVisible"
                />
              </template>
            </UInput>
          </UFormField>

          <UAlert
            v-if="error"
            color="error"
            variant="subtle"
            icon="i-lucide-circle-alert"
            :description="error"
          />

          <UButton type="submit" color="primary" block :loading="loading">
            {{ loading ? "Updating..." : "Reset password" }}
          </UButton>
        </UForm>

        <template #footer>
          <p class="text-center text-sm text-muted">
            <RouterLink :to="{ name: 'login' }" class="font-medium text-primary">
              Back to sign in<UIcon class="inline align-middle" name="i-lucide-move-up-right" />
            </RouterLink>
          </p>
        </template>
      </UCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { useRoute } from "vue-router";
import * as z from "zod";
import type { FormSubmitEvent } from "@nuxt/ui";

import { useAuth } from "@/composables/useAuth";

const { resetPassword, loading, error } = useAuth();
const route = useRoute();

const rawToken = route.query.token;
const resetPasswordToken = Array.isArray(rawToken) ? rawToken[0] : rawToken;
const isValidToken = typeof resetPasswordToken === "string" && resetPasswordToken.length > 0;

const isPasswordVisible = ref(false);

const resetPasswordSchema = z
  .object({
    password: z
      .string()
      .min(8, "Password must be at least 8 characters.")
      .max(255)
      .regex(/[A-Z]/, "Password must include an uppercase letter.")
      .regex(/[a-z]/, "Password must include a lowercase letter.")
      .regex(/\d/, "Password must include a digit.")
      .regex(/[^A-Za-z0-9\s]/, "Password must include a special character."),
    confirmed_password: z.string().min(1, "Please confirm your password."),
  })
  .refine((data) => data.password === data.confirmed_password, {
    message: "Passwords don't match.",
    path: ["confirmed_password"],
  });

type Schema = z.infer<typeof resetPasswordSchema>;

const state = reactive<Partial<Schema>>({
  password: "",
  confirmed_password: "",
});

const onSubmit = async (event: FormSubmitEvent<Schema>): Promise<void> => {
  await resetPassword(resetPasswordToken as string, {
    password: event.data.password,
    confirmed_password: event.data.confirmed_password,
  });
};
</script>
