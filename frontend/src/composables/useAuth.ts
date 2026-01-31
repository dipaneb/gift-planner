import { ref } from "vue";
import { useRouter } from "vue-router";
import {
  authApi,
  type RegisterRequest,
  type LoginRequest,
  type User,
  type ForgotPasswordRequest,
  type ResetPasswordRequest,
} from "@/api/auth";

// Store access token in memory (not localStorage for security).
let accessToken: string | null = null;

export function useAuth() {
  const router = useRouter();

  const loading = ref(false);
  const error = ref<string | null>(null);
  const user = ref<User | null>(null);
  const isAuthenticated = ref(false);

  /**
   * Register a new user.
   * Stores access token in memory and refresh token in httpOnly cookie.
   * Redirects to home on success.
   */
  const register = async (data: RegisterRequest): Promise<void> => {
    loading.value = true;
    error.value = null;

    try {
      const response = await authApi.register(data);

      // Store access token in memory (secure)
      accessToken = response.access_token;

      // Store user data
      user.value = response.user;
      isAuthenticated.value = true;

      // Redirect to home page or dashboard
      await router.push("/");
    } catch (err) {
      error.value = err instanceof Error ? err.message : "Registration failed";
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Login an existing user.
   * Stores access token in memory and refresh token in httpOnly cookie.
   * Redirects to home on success.
   */
  const login = async (credentials: LoginRequest): Promise<void> => {
    loading.value = true;
    error.value = null;

    try {
      const response = await authApi.login(credentials);

      // Store access token in memory (secure)
      accessToken = response.access_token;

      // Store user data
      user.value = response.user;
      isAuthenticated.value = true;

      // Redirect to home page or dashboard
      await router.push("/");
    } catch (err) {
      error.value = err instanceof Error ? err.message : "Login failed";
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Refresh the access token using the refresh token from cookie.
   * Call this when the access token expires.
   */
  const refreshToken = async (): Promise<void> => {
    loading.value = true;
    error.value = null;

    try {
      const response = await authApi.refresh();

      // Update access token in memory
      accessToken = response.access_token;
      isAuthenticated.value = true;
    } catch (err) {
      error.value = err instanceof Error ? err.message : "Token refresh failed";
      // Clear auth state on refresh failure
      accessToken = null;
      user.value = null;
      isAuthenticated.value = false;
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Logout the current user.
   * Deletes all refresh tokens for the user and clears local state.
   * Redirects to login page.
   */
  const logout = async (): Promise<void> => {
    loading.value = true;
    error.value = null;

    try {
      await authApi.logout();

      // Clear auth data
      accessToken = null;
      user.value = null;
      isAuthenticated.value = false;

      // Redirect to login page
      await router.push("/login");
    } catch (err) {
      error.value = err instanceof Error ? err.message : "Logout failed";
      // Still clear local state even if logout API fails
      accessToken = null;
      user.value = null;
      isAuthenticated.value = false;
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Fetch the current authenticated user.
   * Useful for checking auth status on app initialization.
   * If access token is expired, will attempt to refresh it.
   */
  const fetchCurrentUser = async (): Promise<void> => {
    if (!accessToken) {
      // Try to refresh the token from cookie
      try {
        await refreshToken();
      } catch {
        return;
      }
    }

    loading.value = true;
    error.value = null;

    try {
      user.value = await authApi.getCurrentUser(accessToken!);
      isAuthenticated.value = true;
    } catch (err) {
      error.value = err instanceof Error ? err.message : "Failed to fetch user";
      // If getCurrentUser fails, try refreshing the token once
      try {
        await refreshToken();
        user.value = await authApi.getCurrentUser(accessToken!);
        isAuthenticated.value = true;
      } catch {
        // Clear invalid token
        accessToken = null;
        isAuthenticated.value = false;
        throw err;
      }
    } finally {
      loading.value = false;
    }
  };

  /**
   * Request a password reset email.
   */
  const forgotPassword = async (data: ForgotPasswordRequest): Promise<void> => {
    loading.value = true;
    error.value = null;

    try {
      await authApi.forgotPassword(data);
    } catch (err) {
      error.value = err instanceof Error ? err.message : "Failed to send reset email";
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Reset password using token from email.
   */
  const resetPassword = async (token: string, data: ResetPasswordRequest): Promise<void> => {
    loading.value = true;
    error.value = null;

    try {
      await authApi.resetPassword(token, data);
      // Redirect to login after successful password reset
      await router.push("/login");
    } catch (err) {
      error.value = err instanceof Error ? err.message : "Failed to reset password";
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Get the current access token.
   * Useful for making authenticated API calls.
   */
  const getAccessToken = (): string | null => {
    return accessToken;
  };

  return {
    // State
    loading,
    error,
    user,
    isAuthenticated,

    // Methods
    register,
    login,
    logout,
    refreshToken,
    fetchCurrentUser,
    forgotPassword,
    resetPassword,
    getAccessToken,
  };
}
