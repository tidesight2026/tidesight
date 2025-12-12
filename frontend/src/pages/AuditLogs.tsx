import { useEffect, useState } from 'react'
import Layout from '../components/layout/Layout'
import Card from '../components/common/Card'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { apiService } from '../services/api'
import type { AuditLog } from '../types'
import { useToast } from '../hooks/useToast'
import { useTranslation } from 'react-i18next'

export default function AuditLogs() {
  const { i18n } = useTranslation()
  const [logs, setLogs] = useState<AuditLog[]>([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    action_type: '',
    entity_type: '',
    start_date: '',
    end_date: '',
  })
  const { showToast } = useToast()

  useEffect(() => {
    fetchLogs()
  }, [filters])

  const fetchLogs = async () => {
    try {
      setLoading(true)
      const params: any = { limit: 200 }
      if (filters.action_type) params.action_type = filters.action_type
      if (filters.entity_type) params.entity_type = filters.entity_type
      if (filters.start_date) params.start_date = filters.start_date
      if (filters.end_date) params.end_date = filters.end_date
      
      const data = await apiService.getAuditLogs(params)
      setLogs(data)
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'خطأ في جلب سجلات التدقيق', 'error')
    } finally {
      setLoading(false)
    }
  }

  const getActionColor = (actionType: string) => {
    switch (actionType) {
      case 'create':
        return 'bg-green-100 text-green-800'
      case 'update':
        return 'bg-blue-100 text-blue-800'
      case 'delete':
        return 'bg-red-100 text-red-800'
      case 'login':
      case 'logout':
        return 'bg-purple-100 text-purple-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleString('ar-SA', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <Layout>
      <div className="space-y-6" dir={i18n.dir()}>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">سجلات التدقيق</h1>
          <p className="mt-2 text-gray-600">تتبع جميع العمليات الحساسة في النظام</p>
        </div>

        {/* Filters */}
        <Card title="تصفية السجلات">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                نوع العملية
              </label>
              <select
                value={filters.action_type}
                onChange={(e) => setFilters({ ...filters, action_type: e.target.value })}
                className="input-field"
              >
                <option value="">الكل</option>
                <option value="create">إنشاء</option>
                <option value="update">تعديل</option>
                <option value="delete">حذف</option>
                <option value="login">تسجيل دخول</option>
                <option value="logout">تسجيل خروج</option>
                <option value="export">تصدير</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                نوع الكيان
              </label>
              <select
                value={filters.entity_type}
                onChange={(e) => setFilters({ ...filters, entity_type: e.target.value })}
                className="input-field"
              >
                <option value="">الكل</option>
                <option value="account">حساب</option>
                <option value="journal_entry">قيد محاسبي</option>
                <option value="invoice">فاتورة</option>
                <option value="sales_order">طلب بيع</option>
                <option value="harvest">حصاد</option>
                <option value="user">مستخدم</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                من تاريخ
              </label>
              <input
                type="date"
                value={filters.start_date}
                onChange={(e) => setFilters({ ...filters, start_date: e.target.value })}
                className="input-field"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                إلى تاريخ
              </label>
              <input
                type="date"
                value={filters.end_date}
                onChange={(e) => setFilters({ ...filters, end_date: e.target.value })}
                className="input-field"
              />
            </div>
          </div>
        </Card>

        {/* Logs Table */}
        <Card>
          {loading ? (
            <div className="flex justify-center py-12">
              <LoadingSpinner />
            </div>
          ) : logs.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <p>لا توجد سجلات تدقيق</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      التاريخ والوقت
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      العملية
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      الكيان
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      المستخدم
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      IP
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      الوصف
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {logs.map((log) => (
                    <tr key={log.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(log.created_at)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`px-2 py-1 text-xs font-medium rounded-full ${getActionColor(
                            log.action_type
                          )}`}
                        >
                          {log.action_type_display}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <div>
                          <div className="font-medium">{log.entity_type_display}</div>
                          {log.entity_description && (
                            <div className="text-xs text-gray-500">{log.entity_description}</div>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {log.user_name || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-mono">
                        {log.user_ip || '-'}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {log.description || '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </div>
    </Layout>
  )
}

