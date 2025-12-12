export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://tidesight.cloud'

export const ROLES = {
  OWNER: 'owner',
  MANAGER: 'manager',
  ACCOUNTANT: 'accountant',
  WORKER: 'worker',
  VIEWER: 'viewer',
} as const

