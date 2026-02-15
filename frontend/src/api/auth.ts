const API_BASE_URL = import.meta.env.VITE_BACKEND_URL;

// Type definitions for request/response data
export interface RegisterRequest {
  name: string;
  email: string;
  password: string;
  confirmed_password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: {
    id: string; // UUID serialized as string in JSON
    email: string;
    name: string | null;
    budget: string | null;
    spent: string;
    remaining: string | null;
  };
}

export interface User {
  id: string; // UUID serialized as string in JSON
  email: string;
  name: string | null;
  budget: string | null;
  spent: string;
  remaining: string | null;
}

export interface RefreshResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  password: string;
  confirmed_password: string;
}

export interface RegisterResponse {
  success: boolean;
  message: string;
}

export interface VerifyEmailResponse {
  success: boolean;
  message: string;
}

// Helper function to handle API errors
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: "An error occurred" }));
    throw new Error(error.message || `HTTP error! status: ${response.status}`);
  }
  return response.json();
}

/**
 * Auth API Service
 *
 * This API uses a dual-token system:
 * - Access Token (JWT): Short-lived, stored in memory, used for authenticated requests
 * - Refresh Token: Long-lived, stored in httpOnly cookie, used to get new access tokens
 *
 */
export const authApi = {
  /**
   * Register a new user
   * Sends verification email to the user
   * @param data - User registration data
   * @returns Promise with success message
   */
  async register(data: RegisterRequest): Promise<RegisterResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify(data),
    });
    return handleResponse<RegisterResponse>(response);
  },

  /**
   * Login an existing user
   * Returns access token (JWT) and sets refresh token as httpOnly cookie
   * @param credentials - User login credentials
   * @returns Promise with auth response including access token and user data
   */
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const data = new URLSearchParams();
    data.append("username", credentials.email);
    data.append("password", credentials.password);

    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      credentials: "include",
      body: data,
    });
    return handleResponse<AuthResponse>(response);
  },

  /**
   * Refresh the access token using the refresh token from cookie
   * @returns Promise with new access token
   */
  async refresh(): Promise<RefreshResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
    });
    return handleResponse<RefreshResponse>(response);
  },

  /**
   * Logout the current user
   * Deletes all refresh tokens for the user using the refresh token from cookie
   */
  async logout(): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/auth/logout`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
    });
    await handleResponse<void>(response);
  },

  /**
   * Request a password reset email
   * @param data - Email address for password reset
   */
  async forgotPassword(data: ForgotPasswordRequest): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/auth/forgot-password`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });
    await handleResponse<void>(response);
  },

  /**
   * Reset password using token from email
   * @param token - Reset token from email
   * @param data - New password
   */
  async resetPassword(token: string, data: ResetPasswordRequest): Promise<void> {
    const response = await fetch(
      `${API_BASE_URL}/auth/reset-password?token=${encodeURIComponent(token)}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      },
    );
    await handleResponse<void>(response);
  },

  /**
   * Verify email using token from email
   * @param token - Verification token from email
   */
  async verifyEmail(token: string): Promise<VerifyEmailResponse> {
    const response = await fetch(
      `${API_BASE_URL}/auth/verify-email?token=${encodeURIComponent(token)}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      },
    );
    return handleResponse<VerifyEmailResponse>(response);
  },
};
