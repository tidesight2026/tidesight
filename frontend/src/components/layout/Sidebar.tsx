import { Link, useLocation } from 'react-router-dom'
import type { User } from '../../types'
import LanguageSwitcher from '../common/LanguageSwitcher'
import {
  canAccessReports,
  canAccessAccounting,
  canAccessSales,
  canAccessOperations,
  canAccessInventory,
  canAccessBiological,
} from '../../utils/permissions'

interface SidebarProps {
  user: User | null
  onLogout: () => void
}

interface MenuItem {
  name: string
  path: string
  icon: string
  requiresPermission?: (role?: string) => boolean
  requiresStaff?: boolean
}

const getAllMenuItems = (): MenuItem[] => [
  { name: 'لوحة التحكم', path: '/dashboard', icon: '📊' },
  { name: 'المزرعة', path: '/farm', icon: '🏭', requiresPermission: canAccessBiological },
  { name: 'الأحواض', path: '/ponds', icon: '🐟', requiresPermission: canAccessBiological },
  { name: 'الدفعات', path: '/batches', icon: '📦', requiresPermission: canAccessBiological },
  { name: 'المخزون', path: '/inventory', icon: '📋', requiresPermission: canAccessInventory },
  { name: 'العمليات اليومية', path: '/operations', icon: '📝', requiresPermission: canAccessOperations },
  { name: 'الحصاد', path: '/harvests', icon: '🌾', requiresPermission: canAccessSales },
  { name: 'طلبات البيع', path: '/sales-orders', icon: '📋', requiresPermission: canAccessSales },
  { name: 'الفواتير', path: '/invoices', icon: '🧾', requiresPermission: canAccessSales },
  { name: 'الاشتراك والفوترة', path: '/billing', icon: '💳', requiresPermission: (role?: string) => role === 'owner' || role === 'manager' },
  { name: 'لوحة المالك', path: '/saas-admin', icon: '🛡️', requiresStaff: true },
  { name: 'التقارير', path: '/reports', icon: '📈', requiresPermission: canAccessReports },
  { name: 'المحاسبة', path: '/accounting', icon: '💰', requiresPermission: canAccessAccounting },
  { name: 'إعادة التقييم (IAS 41)', path: '/biological-asset-revaluations', icon: '📊', requiresPermission: canAccessAccounting },
  { name: 'سجلات التدقيق', path: '/audit-logs', icon: '📋', requiresPermission: (role?: string) => role === 'owner' || role === 'manager' },
  { name: 'الإعدادات', path: '/settings', icon: '⚙️' },
]

export default function Sidebar({ user, onLogout }: SidebarProps) {
  const location = useLocation()
  const menuItems = getAllMenuItems()

  // Filter menu items based on permissions
  const visibleMenuItems = menuItems.filter((item) => {
    if (item.requiresStaff && !user?.is_staff) return false
    if (!item.requiresPermission) return true
    return item.requiresPermission(user?.role)
  })

  return (
    <div className="w-64 bg-white shadow-lg flex flex-col">
      {/* Logo */}
      <div className="h-16 flex items-center justify-center border-b border-gray-200 px-4">
        <h2 className="text-lg font-bold text-primary-600 flex-1">AquaERP</h2>
        <LanguageSwitcher />
      </div>

      {/* User Info */}
      {user && (
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-full bg-primary-600 flex items-center justify-center text-white font-medium">
              {user.full_name.charAt(0)}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">{user.full_name}</p>
              <p className="text-xs text-gray-500 truncate">{user.role}</p>
            </div>
          </div>
        </div>
      )}

      {/* Navigation Menu */}
      <nav className="flex-1 overflow-y-auto py-4">
        <ul className="space-y-1 px-2">
          {visibleMenuItems.map((item) => {
            const isActive = location.pathname === item.path
            return (
              <li key={item.path}>
                <Link
                  to={item.path}
                  className={`
                    flex items-center gap-3 px-4 py-3 rounded-lg transition-colors
                    ${isActive
                      ? 'bg-primary-50 text-primary-700 font-medium'
                      : 'text-gray-700 hover:bg-gray-50'
                    }
                  `}
                >
                  <span className="text-lg">{item.icon}</span>
                  <span>{item.name}</span>
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>

      {/* Logout Button */}
      <div className="p-4 border-t border-gray-200">
        <button
          onClick={onLogout}
          className="w-full flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-red-50 hover:text-red-700 rounded-lg transition-colors"
        >
          <span className="text-lg">🚪</span>
          <span>تسجيل الخروج</span>
        </button>
      </div>
    </div>
  )
}

