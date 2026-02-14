import type { User } from './auth'

const API_BASE_URL = import.meta.env.VITE_BACKEND_URL

export interface BudgetUpdateRequest {
  budget: number
}

export interface UserNameUpdateRequest {
  name: string
}

export interface UserPasswordUpdateRequest {
  current_password: string
  new_password: string
  confirmed_password: string
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'An error occurred' }))
    throw new Error(error.detail || error.message || `HTTP error! status: ${response.status}`)
  }
  return response.json()
}

export const usersApi = {
  /**
   * Get the current authenticated user
   * @param token - The access token (JWT)
   * @returns Promise with user data
   */
  async getCurrentUser(token: string): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/users/me`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      credentials: 'include',
    })
    return handleResponse<User>(response)
  },

  async updateBudget(token: string, data: BudgetUpdateRequest): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/users/me/budget`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      credentials: 'include',
      body: JSON.stringify(data),
    })
    return handleResponse<User>(response)
  },

  async deleteBudget(token: string): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/users/me/budget`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      credentials: 'include',
    })
    return handleResponse<User>(response)
  },

  async updateName(token: string, data: UserNameUpdateRequest): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/users/me`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      credentials: 'include',
      body: JSON.stringify(data),
    })
    return handleResponse<User>(response)
  },

  async updatePassword(token: string, data: UserPasswordUpdateRequest): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/users/me/password`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      credentials: 'include',
      body: JSON.stringify(data),
    })
    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'An error occurred' }))
      throw new Error(error.detail || error.message || `HTTP error! status: ${response.status}`)
    }
  },
}
