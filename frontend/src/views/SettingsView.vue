<template>
  <div class="flex flex-col gap-6">
    <h1>{{ t("settings.title") }}</h1>

    <UCard>
      <template #header>
        <h2>{{ t("settings.profileInfo") }}</h2>
      </template>

      <div class="flex flex-col gap-4">
        <div class="py-3">
          <span>{{ t("settings.emailLabel") }}</span>
          <span>{{ authStore.user?.email }}</span>
        </div>
        <USeparator />
        <div v-if="!editingName">
          <div class="py-3">
            <span>{{ t("settings.nameLabel") }}</span>
            <span>{{ authStore.user?.name || t("common.notSet") }}</span>
          </div>
          <div class="flex gap-2">
            <UButton
              @click="editingName = true"
              color="neutral"
              variant="outline"
              class="self-start"
            >
              {{ t("settings.editName") }}
            </UButton>
            <UButton
              v-if="authStore.user?.name"
              @click="handleDeleteName"
              color="error"
              variant="soft"
              :loading="isDeletingName"
              class="self-start"
            >
              {{ t("settings.deleteName") }}
            </UButton>
          </div>
        </div>

        <UForm
          v-else
          :schema="nameSchema"
          :state="nameForm"
          @submit="handleUpdateName"
          class="flex flex-col gap-4"
        >
          <UAlert v-if="nameError" :title="nameError" color="error" variant="subtle" />

          <UFormField :label="t('auth.name')" name="name" required>
            <UInput
              v-model="nameForm.name"
              :placeholder="t('settings.namePlaceholder')"
              class="w-full"
            />
          </UFormField>

          <div class="flex gap-2">
            <UButton
              type="button"
              @click="cancelEditName"
              color="neutral"
              variant="outline"
              :disabled="isUpdatingName"
            >
              {{ t("common.cancel") }}
            </UButton>
            <UButton type="submit" color="primary" :loading="isUpdatingName">
              {{ t("common.save") }}
            </UButton>
          </div>
        </UForm>
      </div>
    </UCard>

    <UCard>
      <template #header>
        <h2>{{ t("settings.changePassword") }}</h2>
      </template>

      <UForm
        :schema="passwordSchema"
        :state="passwordForm"
        @submit="handleUpdatePassword"
        class="flex flex-col gap-4"
      >
        <UAlert v-if="passwordError" :title="passwordError" color="error" variant="subtle" />
        <UAlert v-if="passwordSuccess" :title="passwordSuccess" color="success" variant="subtle" />

        <UFormField :label="t('settings.currentPassword')" name="current_password" required>
          <UInput
            v-model="passwordForm.current_password"
            type="password"
            :placeholder="t('settings.currentPasswordPlaceholder')"
            class="w-full"
          />
        </UFormField>

        <UFormField :label="t('settings.newPasswordLabel')" required>
          <UInput
            v-model="passwordForm.new_password"
            type="password"
            :placeholder="t('settings.newPasswordPlaceholder')"
            class="w-full"
          />
        </UFormField>

        <div v-if="passwordForm.new_password" :style="{ '--pw-color': newPasswordColorValue }">
          <UProgress
            :model-value="newPasswordScore"
            :max="5"
            :indicator="newPasswordText"
            size="sm"
            :ui="{ indicator: 'bg-[var(--pw-color)] transition-[background-color] duration-300' }"
          />
          <p class="text-xs pb-0.5 pt-2">
            {{ newPasswordText }}. {{ t("auth.passwordStrength.mustContain") }}
          </p>
          <ul class="space-y-1">
            <li
              v-for="(req, index) in newPasswordRequirements"
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

        <UFormField :label="t('settings.confirmNewPassword')" name="confirmed_password" required>
          <UInput
            v-model="passwordForm.confirmed_password"
            type="password"
            :placeholder="t('settings.confirmNewPasswordPlaceholder')"
            class="w-full"
          />
        </UFormField>

        <UButton type="submit" color="primary" :loading="isUpdatingPassword" class="self-start">
          {{ t("settings.updatePassword") }}
        </UButton>
      </UForm>
    </UCard>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, reactive } from "vue";
