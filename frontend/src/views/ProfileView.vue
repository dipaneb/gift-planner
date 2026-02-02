<template>
  <div class="profile">
    <h1>Profile</h1>
    <div class="profile-content">
      <div class="info-section">
        <h2>Personal Information</h2>
        <div class="info-row">
          <label>Name:</label>
          <span>{{ authStore.user?.name || "Not set" }}</span>
        </div>
        <div class="info-row">
          <label>Email:</label>
          <span>{{ authStore.user?.email }}</span>
        </div>
        <div class="info-row">
          <label>User ID:</label>
          <span>{{ authStore.user?.id }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from "@/stores/auth";

const authStore = useAuthStore();
</script>

<style scoped>
.profile {
  padding: 1rem;
}

h1 {
  color: #2c3e50;
  margin-bottom: 1.5rem;
}

.profile-content {
  max-width: 800px;
}

.info-section {
  background: #fff;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 2rem;
}

.info-section h2 {
  color: #2c3e50;
  font-size: 1.3rem;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #3498db;
}

.info-row {
  display: flex;
  padding: 1rem 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-row:last-child {
  border-bottom: none;
}

.info-row label {
  font-weight: 600;
  color: #555;
  width: 150px;
  flex-shrink: 0;
}

.info-row span {
  color: #333;
}
</style>
