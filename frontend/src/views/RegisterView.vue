<template>
  <div class="flex h-screen">
    <div class="flex-1" />
    <div class="flex flex-1 flex-col items-center justify-center gap-10">
      <h1>Create your account.</h1>
      <UCard class="min-w-100">
        <div v-if="successMessage" class="flex flex-col gap-4">
          <UAlert
            color="success"
            variant="subtle"
            icon="i-lucide-circle-check"
            :description="successMessage"
          />
        </div>

        <UForm
          v-else
          :schema="registerSchema"
          :state="state"
          @submit="onSubmit"
          class="flex flex-col gap-6"
        >
          <UFormField label="Name" name="name">
            <UInput
              v-model="state.name"
              type="text"
              name="name"
              id="name"
              autocomplete="name"
              class="w-full"
              :disabled="loading"
            />
          </UFormField>

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

          <UFormField label="Password" name="password" required>
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
            {{ loading ? "Submitting..." : "Create account" }}
          </UButton>
        </UForm>

        <template #footer>
          <p class="text-center text-sm text-muted">
            Already have an account?
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
import { reactive, ref } from "vue";
import * as z from "zod";
import type { FormSubmitEvent } from "@nuxt/ui";

import { useAuth } from "@/composables/useAuth";

const { register, loading, error } = useAuth();

const isPasswordVisible = ref(false);
const successMessage = ref("");

const registerSchema = z
  .object({
    name: z.string().max(255),
    email: z.email(),
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

type Schema = z.infer<typeof registerSchema>;

const state = reactive<Partial<Schema>>({
  name: "",
  email: "",
  password: "",
  confirmed_password: "",
});

const onSubmit = async (event: FormSubmitEvent<Schema>): Promise<void> => {
  const response = await register({
    name: event.data.name,
    email: event.data.email,
    password: event.data.password,
    confirmed_password: event.data.confirmed_password,
  });

  if (response.success && response.message) {
    successMessage.value = response.message;
  }
};
</script>
