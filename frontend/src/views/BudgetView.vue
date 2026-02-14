<template>
  <div class="budget">
    <h1>Budget</h1>
    <div class="budget-content">
      <div class="budget-section">
        <h2>Budget Overview</h2>

        <div class="budget-stats">
          <div class="stat-card">
            <div class="stat-label">Total Budget</div>
            <div class="stat-value" :class="{ 'not-set': !authStore.user?.budget }">
              {{ authStore.user?.budget ? `${authStore.user.budget} €` : 'Not set' }}
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-label">Spent</div>
            <div class="stat-value spent">
              {{ authStore.user?.spent || '0.00' }} €
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-label">Remaining</div>
            <div class="stat-value" :class="remainingClass">
              {{ remainingDisplay }}
            </div>
          </div>
        </div>

        <form @submit.prevent="handleSubmit" class="budget-form">
          <div class="form-group">
            <label for="budget-input">Budget (&euro;)</label>
            <input
              id="budget-input"
              v-model.number="budgetInput"
              type="number"
              min="0.01"
              step="0.01"
              placeholder="e.g. 500.00"
              required
            />
          </div>

          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="loading">
              {{ loading ? 'Saving...' : 'Set budget' }}
            </button>
            <button
              type="button"
              class="btn btn-danger"
              :disabled="loading || !authStore.user?.budget"
              @click="handleDelete"
            >
              {{ loading ? 'Removing...' : 'Remove budget' }}
            </button>
          </div>
        </form>

        <p v-if="error" class="error-message">{{ error }}</p>
        <p v-if="successMessage" class="success-message">{{ successMessage }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useBudget } from '@/composables/useBudget'

const authStore = useAuthStore()
const { loading, error, updateBudget, deleteBudget } = useBudget()

const budgetInput = ref<number | null>(
  authStore.user?.budget ? parseFloat(authStore.user.budget) : null,
)
const successMessage = ref<string | null>(null)

const remainingDisplay = computed(() => {
  if (!authStore.user?.budget) return 'N/A'
  if (authStore.user.remaining === null) return 'N/A'
  return `${authStore.user.remaining} €`
})

const remainingClass = computed(() => {
  if (!authStore.user?.budget || authStore.user.remaining === null) return 'not-set'
  const remaining = parseFloat(authStore.user.remaining)
  if (remaining < 0) return 'negative'
  if (remaining === 0) return 'zero'
  return 'positive'
})

function clearMessages() {
  successMessage.value = null
  error.value = null
}

async function handleSubmit() {
  clearMessages()
  if (budgetInput.value === null || budgetInput.value <= 0) return

  const ok = await updateBudget(budgetInput.value)
  if (ok) {
    successMessage.value = 'Budget updated successfully.'
  }
}

async function handleDelete() {
  clearMessages()

  const ok = await deleteBudget()
  if (ok) {
    budgetInput.value = null
    successMessage.value = 'Budget removed.'
  }
}
</script>

<style scoped>
.budget {
  padding: 1rem;
}

h1 {
  color: #2c3e50;
  margin-bottom: 1.5rem;
}

.budget-content {
  max-width: 800px;
}

.budget-section {
  background: #fff;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 2rem;
}

.budget-section h2 {
  color: #2c3e50;
  font-size: 1.3rem;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #3498db;
}

.budget-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border: 1px solid #dee2e6;
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-label {
  font-size: 0.85rem;
  color: #6c757d;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
  margin-bottom: 0.75rem;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: #2c3e50;
}

.stat-value.not-set {
  color: #999;
  font-size: 1.4rem;
  font-style: italic;
}

.stat-value.spent {
  color: #e67e22;
}

.stat-value.positive {
  color: #27ae60;
}

.stat-value.negative {
  color: #e74c3c;
}

.stat-value.zero {
  color: #95a5a6;
}

.budget-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.form-group label {
  font-weight: 600;
  color: #555;
  font-size: 0.9rem;
}

.form-group input {
  padding: 0.6rem 0.8rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  max-width: 250px;
}

.form-group input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.form-actions {
  display: flex;
  gap: 0.75rem;
}

.btn {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #3498db;
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  background: #2980b9;
}

.btn-danger {
  background: #e74c3c;
  color: #fff;
}

.btn-danger:hover:not(:disabled) {
  background: #c0392b;
}

.error-message {
  color: #e74c3c;
  margin-top: 0.75rem;
  font-size: 0.9rem;
}

.success-message {
  color: #27ae60;
  margin-top: 0.75rem;
  font-size: 0.9rem;
}
</style>
