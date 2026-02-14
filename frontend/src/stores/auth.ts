import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

import { authApi, type AuthResponse, type User, type LoginRequest, type RegisterRequest } from '@/api/auth'
import { usersApi } from '@/api/users'


export const useAuthStore = defineStore('auth', () => {
  // State
  const accessToken = ref<string | null>(null)
  const user = ref<User | null>(null)
  const isInitialized = ref(false)
  const isInitializing = ref(false)

  // Getters
  const isAuthenticated = computed(() => !!accessToken.value)

  // Actions
  
  /**
   * Initialize authentication state on app load
   * Attempts to refresh the access token using the httpOnly cookie
   * This should be called once during app initialization
   * Returns true if authenticated, false otherwise
   */
  async function initialize(): Promise<boolean> {
    // Prevent multiple simultaneous initialization attempts
    if (isInitialized.value || isInitializing.value) {
      return isAuthenticated.value
    }

    isInitializing.value = true

    try {
      const response = await authApi.refresh()
      accessToken.value = response.access_token
      user.value = response.user
      
      return true
    } catch (error) {
      // Refresh failed - user is not authenticated
      accessToken.value = null
      user.value = null
      return false
    } finally {
      isInitialized.value = true
      isInitializing.value = false
    }
  }

  /**
   * Login with email and password
   */
  async function login(credentials: LoginRequest): Promise<void> {
    const response = await authApi.login(credentials)
    setAuthData(response)
  }

  /**
   * Register a new user
   */
  async function register(data: RegisterRequest): Promise<void> {
    const response = await authApi.register(data)
    setAuthData(response)
  }

  /**
   * Logout the current user
   * Clears local state and calls the backend logout endpoint
   */
  async function logout(): Promise<void> {
    try {
      await authApi.logout()
    } catch (error) {
      // Even if backend logout fails, clear local state
      console.error('Logout error:', error)
    } finally {
      clearAuthData()
    }
  }

  /**
   * Set authentication data from login/register response
   */
  function setAuthData(response: AuthResponse): void {
    accessToken.value = response.access_token
    user.value = response.user
  }

  /**
   * Clear all authentication data
   */
  function clearAuthData(): void {
    accessToken.value = null
    user.value = null
  }

  /**
   * Refresh user data from the backend
   * Useful after operations that affect computed fields (e.g., budget spent/remaining)
   */
  async function refreshUser(): Promise<void> {
    if (!accessToken.value) return
    
    try {
      const updatedUser = await usersApi.getCurrentUser(accessToken.value)
      user.value = updatedUser
    } catch (error) {
      console.error('Failed to refresh user data:', error)
    }
  }

  return {
    // State
    accessToken,
    user,
    isInitialized,
    isInitializing,
    
    // Getters
    isAuthenticated,
    
    // Actions
    initialize,
    login,
    register,
    logout,
    refreshUser,
  }
})
