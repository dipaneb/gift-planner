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
      <h1>{{ t("auth.registerPage.title") }}</h1>
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
          <UFormField :label="t('auth.name')" name="name">
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

          <UFormField :label="t('auth.email')" name="email" required>
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

          <UFormField :label="t('auth.password')" required>
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
                <UButton
                  :icon="isPasswordVisible ? 'i-lucide-eye' : 'i-lucide-eye-closed'"
                  variant="ghost"
                  color="neutral"
                  size="sm"
                  :aria-label="isPasswordVisible ? t('auth.hidePassword') : t('auth.showPassword')"
                  @click="isPasswordVisible = !isPasswordVisible"
                />
              </template>
            </UInput>
          </UFormField>

          <PasswordStrength :password="state.password" />

          <UFormField :label="t('auth.confirmPassword')" name="confirmed_password" required>
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
                <UButton
                  :icon="isPasswordVisible ? 'i-lucide-eye' : 'i-lucide-eye-closed'"
                  variant="ghost"
                  color="neutral"
                  size="sm"
                  :aria-label="isPasswordVisible ? t('auth.hidePassword') : t('auth.showPassword')"
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
            {{ loading ? t("common.submitting") : t("auth.registerPage.submit") }}
          </UButton>
        </UForm>

        <template #footer>
          <p class="text-center text-sm text-muted">
            {{ t("auth.registerPage.hasAccount") }}
            <RouterLink :to="{ name: 'login' }" class="font-medium text-primary">
              {{ t("auth.registerPage.signInLink")
              }}<UIcon class="inline align-middle" name="i-lucide-move-up-right" />
            </RouterLink>
          </p>
        </template>
      </UCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { useI18n } from "vue-i18n";
import * as z from "zod";
import type { FormSubmitEvent } from "@nuxt/ui";

import { useAuth } from "@/composables/useAuth";
import LanguageSelector from "@/components/LanguageSelector.vue";
import PasswordStrength from "@/components/PasswordStrengthIndicator.vue";
import AuroraBackground from "@/components/AuroraBackground.vue";

const { t } = useI18n();
const { register, loading, error } = useAuth();

const isPasswordVisible = ref(false);
const successMessage = ref("");

const registerSchema = computed(() =>
  z
    .object({
      name: z.string().max(255),
      email: z.email(),
      password: z
        .string()
        .min(8, t("auth.validation.passwordMin"))
        .max(255)
        .regex(/[A-Z]/, t("auth.validation.passwordUppercase"))
        .regex(/[a-z]/, t("auth.validation.passwordLowercase"))
        .regex(/\d/, t("auth.validation.passwordDigit"))
        .regex(/[^A-Za-z0-9\s]/, t("auth.validation.passwordSpecial")),
      confirmed_password: z.string().min(1, t("auth.validation.confirmPasswordRequired")),
    })
    .refine((data) => data.password === data.confirmed_password, {
      message: t("auth.validation.passwordsMismatch"),
      path: ["confirmed_password"],
    }),
);

type Schema = z.infer<typeof registerSchema.value>;

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

  if (response.success) {
    successMessage.value = t("auth.registerPage.successMessage");
  }
};
</script>
