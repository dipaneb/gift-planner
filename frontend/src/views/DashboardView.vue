<template>
  <div class="dashboard">
    <h1>Dashboard</h1>
    <div class="dashboard-content">
      <p>
        Welcome back<strong>{{
          authStore.user?.name === null ? "" : `, ${authStore.user?.name}`
        }}</strong
        >!
      </p>
      <p>This is a protected route that requires authentication.</p>

      <div class="info-card">
        <h2>Your Account</h2>
        <p><strong>Email:</strong> {{ authStore.user?.email }}</p>
        <p><strong>User ID:</strong> {{ authStore.user?.id }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from "@/stores/auth";

const authStore = useAuthStore();
</script>

<style scoped>
.dashboard {
  padding: 1rem;
}

h1 {
  color: #2c3e50;
  margin-bottom: 1.5rem;
}

.dashboard-content {
  max-width: 800px;
}

.dashboard-content p {
  font-size: 1.1rem;
  color: #555;
  margin-bottom: 1rem;
}

.info-card {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1.5rem;
  margin-top: 2rem;
}

.info-card h2 {
  color: #2c3e50;
  font-size: 1.3rem;
  margin-bottom: 1rem;
}

.info-card p {
  margin: 0.5rem 0;
  font-size: 1rem;
}
</style>
