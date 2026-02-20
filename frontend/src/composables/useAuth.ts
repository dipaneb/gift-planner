import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/auth'
import type { LoginRequest, RegisterRequest, ForgotPasswordRequest, ResetPasswordRequest } from '@/api/auth'
import { getErrorMessage } from './utils'

/**
 * Composable for auth actions with component-scoped loading and error states.
 * Uses the auth store for global state management but provides local UI state.
 * 
 * This separates concerns:
 * - Store: Global state (token, user)
 * - Composable: Local UI state (loading, error)
 */

export function useAuth() {
  const router = useRouter()
  const authStore = useAuthStore()
  
  const loading = ref(false)
  const error = ref<string | null>(null)

  /**
   * Login with credentials
   * Handles redirect after successful login
   */
  async function login(credentials: LoginRequest, redirectPath?: string): Promise<boolean> {
    loading.value = true
    error.value = null

    try {
      await authStore.login(credentials)
      await router.push(redirectPath || '/app')
      return true
    } catch (err) {
      error.value = getErrorMessage(err, 'Login failed')
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * Register a new user
   * Sends verification email instead of auto-login
   */
  async function register(data: RegisterRequest): Promise<{ success: boolean; message?: string }> {
    loading.value = true
    error.value = null

    try {
      const response = await authStore.register(data)
      return { success: true, message: response.message }
    } catch (err) {
      error.value = getErrorMessage(err, 'Registration failed')
      return { success: false }
    } finally {
      loading.value = false
    }
  }

  /**
   * Logout the current user
   */
  async function logout(): Promise<void> {
    loading.value = true
    error.value = null

    try {
      await authStore.logout()
      await router.push('/login')
    } catch (err) {
      error.value = getErrorMessage(err, 'Logout failed')
      // Still redirect to login even if logout fails
      await router.push('/login')
    } finally {
      loading.value = false
    }
  }

  /**
   * Request a password reset email
   */
  async function forgotPassword(data: ForgotPasswordRequest): Promise<boolean> {
    loading.value = true
    error.value = null

    try {
      await authApi.forgotPassword(data)
      return true
    } catch (err) {
      error.value = getErrorMessage(err, 'Failed to send reset email')
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * Reset password using token from email
   */
  async function resetPassword(token: string, data: ResetPasswordRequest): Promise<boolean> {
    loading.value = true
    error.value = null

    try {
      await authApi.resetPassword(token, data)
      await router.push('/login')
      return true
    } catch (err) {
      error.value = getErrorMessage(err, 'Failed to reset password')
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * Verify email using token from email
   */
  async function verifyEmail(token: string): Promise<{ success: boolean; message?: string }> {
    loading.value = true
    error.value = null

    try {
      const response = await authApi.verifyEmail(token)
      return { success: true, message: response.message }
    } catch (err) {
      error.value = getErrorMessage(err, 'Failed to verify email')
      return { success: false }
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    error,
    login,
    register,
    logout,
    forgotPassword,
    resetPassword,
    verifyEmail,
  }
}
