<template>
  <div class="verify-email-container">
    <h1>Email Verification</h1>

    <div v-if="loading" class="loading-message">
      <p>Verifying your email...</p>
    </div>

    <div v-else-if="success" class="success-message">
      <p>{{ message }}</p>
      <p>Your email has been verified successfully!</p>
      <RouterLink :to="{ name: 'login' }">Go to Login</RouterLink>
    </div>

    <div v-else class="error-message">
      <p>{{ error }}</p>
      <p>The verification link may be invalid or expired.</p>
      <RouterLink :to="{ name: 'login' }">Go to Login</RouterLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import { useAuth } from "@/composables/useAuth";

const route = useRoute();
const { verifyEmail, loading, error } = useAuth();

const success = ref(false);
const message = ref("");

onMounted(async () => {
  const token = route.query.token as string;

  if (!token) {
    error.value = "Verification token is missing";
    return;
  }

  const response = await verifyEmail(token);

  if (response.success && response.message) {
    success.value = true;
    message.value = response.message;
  }
});
</script>
