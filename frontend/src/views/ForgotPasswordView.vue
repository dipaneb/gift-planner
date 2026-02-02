<template>
  <h1>Forgot Password</h1>

  <form @submit.prevent="onSubmit" novalidate>
    <label for="email">Email</label>
    <input v-model="email" type="email" id="email" inputmode="email" :disabled="loading" />
    <p>{{ error }}</p>

    <button type="submit" :disabled="loading">{{ loading ? "Submitting..." : "Submit" }}</button>
  </form>

  <p v-if="emailSent">If this email address exists, an email has been sent.</p>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import * as z from "zod";
import { useAuth } from "@/composables/useAuth";

const { forgotPassword, loading, error } = useAuth();

const email = ref("");
const emailSent = ref(false);
watch(email, () => (emailSent.value = false));

const forgotPasswordSchema = z.object({
  email: z.email(),
});

const onSubmit = async (): Promise<void> => {
  const result = forgotPasswordSchema.safeParse({ email: email.value });
  if (!result.success) {
    console.log("Error from zod is: ", result.error);
    return;
  }
  try {
    await forgotPassword({ email: email.value });
    emailSent.value = true;
  } catch (e) {
    console.log("error from backend: ", e);
  }
};
</script>
