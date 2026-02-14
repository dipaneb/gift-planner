<template>
  <div class="settings">
    <h1>Settings</h1>
    <div class="settings-content">
      <div class="settings-section">
        <h2>Profile Information</h2>
        <div v-if="!editingName" class="info-group">
          <div class="info-row">
            <label>Name:</label>
            <span>{{ authStore.user?.name || "Not set" }}</span>
          </div>
          <div class="info-row">
            <label>Email:</label>
            <span>{{ authStore.user?.email }}</span>
          </div>
          <button @click="editingName = true" class="btn-secondary">Edit Name</button>
        </div>
        <form v-else @submit.prevent="handleUpdateName" class="edit-form">
          <div class="form-group">
            <label for="name">Name:</label>
            <input
              id="name"
              v-model="nameForm.name"
              type="text"
              required
              minlength="1"
              maxlength="255"
              placeholder="Enter your name"
            />
          </div>
          <div v-if="nameError" class="error-message">{{ nameError }}</div>
          <div class="form-actions">
            <button type="submit" class="btn-primary" :disabled="isUpdatingName">
              {{ isUpdatingName ? 'Saving...' : 'Save' }}
            </button>
            <button type="button" @click="cancelEditName" class="btn-secondary" :disabled="isUpdatingName">
              Cancel
            </button>
          </div>
        </form>
      </div>

      <div class="settings-section">
        <h2>Change Password</h2>
        <form @submit.prevent="handleUpdatePassword" class="edit-form">
          <div class="form-group">
            <label for="current-password">Current Password:</label>
            <input
              id="current-password"
              v-model="passwordForm.current_password"
              type="password"
              required
              placeholder="Enter current password"
            />
          </div>
          <div class="form-group">
            <label for="new-password">New Password:</label>
            <input
              id="new-password"
              v-model="passwordForm.new_password"
              type="password"
              required
              minlength="8"
              placeholder="Enter new password (min 8 characters)"
            />
          </div>
          <div class="form-group">
            <label for="confirm-password">Confirm New Password:</label>
            <input
              id="confirm-password"
              v-model="passwordForm.confirmed_password"
              type="password"
              required
              minlength="8"
              placeholder="Confirm new password"
            />
          </div>
          <div v-if="passwordError" class="error-message">{{ passwordError }}</div>
          <div v-if="passwordSuccess" class="success-message">{{ passwordSuccess }}</div>
          <div class="form-actions">
            <button type="submit" class="btn-primary" :disabled="isUpdatingPassword">
              {{ isUpdatingPassword ? 'Updating...' : 'Update Password' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { usersApi } from '@/api/users'

const authStore = useAuthStore()

const editingName = ref(false)
const isUpdatingName = ref(false)
const isUpdatingPassword = ref(false)
const nameError = ref('')
const passwordError = ref('')
const passwordSuccess = ref('')

const nameForm = reactive({
  name: authStore.user?.name || '',
})

const passwordForm = reactive({
  current_password: '',
  new_password: '',
  confirmed_password: '',
})

const cancelEditName = () => {
  editingName.value = false
  nameForm.name = authStore.user?.name || ''
  nameError.value = ''
}

const handleUpdateName = async () => {
  nameError.value = ''
  isUpdatingName.value = true

  try {
    const updatedUser = await usersApi.updateName(authStore.accessToken!, {
      name: nameForm.name,
    })
    authStore.user = updatedUser
    editingName.value = false
  } catch (error) {
    nameError.value = error instanceof Error ? error.message : 'Failed to update name'
  } finally {
    isUpdatingName.value = false
  }
}

const handleUpdatePassword = async () => {
  passwordError.value = ''
  passwordSuccess.value = ''

  if (passwordForm.new_password !== passwordForm.confirmed_password) {
    passwordError.value = 'New password and confirmation do not match'
    return
  }

  if (passwordForm.new_password.length < 8) {
    passwordError.value = 'New password must be at least 8 characters'
    return
  }

  isUpdatingPassword.value = true

  try {
    await usersApi.updatePassword(authStore.accessToken!, {
      current_password: passwordForm.current_password,
      new_password: passwordForm.new_password,
      confirmed_password: passwordForm.confirmed_password,
    })
    passwordSuccess.value = 'Password updated successfully'
    passwordForm.current_password = ''
    passwordForm.new_password = ''
    passwordForm.confirmed_password = ''
  } catch (error) {
    passwordError.value = error instanceof Error ? error.message : 'Failed to update password'
  } finally {
    isUpdatingPassword.value = false
  }
}
</script>

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
  padding: 2rem;
  margin-bottom: 1.5rem;
}

.settings-section h2 {
  color: #2c3e50;
  font-size: 1.3rem;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #3498db;
}

.info-group {
  margin-top: 1rem;
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
  word-break: break-all;
}

.user-id {
  font-family: monospace;
  font-size: 0.9rem;
}

.edit-form {
  margin-top: 1rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-weight: 600;
  color: #555;
  margin-bottom: 0.5rem;
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #3498db;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

.btn-primary,
.btn-secondary {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-primary {
  background-color: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2980b9;
}

.btn-primary:disabled {
  background-color: #bdc3c7;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #ecf0f1;
  color: #2c3e50;
  margin-top: 1rem;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #d5dbdb;
}

.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  color: #e74c3c;
  background-color: #fadbd8;
  padding: 0.75rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.success-message {
  color: #27ae60;
  background-color: #d5f4e6;
  padding: 0.75rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}
</style>
