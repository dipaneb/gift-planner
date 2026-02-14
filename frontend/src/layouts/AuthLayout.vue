<template>
  <div class="auth-layout">
    <nav class="navbar">
      <div class="nav-container">
        <div class="nav-brand">
          <RouterLink :to="{ name: 'dashboard' }">Gift Planner</RouterLink>
        </div>

        <div class="nav-links">
          <RouterLink :to="{ name: 'dashboard' }">Dashboard</RouterLink>
          <RouterLink :to="{ name: 'settings' }">Settings</RouterLink>
          <RouterLink :to="{ name: 'recipients' }">Recipients</RouterLink>
          <RouterLink :to="{ name: 'gifts' }">Gifts</RouterLink>
          <RouterLink :to="{ name: 'budget' }">Budget</RouterLink>
        </div>

        <div class="nav-actions">
          <span v-if="authStore.user">{{ authStore.user.email }}</span>
          <button @click="handleLogout">Logout</button>
        </div>
      </div>
    </nav>

    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from "@/stores/auth";
import { useAuth } from "@/composables/useAuth";

const authStore = useAuthStore();
const { logout } = useAuth();

async function handleLogout() {
  await logout();
}
</script>

<style scoped>
.auth-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  background: #2c3e50;
  color: white;
  padding: 1rem 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
}

.nav-brand a {
  font-size: 1.5rem;
  font-weight: bold;
  color: white;
  text-decoration: none;
}

.nav-links {
  display: flex;
  gap: 1.5rem;
  flex: 1;
}

.nav-links a {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: all 0.2s;
}

.nav-links a:hover,
.nav-links a.router-link-exact-active {
  color: white;
  background: rgba(255, 255, 255, 0.1);
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.nav-actions span {
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.9rem;
}

.nav-actions button {
  padding: 0.5rem 1rem;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.2s;
}

.nav-actions button:hover {
  background: #c0392b;
}

.main-content {
  flex: 1;
  padding: 2rem;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
}
</style>
