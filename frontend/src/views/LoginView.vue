<template>
  <div class="h-screen relative">
    <!-- <div class="flex h-screen"> -->
    <!-- <div class="flex-1" /> -->
    <AuroraBackground
      :color-stops="['#f4fff8', '#ccffe0', '#f4fff8']"
      :color-stops-dark="['#0a1f12', '#0d3d1f', '#0a1f12']"
      :blend="0.18"
      :amplitude="0.5"
      :speed="0.5"
      height="8rem"
      class="absolute top-0 left-0 right-0 -z-10"
    />
    <!-- <div class="flex flex-1 flex-col items-center justify-center gap-10 relative"> -->
    <div class="flex flex-col items-center justify-center gap-10 relative h-full">
      <div class="absolute top-4 right-4">
        <LanguageSelector />
      </div>
      <h1>{{ t("auth.loginPage.title") }}</h1>
      <UCard class="min-w-100">
        <UForm :schema="loginSchema" :state="state" @submit="onSubmit" class="flex flex-col gap-6">
          <UFormField :label="t('auth.email')" name="email" required>
            <UInput
              v-model="state.email"
              type="email"
              name="email"
              id="email"
              inputmode="email"
              class="w-full"
              :disabled="loading"
              :loading="loading"
            />
          </UFormField>

          <UFormField :label="t('auth.password')" name="password" required>
            <template #hint>
              <RouterLink :to="{ name: 'forgotPassword' }" class="text-sm">
                {{ t("auth.forgotPassword") }}
              </RouterLink>
            </template>
            <UInput
              v-model="state.password"
              :type="isPasswordVisible ? 'text' : 'password'"
              name="password"
              id="password"
              autocomplete="current-password"
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
                  @click="toggleVisibility"
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
            {{ loading ? t("common.submitting") : t("auth.loginPage.submit") }}
          </UButton>
        </UForm>

        <template #footer>
          <p class="text-center text-sm text-muted">
            {{ t("auth.loginPage.noAccount") }}
            <RouterLink :to="{ name: 'register' }" class="font-medium text-primary">
              {{ t("auth.loginPage.registerLink")
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
import { useRoute } from "vue-router";
import { useI18n } from "vue-i18n";
import * as z from "zod";
import type { FormSubmitEvent } from "@nuxt/ui";

import { useAuth } from "@/composables/useAuth";
import LanguageSelector from "@/components/LanguageSelector.vue";
import AuroraBackground from "@/components/AuroraBackground.vue";

const route = useRoute();
const { t } = useI18n();
const { login, loading, error } = useAuth();

const isPasswordVisible = ref(false);

const loginSchema = computed(() =>
  z.object({
    email: z.email(t("auth.validation.emailFormat")),
    password: z
      .string()
      .min(8, t("auth.validation.passwordMin"))
      .max(255)
      .regex(/[A-Z]/, t("auth.validation.passwordUppercase"))
      .regex(/[a-z]/, t("auth.validation.passwordLowercase"))
      .regex(/\d/, t("auth.validation.passwordDigit"))
      .regex(/[^A-Za-z0-9\s]/, t("auth.validation.passwordSpecial")),
  }),
);

type Schema = z.infer<typeof loginSchema.value>;

const state = reactive<Partial<Schema>>({
  email: "",
  password: "",
});

const onSubmit = async (event: FormSubmitEvent<Schema>): Promise<void> => {
  const redirect = route.query.redirect as string | undefined;
  await login({ email: event.data.email, password: event.data.password }, redirect);
};

const toggleVisibility = (): void => {
  isPasswordVisible.value = !isPasswordVisible.value;
};
</script>
