# 📄 دليل ملفات Frontend - AquaERP

هذا الدليل يحتوي على جميع الملفات المطلوبة لـ Frontend مع محتواها الكامل.

---

## ⚠️ ملاحظة مهمة

قبل البدء، تأكد من:

1. ✅ إنشاء مشروع React (راجع `FRONTEND_QUICK_START.md`)
2. ✅ تثبيت جميع المكتبات
3. ✅ نسخ ملفات التكوين

---

## 📁 الملفات المطلوبة

### 1. ملفات التكوين

#### `frontend/vite.config.ts`

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

#### `frontend/tailwind.config.js`

انسخ من: `frontend_configs/tailwind.config.js`

#### `frontend/src/index.css`

انسخ من: `frontend_configs/index.css`

---

### 2. ملفات Types

#### `frontend/src/types/index.ts`

```typescript
export interface User {
  id: number
  username: string
  email: string
  full_name: string
  role: string
  is_staff: boolean
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface LoginResponse {
  access: string
  refresh: string
  user: User
}

export interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
  isAuthenticated: boolean
}
```

---

### 3. ملفات Constants

#### `frontend/src/utils/constants.ts`

```typescript
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const ROLES = {
  OWNER: 'owner',
  MANAGER: 'manager',
  ACCOUNTANT: 'accountant',
  WORKER: 'worker',
  VIEWER: 'viewer',
} as const
```

---

### 4. ملفات Auth Utilities

#### `frontend/src/utils/auth.ts`

```typescript
const TOKEN_KEY = 'auth_token'
const REFRESH_TOKEN_KEY = 'refresh_token'
const USER_KEY = 'user'

export const authUtils = {
  setToken: (token: string) => {
    localStorage.setItem(TOKEN_KEY, token)
  },
  
  getToken: (): string | null => {
    return localStorage.getItem(TOKEN_KEY)
  },
  
  setRefreshToken: (token: string) => {
    localStorage.setItem(REFRESH_TOKEN_KEY, token)
  },
  
  getRefreshToken: (): string | null => {
    return localStorage.getItem(REFRESH_TOKEN_KEY)
  },
  
  setUser: (user: any) => {
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  },
  
  getUser: (): any => {
    const user = localStorage.getItem(USER_KEY)
    return user ? JSON.parse(user) : null
  },
  
  clear: () => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  },
}
```

---

### 5. ملفات API Service

#### `frontend/src/services/api.ts`

```typescript
import axios, { AxiosInstance, AxiosError } from 'axios'
import { authUtils } from '../utils/auth'
import { API_BASE_URL } from '../utils/constants'
import type { LoginCredentials, LoginResponse, User } from '../types'

class ApiService {
  private api: AxiosInstance

  constructor() {
    this.api = axios.create({
      baseURL: `${API_BASE_URL}/api`,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor
    this.api.interceptors.request.use(
      (config) => {
        const token = authUtils.getToken()
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor
    this.api.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Handle token refresh or logout
          authUtils.clear()
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const response = await this.api.post<LoginResponse>('/auth/login', credentials)
    return response.data
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.api.get<User>('/auth/me')
    return response.data
  }

  async refreshToken(refreshToken: string): Promise<{ access: string }> {
    const response = await this.api.post<{ access: string }>('/auth/refresh', { refresh: refreshToken })
    return response.data
  }

  async logout(): Promise<void> {
    await this.api.post('/auth/logout')
  }
}

export const apiService = new ApiService()
```

---

### 6. ملفات Store (Zustand)

#### `frontend/src/store/authStore.ts`

```typescript
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
```

---

## 🎯 الخطوات التالية

بعد إنشاء هذه الملفات الأساسية، يمكنك:

1. إنشاء صفحات (Login, Dashboard)
2. إنشاء Components (LoginForm, Layout)
3. إعداد Routing

راجع `FRONTEND_COMPONENTS_GUIDE.md` للخطوات التالية.

---

**ملاحظة:** تأكد من تثبيت `zustand` مع middleware:

```bash
npm install zustand
```

---

**تاريخ الإنشاء:** ديسمبر 2025
