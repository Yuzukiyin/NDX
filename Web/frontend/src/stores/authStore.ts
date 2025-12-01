import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import apiClient from '../lib/api'
import type { User, LoginCredentials, RegisterData, TokenResponse } from '../types'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  login: (credentials: LoginCredentials) => Promise<void>
  register: (data: RegisterData) => Promise<void>
  logout: () => void
  fetchCurrentUser: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: !!localStorage.getItem('access_token'),

      login: async (credentials: LoginCredentials) => {
        const response = await apiClient.post<TokenResponse>('/auth/login', credentials)
        const { access_token, refresh_token } = response.data

        localStorage.setItem('access_token', access_token)
        localStorage.setItem('refresh_token', refresh_token)

        // Fetch user info
        const userResponse = await apiClient.get<User>('/auth/me')
        set({ user: userResponse.data, isAuthenticated: true })
      },

      register: async (data: RegisterData) => {
        await apiClient.post('/auth/register', data)
        // Auto login after registration
        await useAuthStore.getState().login({
          email: data.email,
          password: data.password,
        })
      },

      logout: () => {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        set({ user: null, isAuthenticated: false })
      },

      fetchCurrentUser: async () => {
        try {
          const response = await apiClient.get<User>('/auth/me')
          set({ user: response.data, isAuthenticated: true })
        } catch (error) {
          set({ user: null, isAuthenticated: false })
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ user: state.user }),
    }
  )
)
