<template>
  <div class="flex h-screen">
    <div class="flex-1" />
    <div class="flex flex-1 flex-col items-center justify-center gap-10">
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
                <UIcon
                  :name="isPasswordVisible ? 'i-lucide-eye' : 'i-lucide-eye-closed'"
                  class="cursor-pointer"
                  @click="isPasswordVisible = !isPasswordVisible"
                />
              </template>
            </UInput>
          </UFormField>

          <div v-if="state.password" :style="{ '--pw-color': passwordColorValue }">
            <UProgress
              :model-value="passwordScore"
              :max="5"
              :indicator="passwordText"
              size="sm"
              :ui="{ indicator: 'bg-[var(--pw-color)] transition-[background-color] duration-300' }"
            />
            <p class="text-xs pb-0.5 pt-2">
              {{ passwordText }}. {{ t("auth.passwordStrength.mustContain") }}
            </p>
            <ul class="space-y-1">
              <li
                v-for="(req, index) in passwordRequirements"
                :key="index"
                class="flex items-center gap-0.5"
                :class="req.met ? 'text-success' : 'text-muted'"
              >
                <UIcon
                  :name="req.met ? 'i-lucide-circle-check' : 'i-lucide-circle-x'"
                  class="size-4 shrink-0"
                />
                <span class="text-xs">&nbsp;{{ req.text }}</span>
              </li>
            </ul>
          </div>

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

const passwordRequirements = computed(() => {
  const password = state.password || "";
  return [
    {
      regex: /.{8,}/,
      text: t("auth.passwordStrength.requirement8Chars"),
      met: /.{8,}/.test(password),
    },
    { regex: /\d/, text: t("auth.passwordStrength.requirement1Number"), met: /\d/.test(password) },
    {
      regex: /[a-z]/,
      text: t("auth.passwordStrength.requirement1Lowercase"),
      met: /[a-z]/.test(password),
    },
    {
      regex: /[A-Z]/,
      text: t("auth.passwordStrength.requirement1Uppercase"),
      met: /[A-Z]/.test(password),
    },
    {
      regex: /[^A-Za-z0-9\s]/,
      text: t("auth.passwordStrength.requirement1Special"),
      met: /[^A-Za-z0-9\s]/.test(password),
    },
  ];
});

const passwordScore = computed(() => {
  return passwordRequirements.value.filter((req) => req.met).length;
});

const passwordColorValue = computed(() => {
  const score = passwordScore.value;
  if (score === 0) return "oklch(55% 0 0)";
  if (score === 1) return "oklch(55% 0.2 25)";
  if (score === 2) return "oklch(65% 0.18 50)";
  if (score === 3) return "oklch(75% 0.15 85)";
  if (score === 4) return "oklch(75% 0.16 110)";
  return "oklch(75% 0.19 145)";
});

const passwordText = computed(() => {
  const score = passwordScore.value;
  if (score === 0) return t("auth.passwordStrength.enterPassword");
  if (score <= 2) return t("auth.passwordStrength.weakPassword");
  if (score <= 3) return t("auth.passwordStrength.mediumPassword");
  return t("auth.passwordStrength.strongPassword");
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
