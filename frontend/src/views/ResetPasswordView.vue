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
      <h1>{{ t("auth.resetPassword.title") }}</h1>
      <UCard class="min-w-100">
        <UAlert
          v-if="!isValidToken"
          color="error"
          variant="subtle"
          icon="i-lucide-circle-alert"
          :title="t('auth.resetPassword.invalidLink')"
          :description="t('auth.resetPassword.invalidLinkDescription')"
        />

        <UForm
          v-else
          :schema="resetPasswordSchema"
          :state="state"
          @submit="onSubmit"
          class="flex flex-col gap-6"
        >
          <UFormField :label="t('auth.newPassword')" name="password" required>
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
            {{ loading ? t("common.updating") : t("auth.resetPassword.submit") }}
          </UButton>
        </UForm>

        <template #footer>
          <p class="text-center text-sm text-muted">
            <RouterLink :to="{ name: 'login' }" class="font-medium text-primary">
              {{ t("auth.resetPassword.backToSignIn")
              }}<UIcon class="inline align-middle" name="i-lucide-move-up-right" />
            </RouterLink>
          </p>
        </template>
      </UCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import { useI18n } from "vue-i18n";
import * as z from "zod";
import type { FormSubmitEvent } from "@nuxt/ui";

import { useAuth } from "@/composables/useAuth";
import LanguageSelector from "@/components/LanguageSelector.vue";
import PasswordStrength from "@/components/PasswordStrengthIndicator.vue";
import AuroraBackground from "@/components/AuroraBackground.vue";

const { t, locale } = useI18n();
const { resetPassword, loading, error } = useAuth();
const route = useRoute();

// Handle locale parameter from URL (from email link)
onMounted(() => {
  const urlLocale = route.query.locale as string;
  if (urlLocale && ["en", "fr"].includes(urlLocale) && locale.value !== urlLocale) {
    locale.value = urlLocale;
    localStorage.setItem("locale", urlLocale);
  }
});

const rawToken = route.query.token;
const resetPasswordToken = Array.isArray(rawToken) ? rawToken[0] : rawToken;
const isValidToken = typeof resetPasswordToken === "string" && resetPasswordToken.length > 0;

const isPasswordVisible = ref(false);

const resetPasswordSchema = computed(() =>
  z
    .object({
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

type Schema = z.infer<typeof resetPasswordSchema.value>;

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