import { useI18n } from "vue-i18n";
import { z } from "zod";
import type { FormSubmitEvent } from "@nuxt/ui";
import { useAuthStore } from "@/stores/auth";
import { usersApi } from "@/api/users";
import { getErrorMessage } from "@/composables/utils";

const { t } = useI18n();
const authStore = useAuthStore();

const nameSchema = computed(() =>
  z.object({
    name: z
      .string()
      .trim()
      .min(1, t("validation.nameRequired"))
      .max(255, t("validation.nameTooLong")),
  }),
);

const passwordSchema = computed(() =>
  z
    .object({
      current_password: z.string().min(1, t("auth.validation.confirmPasswordRequired")),
      new_password: z.string().min(8, t("auth.validation.passwordMin")),
      confirmed_password: z.string().min(8, t("auth.validation.passwordMin")),
    })
    .refine((data) => data.new_password === data.confirmed_password, {
      message: t("auth.validation.passwordsMismatch"),
      path: ["confirmed_password"],
    }),
);

type NameSchema = z.output<typeof nameSchema.value>;
type PasswordSchema = z.output<typeof passwordSchema.value>;

const editingName = ref(false);
const isUpdatingName = ref(false);
const isDeletingName = ref(false);
const isUpdatingPassword = ref(false);
const nameError = ref("");
const passwordError = ref("");
const passwordSuccess = ref("");

const nameForm = reactive<Partial<NameSchema>>({
  name: authStore.user?.name || "",
});

const passwordForm = reactive<Partial<PasswordSchema>>({
  current_password: "",
  new_password: "",
  confirmed_password: "",
});

const newPasswordRequirements = computed(() => {
  const password = passwordForm.new_password || "";
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

const newPasswordScore = computed(() => {
  return newPasswordRequirements.value.filter((req) => req.met).length;
});

const newPasswordColorValue = computed(() => {
  const score = newPasswordScore.value;
  if (score === 0) return "oklch(55% 0 0)";
  if (score === 1) return "oklch(55% 0.2 25)";
  if (score === 2) return "oklch(65% 0.18 50)";
  if (score === 3) return "oklch(75% 0.15 85)";
  if (score === 4) return "oklch(75% 0.16 110)";
  return "oklch(75% 0.19 145)";
});

const newPasswordText = computed(() => {
  const score = newPasswordScore.value;
  if (score === 0) return t("auth.passwordStrength.enterPassword");
  if (score <= 2) return t("auth.passwordStrength.weakPassword");
  if (score <= 3) return t("auth.passwordStrength.mediumPassword");
  return t("auth.passwordStrength.strongPassword");
});

const cancelEditName = () => {
  editingName.value = false;
  nameForm.name = authStore.user?.name || "";
  nameError.value = "";
};

const handleDeleteName = async () => {
  nameError.value = "";
  isDeletingName.value = true;

  try {
    const updatedUser = await usersApi.deleteName();
    authStore.user = updatedUser;
  } catch (error) {
    nameError.value = getErrorMessage(error, t("settings.deleteNameFailed"));
  } finally {
    isDeletingName.value = false;
  }
};

const handleUpdateName = async (event: FormSubmitEvent<NameSchema>) => {
  nameError.value = "";
  isUpdatingName.value = true;

  try {
    const updatedUser = await usersApi.updateName({
      name: event.data.name,
    });
    authStore.user = updatedUser;
    editingName.value = false;
  } catch (error) {
    nameError.value = getErrorMessage(error, t("settings.updateNameFailed"));
  } finally {
    isUpdatingName.value = false;
  }
};

const handleUpdatePassword = async (event: FormSubmitEvent<PasswordSchema>) => {
  passwordError.value = "";
  passwordSuccess.value = "";
  isUpdatingPassword.value = true;

  try {
    await usersApi.updatePassword({
      current_password: event.data.current_password,
      new_password: event.data.new_password,
      confirmed_password: event.data.confirmed_password,
    });
    passwordSuccess.value = t("settings.passwordUpdated");
    passwordForm.current_password = "";
    passwordForm.new_password = "";
    passwordForm.confirmed_password = "";
  } catch (error) {
    passwordError.value = getErrorMessage(error, t("settings.updatePasswordFailed"), {
      400: t("settings.incorrectCurrentPassword"),
    });
  } finally {
    isUpdatingPassword.value = false;
  }
};
</script>
