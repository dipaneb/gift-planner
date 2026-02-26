import { ref } from "vue";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";

import { useAuthStore } from "@/stores/auth";
import { authApi } from "@/api/auth";
import type {
  LoginRequest,
  RegisterRequest,
  ForgotPasswordRequest,
  ResetPasswordRequest,
} from "@/api/auth";
import { getErrorMessage } from "./utils";

/**
 * Composable for auth actions with component-scoped loading and error states.
 * Uses the auth store for global state management but provides local UI state.
 *
 * This separates concerns:
 * - Store: Global state (token, user)
 * - Composable: Local UI state (loading, error)
 */

export function useAuth() {
  const router = useRouter();
  const { t } = useI18n();
  const authStore = useAuthStore();

  const loading = ref(false);
  const error = ref<string | null>(null);

  /**
   * Login with credentials
   * Handles redirect after successful login
   */
  async function login(credentials: LoginRequest, redirectPath?: string): Promise<boolean> {
    loading.value = true;
    error.value = null;

    try {
      await authStore.login(credentials);
      await router.push(redirectPath || "/recipients");
      return true;
    } catch (err) {
      error.value = getErrorMessage(err, t("errors.loginFailed"), {
        401: t("errors.invalidCredentials"),
        403: t("errors.emailNotVerified"),
      });
      return false;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Register a new user
   * Sends verification email instead of auto-login
   */
  async function register(data: RegisterRequest): Promise<{ success: boolean; message?: string }> {
    loading.value = true;
    error.value = null;

    try {
      const response = await authStore.register(data);
      return { success: true, message: response.message };
    } catch (err) {
      error.value = getErrorMessage(err, t("errors.registrationFailed"), {
        409: t("errors.emailAlreadyInUse"),
      });
      return { success: false };
    } finally {
      loading.value = false;
    }
  }

  /**
   * Logout the current user
   */
  async function logout(): Promise<void> {
    loading.value = true;
    error.value = null;

    try {
      await authStore.logout();
      await router.push("/login");
    } catch (err) {
      error.value = getErrorMessage(err, t("errors.logoutFailed"));
      // Still redirect to login even if logout fails
      await router.push("/login");
    } finally {
      loading.value = false;
    }
  }

  /**
   * Request a password reset email
   */
  async function forgotPassword(data: ForgotPasswordRequest): Promise<boolean> {
    loading.value = true;
    error.value = null;

    try {
      await authApi.forgotPassword(data);
      return true;
    } catch (err) {
      error.value = getErrorMessage(err, t("errors.forgotPasswordFailed"));
      return false;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Reset password using token from email
   */
  async function resetPassword(token: string, data: ResetPasswordRequest): Promise<boolean> {
    loading.value = true;
    error.value = null;

    try {
      await authApi.resetPassword(token, data);
      await router.push("/login");
      return true;
    } catch (err) {
      error.value = getErrorMessage(err, t("errors.resetPasswordFailed"), {
        400: t("errors.invalidOrExpiredToken"),
      });
      return false;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Verify email using token from email
   */
  async function verifyEmail(token: string): Promise<{ success: boolean; message?: string }> {
    loading.value = true;
    error.value = null;

    try {
      const response = await authApi.verifyEmail(token);
      return { success: true, message: response.message };
    } catch (err) {
      error.value = getErrorMessage(err, t("errors.verifyEmailFailed"));
      return { success: false };
    } finally {
      loading.value = false;
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
  };
}
