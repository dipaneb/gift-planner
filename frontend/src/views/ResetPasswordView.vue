<template>
  <h1>Reset Password</h1>

  <form @submit.prevent="onSubmit" novalidate>
    <label for="password">New password</label>
    <input
      v-model="password"
      type="password"
      id="password"
      autocomplete="new-password"
      :disabled="loading"
    />

    <label for="confirmedPassword">Confirmed password</label>
    <input
      v-model="confirmedPassword"
      type="password"
      id="confirmedPassword"
      autocomplete="new-password"
      :disabled="loading"
    />

    <p>{{ error }}</p>

    <button type="submit" :disabled="loading">{{ loading ? "Submitting..." : "Submit" }}</button>
  </form>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRoute } from "vue-router";
import * as z from "zod";

import { useAuth } from "@/composables/useAuth";

const { resetPassword, loading, error } = useAuth();
const route = useRoute();

const rawResetPasswordToken = route.query.token;
const resetPasswordToken = Array.isArray(rawResetPasswordToken)
  ? rawResetPasswordToken[0]
  : rawResetPasswordToken;
const password = ref("");
const confirmedPassword = ref("");

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
    confirmed_password: z.string().min(8, "Password must be at least 8 characters.").max(255),
  })
  .refine((data) => data.password === data.confirmed_password, {
    message: "Passwords don't match.",
    path: ["confirm"],
  });

const onSubmit = async (): Promise<void> => {
  const result = resetPasswordSchema.safeParse({
    password: password.value,
    confirmed_password: confirmedPassword.value,
  });
  if (!result.success) {
    console.log("Error from zod is: ", result.error);
    return;
  }

  if (typeof resetPasswordToken !== "string") {
    console.error(
      "Error from query parameter(s): One and exactly one query parameter should be included",
    );
    return;
  }
  try {
    await resetPassword(resetPasswordToken, {
      password: password.value,
      confirmed_password: confirmedPassword.value,
    });
  } catch (e) {
    console.log("error from backend: ", e);
  }
};
</script>
