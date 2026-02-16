import api from ".";

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
    const response = await api.post<RegisterResponse>("/auth/register", data);
    return response.data;
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

    const response = await api.post<AuthResponse>("/auth/login", data, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
    return response.data;
  },

  /**
   * Refresh the access token using the refresh token from cookie
   * @returns Promise with new access token
   */
  async refresh(): Promise<RefreshResponse> {
    const response = await api.post<RefreshResponse>("/auth/refresh");
    return response.data;
  },

  /**
   * Logout the current user
   * Deletes all refresh tokens for the user using the refresh token from cookie
   */
  async logout(): Promise<void> {
    await api.post("/auth/logout");
  },

  /**
   * Request a password reset email
   * @param data - Email address for password reset
   */
  async forgotPassword(data: ForgotPasswordRequest): Promise<void> {
    await api.post("/auth/forgot-password", data);
  },

  /**
   * Reset password using token from email
   * @param token - Reset token from email
   * @param data - New password
   */
  async resetPassword(token: string, data: ResetPasswordRequest): Promise<void> {
    await api.post("/auth/reset-password", data, {
      params: { token },
    });
  },

  /**
   * Verify email using token from email
   * @param token - Verification token from email
   */
  async verifyEmail(token: string): Promise<VerifyEmailResponse> {
    const response = await api.post<VerifyEmailResponse>("/auth/verify-email", null, {
      params: { token },
    });
    return response.data;
  },
};
