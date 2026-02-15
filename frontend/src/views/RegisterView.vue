<template>
  <h1>Register</h1>

  <div v-if="successMessage" class="success-message">
    {{ successMessage }}
    <RouterLink :to="{ name: 'login' }">Go to Login</RouterLink>
  </div>

  <form v-else @submit.prevent="onSubmit" novalidate>
    <label for="name">Name</label>
    <input v-model="name" type="text" name="name" id="name" :disabled="loading" />

    <label for="email">Email</label>
    <input
      v-model="email"
      type="email"
      name="email"
      id="email"
      inputmode="email"
      :disabled="loading"
    />

    <label for="password">Password</label>
    <input
      v-model="password"
      type="password"
      name="password"
      id="password"
      autocomplete="new-password"
      :disabled="loading"
    />

    <label for="confirmed_password">Confirmed Password</label>
    <input
      v-model="confirmed_password"
      type="password"
      name="confirmed_password"
      id="confirmed_password"
      autocomplete="new-password"
      :disabled="loading"
    />

    <button type="button">Toggle visibility</button>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <button type="submit" :disabled="loading">
      {{ loading ? "Submitting..." : "Submit" }}
    </button>
  </form>

  <RouterLink v-if="!successMessage" :to="{ name: 'login' }">Login</RouterLink>
</template>

<script setup lang="ts">
import { ref } from "vue";
import * as z from "zod";
import { useAuth } from "@/composables/useAuth";

const { register, loading, error } = useAuth();

const name = ref("");
const email = ref("");
const password = ref("");
const confirmed_password = ref("");
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
    confirmed_password: z.string().min(8, "Password must be at least 8 characters.").max(255),
  })
  .refine((data) => data.password === data.confirmed_password, {
    message: "Passwords don't match.",
    path: ["confirm"],
  });

const onSubmit = async (): Promise<void> => {
  const result = registerSchema.safeParse({
    name: name.value,
    email: email.value,
    password: password.value,
    confirmed_password: confirmed_password.value,
  });

  if (!result.success) {
    console.error(result);
    return;
  }

  const response = await register({
    name: name.value,
    email: email.value,
    password: password.value,
    confirmed_password: confirmed_password.value,
  });

  if (response.success && response.message) {
    successMessage.value = response.message;
  }
};
</script>
