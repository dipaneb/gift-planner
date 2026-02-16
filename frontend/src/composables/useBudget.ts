import { ref } from 'vue'

import { useAuthStore } from '@/stores/auth'
import { usersApi } from '@/api/users'

/**
 * Composable for budget actions with component-scoped loading and error states.
 * Updates the auth store's user after each operation so the UI stays in sync.
 */
export function useBudget() {
  const authStore = useAuthStore()

  const loading = ref(false)
  const error = ref<string | null>(null)

  /**
   * Set or update the user's budget
   */
  async function updateBudget(budget: number): Promise<boolean> {
    loading.value = true
    error.value = null

    try {
      const updatedUser = await usersApi.updateBudget({ budget })
      authStore.user = updatedUser
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update budget'
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * Remove the user's budget
   */
  async function deleteBudget(): Promise<boolean> {
    loading.value = true
    error.value = null

    try {
      const updatedUser = await usersApi.deleteBudget()
      authStore.user = updatedUser
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete budget'
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    error,
    updateBudget,
    deleteBudget,
  }
}
