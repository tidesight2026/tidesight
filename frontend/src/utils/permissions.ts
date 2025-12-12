/**
 * Permission helpers للـ Frontend
 */

export type UserRole = 'owner' | 'manager' | 'accountant' | 'worker' | 'viewer'

// Role hierarchy
const ROLE_PERMISSIONS: Record<UserRole, UserRole[]> = {
  owner: ['owner', 'manager', 'accountant', 'worker', 'viewer'],
  manager: ['manager', 'accountant', 'worker', 'viewer'],
  accountant: ['accountant', 'viewer'],
  worker: ['worker'],
  viewer: ['viewer'],
}

// Feature permissions
const FEATURE_PERMISSIONS: Record<string, UserRole[]> = {
  reports: ['owner', 'manager', 'accountant'],
  accounting: ['owner', 'manager', 'accountant'],
  sales: ['owner', 'manager', 'accountant'],
  zatca: ['owner', 'manager', 'accountant'],
  daily_operations: ['owner', 'manager', 'accountant', 'worker'],
  inventory: ['owner', 'manager', 'accountant', 'worker'],
  biological: ['owner', 'manager', 'accountant', 'worker'],
  view_only: ['owner', 'manager', 'accountant', 'worker', 'viewer'],
}

export function hasRole(userRole: UserRole | string | undefined, allowedRoles: UserRole[]): boolean {
  if (!userRole) return false
  
  const userAllowedRoles = ROLE_PERMISSIONS[userRole as UserRole] || []
  return allowedRoles.some(role => userAllowedRoles.includes(role))
}

export function hasFeaturePermission(userRole: UserRole | string | undefined, feature: string): boolean {
  if (!userRole) return false
  
  const allowedRoles = FEATURE_PERMISSIONS[feature] || []
  return hasRole(userRole, allowedRoles)
}

// Helper functions for common checks
export function canAccessReports(role?: string): boolean {
  return hasFeaturePermission(role as UserRole, 'reports')
}

export function canAccessAccounting(role?: string): boolean {
  return hasFeaturePermission(role as UserRole, 'accounting')
}

export function canAccessSales(role?: string): boolean {
  return hasFeaturePermission(role as UserRole, 'sales')
}

export function canAccessOperations(role?: string): boolean {
  return hasFeaturePermission(role as UserRole, 'daily_operations')
}

export function canAccessInventory(role?: string): boolean {
  return hasFeaturePermission(role as UserRole, 'inventory')
}

export function canAccessBiological(role?: string): boolean {
  return hasFeaturePermission(role as UserRole, 'biological')
}

