<template>
  <div class="flex flex-col gap-6">
    <h1>Settings</h1>

    <UCard>
      <template #header>
        <h2>Profile Information</h2>
      </template>

      <div class="flex flex-col gap-4">
        <div class="py-3 border-b">
          <span>Email: </span>
          <span>{{ authStore.user?.email }}</span>
        </div>
        <div v-if="!editingName">
          <div class="py-3">
            <span>Name: </span>
            <span>{{ authStore.user?.name || "Not set" }}</span>
          </div>
          <UButton @click="editingName = true" color="neutral" variant="outline" class="self-start">
            Edit Name
          </UButton>
        </div>

        <UForm
          v-else
          :schema="nameSchema"
          :state="nameForm"
          @submit="handleUpdateName"
          class="flex flex-col gap-4"
        >
          <UAlert v-if="nameError" :title="nameError" color="error" variant="subtle" />

          <UFormField label="Name" name="name" required>
            <UInput v-model="nameForm.name" placeholder="Enter your name" class="w-full" />
          </UFormField>

          <div class="flex gap-2">
            <UButton
              type="button"
              @click="cancelEditName"
              color="neutral"
              variant="outline"
              :disabled="isUpdatingName"
            >
              Cancel
            </UButton>
            <UButton type="submit" color="primary" :loading="isUpdatingName"> Save </UButton>
          </div>
        </UForm>
      </div>
    </UCard>

    <UCard>
      <template #header>
        <h2>Change Password</h2>
      </template>

      <UForm
        :schema="passwordSchema"
        :state="passwordForm"
        @submit="handleUpdatePassword"
        class="flex flex-col gap-4"
      >
        <UAlert v-if="passwordError" :title="passwordError" color="error" variant="subtle" />
        <UAlert v-if="passwordSuccess" :title="passwordSuccess" color="success" variant="subtle" />

        <UFormField label="Current Password" name="current_password" required>
          <UInput
            v-model="passwordForm.current_password"
            type="password"
            placeholder="Enter current password"
            class="w-full"
          />
        </UFormField>

        <UFormField label="New Password" name="new_password" required>
          <UInput
            v-model="passwordForm.new_password"
            type="password"
            placeholder="Enter new password (min 8 characters)"
            class="w-full"
          />
        </UFormField>

        <UFormField label="Confirm New Password" name="confirmed_password" required>
          <UInput
            v-model="passwordForm.confirmed_password"
            type="password"
            placeholder="Confirm new password"
            class="w-full"
          />
        </UFormField>

        <UButton type="submit" color="primary" :loading="isUpdatingPassword" class="self-start">
          Update Password
        </UButton>
      </UForm>
    </UCard>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from "vue";
import { z } from "zod";
import type { FormSubmitEvent } from "@nuxt/ui";
import { useAuthStore } from "@/stores/auth";
import { usersApi } from "@/api/users";

const authStore = useAuthStore();

const nameSchema = z.object({
  name: z.string().trim().min(1, "Name is required").max(255, "Name is too long"),
});

const passwordSchema = z
  .object({
    current_password: z.string().min(1, "Current password is required"),
    new_password: z.string().min(8, "New password must be at least 8 characters"),
    confirmed_password: z.string().min(8, "Confirmation password must be at least 8 characters"),
  })
  .refine((data) => data.new_password === data.confirmed_password, {
    message: "Passwords do not match",
    path: ["confirmed_password"],
  });

type NameSchema = z.output<typeof nameSchema>;
type PasswordSchema = z.output<typeof passwordSchema>;

const editingName = ref(false);
const isUpdatingName = ref(false);
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

const cancelEditName = () => {
  editingName.value = false;
  nameForm.name = authStore.user?.name || "";
  nameError.value = "";
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
    nameError.value = error instanceof Error ? error.message : "Failed to update name";
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
    passwordSuccess.value = "Password updated successfully";
    passwordForm.current_password = "";
    passwordForm.new_password = "";
    passwordForm.confirmed_password = "";
  } catch (error) {
    passwordError.value = error instanceof Error ? error.message : "Failed to update password";
  } finally {
    isUpdatingPassword.value = false;
  }
};
</script>
