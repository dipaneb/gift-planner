import api from '.'
import type { User } from './auth'

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

export const usersApi = {
  /**
   * Get the current authenticated user
   * @returns Promise with user data
   */
  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/users/me')
    return response.data
  },

  async updateBudget(data: BudgetUpdateRequest): Promise<User> {
    const response = await api.patch<User>('/users/me/budget', data)
    return response.data
  },

  async deleteBudget(): Promise<User> {
    const response = await api.delete<User>('/users/me/budget')
    return response.data
  },

  async updateName(data: UserNameUpdateRequest): Promise<User> {
    const response = await api.patch<User>('/users/me', data)
    return response.data
  },

  async updatePassword(data: UserPasswordUpdateRequest): Promise<void> {
    await api.patch('/users/me/password', data)
  },
}
