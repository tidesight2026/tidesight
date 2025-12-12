import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User, AuthState } from '../types'
import { apiService } from '../services/api'
import { authUtils } from '../utils/auth'

interface AuthStore extends AuthState {
  login: (username: string, password: string) => Promise<void>
  logout: () => Promise<void>
  setUser: (user: User) => void
  setToken: (token: string, refreshToken: string) => void
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,

      login: async (username: string, password: string) => {
        try {
          const response = await apiService.login({ username, password })
          authUtils.setToken(response.access)
          authUtils.setRefreshToken(response.refresh)
          authUtils.setUser(response.user)
          
          set({
            user: response.user,
            token: response.access,
            refreshToken: response.refresh,
            isAuthenticated: true,
          })
        } catch (error) {
          throw error
        }
      },

      logout: async () => {
        try {
          await apiService.logout()
        } catch (error) {
          console.error('Logout error:', error)
        } finally {
          authUtils.clear()
          set({
            user: null,
            token: null,
            refreshToken: null,
            isAuthenticated: false,
          })
        }
      },

      setUser: (user: User) => {
        set({ user, isAuthenticated: true })
      },

      setToken: (token: string, refreshToken: string) => {
        authUtils.setToken(token)
        authUtils.setRefreshToken(refreshToken)
        set({ token, refreshToken })
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)

