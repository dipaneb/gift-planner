<template>
  <h1>Login</h1>
  <form method="post" @submit.prevent="onSubmit" novalidate>
    <label for="email">Email</label>
    <input
      v-model="email"
      type="email"
      name="email"
      id="email"
      inputmode="email"
      required
      :disabled="loading"
    />

    <label for="password">Password</label>
    <input
      v-model="password"
      type="password"
      name="password"
      id="password"
      autocomplete="current-password"
      required
      :disabled="loading"
    />
    <button type="button">Toggle visibility</button>

    <button type="submit" :disabled="loading">{{ loading ? "Submitting..." : "Submit" }}</button>
  </form>

  <RouterLink :to="{ name: 'register' }">Register</RouterLink>
  <RouterLink :to="{ name: 'forgotPassword' }">Forgot password</RouterLink>

  <p v-if="error">Error is {{ error }}</p>
</template>

<script setup lang="ts">
import { ref } from "vue";
import * as z from "zod";

import { useAuth } from "@/composables/useAuth";

const { login, loading, error } = useAuth();

const email = ref("");
const password = ref("");

const loginSchema = z.object({
  email: z.email(),
  password: z
    .string()
    .min(8, "Password must be at least 8 characters.")
    .max(255)
    .regex(/[A-Z]/, "Password must include an uppercase letter.")
    .regex(/[a-z]/, "Password must include a lowercase letter.")
    .regex(/\d/, "Password must include a digit.")
    .regex(/[^A-Za-z0-9\s]/, "Password must include a special character."),
});

const onSubmit = async (): Promise<void> => {
  const result = loginSchema.safeParse({ email: email.value, password: password.value });
  if (!result.success) {
    console.error("Error from zod for login is: ", result.error);
    return;
  }
  try {
    await login({ email: email.value, password: password.value });
  } catch (err) {
    console.error("Error from backend for login is: ", err);
  }
};
</script>
