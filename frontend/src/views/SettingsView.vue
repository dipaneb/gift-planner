<template>
  <div class="settings">
    <h1>Settings</h1>
    <div class="settings-content">
      <div class="settings-section">
        <h2>Account Settings</h2>
        <p>Manage your account preferences and settings here.</p>
      </div>

      <div class="settings-section">
        <h2>Security</h2>
        <p>Update your password and security preferences.</p>
      </div>

      <div class="settings-section">
        <h2>Notifications</h2>
        <p>Configure your notification preferences.</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts"></script>

<style scoped>
.settings {
  padding: 1rem;
}

h1 {
  color: #2c3e50;
  margin-bottom: 1.5rem;
}

.settings-content {
  max-width: 800px;
}

.settings-section {
  background: #fff;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.settings-section h2 {
  color: #2c3e50;
  font-size: 1.2rem;
  margin-bottom: 0.75rem;
}

.settings-section p {
  color: #666;
  line-height: 1.6;
}
</style>
