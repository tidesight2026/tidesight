/**
 * Global UI Store - إدارة حالة واجهة المستخدم (Loading, Toasts, Errors)
 */
import { create } from 'zustand'
import type { ToastType } from '../components/common/Toast'

interface ToastMessage {
  id: number
  message: string
  type: ToastType
  duration?: number
}

interface UIState {
  // Loading state
  isLoading: boolean
  loadingMessage: string | null
  
  // Toast messages
  toasts: ToastMessage[]
  
  // Actions
  setLoading: (isLoading: boolean, message?: string) => void
  showToast: (message: string, type?: ToastType, duration?: number) => void
  removeToast: (id: number) => void
  clearToasts: () => void
  
  // Helper methods
  success: (message: string, duration?: number) => void
  error: (message: string, duration?: number) => void
  warning: (message: string, duration?: number) => void
  info: (message: string, duration?: number) => void
}

export const useUIStore = create<UIState>((set, get) => ({
  // Initial state
  isLoading: false,
  loadingMessage: null,
  toasts: [],
  
  // Set loading state
  setLoading: (isLoading: boolean, message?: string) => {
    set({
      isLoading,
      loadingMessage: message || null,
    })
  },
  
  // Show toast
  showToast: (message: string, type: ToastType = 'info', duration: number = 3000) => {
    const id = Date.now() + Math.random()
    const toast: ToastMessage = { id, message, type, duration }
    
    set((state) => ({
      toasts: [...state.toasts, toast],
    }))
    
    // Auto remove after duration
    if (duration > 0) {
      setTimeout(() => {
        get().removeToast(id)
      }, duration)
    }
  },
  
  // Remove toast
  removeToast: (id: number) => {
    set((state) => ({
      toasts: state.toasts.filter((toast) => toast.id !== id),
    }))
  },
  
  // Clear all toasts
  clearToasts: () => {
    set({ toasts: [] })
  },
  
  // Helper methods
  success: (message: string, duration?: number) => {
    get().showToast(message, 'success', duration)
  },
  
  error: (message: string, duration?: number) => {
    get().showToast(message, 'error', duration)
  },
  
  warning: (message: string, duration?: number) => {
    get().showToast(message, 'warning', duration)
  },
  
  info: (message: string, duration?: number) => {
    get().showToast(message, 'info', duration)
  },
}))

