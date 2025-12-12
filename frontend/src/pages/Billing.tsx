import { useEffect, useState } from 'react'
import Layout from '../components/layout/Layout'
import Card from '../components/common/Card'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { apiService } from '../services/api'
import type { SubscriptionInfo, UsageStats, SubscriptionInvoice, SubscriptionPlan } from '../types'
import { useAuthStore } from '../store/authStore'
import { useToast } from '../hooks/useToast'

export default function Billing() {
  const user = useAuthStore((state) => state.user)
  const [subscription, setSubscription] = useState<SubscriptionInfo | null>(null)
  const [usage, setUsage] = useState<UsageStats | null>(null)
  const [invoices, setInvoices] = useState<SubscriptionInvoice[]>([])
  const [plans, setPlans] = useState<SubscriptionPlan[]>([])
  const [upgradePlanId, setUpgradePlanId] = useState<number | null>(null)
  const [upgradeLoading, setUpgradeLoading] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { showToast } = useToast()

  useEffect(() => {
    const loadData = async () => {
      setLoading(true)
      setError(null)
      try {
        const [sub, usageData, inv, plansData] = await Promise.all([
          apiService.getSubscription(),
          apiService.getUsageStats(),
          apiService.getSubscriptionInvoices(),
          apiService.getPlansPublic(),
        ])
        setSubscription(sub)
        setUsage(usageData)
        setInvoices(inv)
        setPlans(plansData)
        if (plansData.length > 0) {
          setUpgradePlanId(plansData[0].id)
        }
      } catch (err: any) {
        console.error('Error loading billing data:', err)
        setError(err.response?.data?.detail || 'فشل تحميل بيانات الاشتراك')
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])

  const statusColor: Record<string, string> = {
    active: 'text-green-600 bg-green-50',
    trial: 'text-blue-600 bg-blue-50',
    past_due: 'text-amber-600 bg-amber-50',
    cancelled: 'text-red-600 bg-red-50',
    suspended: 'text-red-600 bg-red-50',
  }

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">الاشتراك والفوترة</h1>
            <p className="mt-2 text-gray-600">إدارة باقة الاشتراك، الاستهلاك، والفواتير</p>
          </div>
          {user && <span className="text-sm text-gray-500">المستخدم: {user.full_name}</span>}
        </div>

        {loading ? (
          <div className="flex justify-center py-16">
            <LoadingSpinner />
          </div>
        ) : error ? (
          <Card title="خطأ">
            <p className="text-red-600">{error}</p>
          </Card>
        ) : (
          <>
            {/* Subscription Summary */}
            {subscription && (
              <Card title="معلومات الاشتراك">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">الباقة الحالية</p>
                    <p className="text-lg font-semibold">{subscription.plan_name_ar || subscription.plan_name}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <p className="text-sm text-gray-500">الحالة</p>
                    <span
                      className={`px-2 py-1 rounded text-sm font-medium ${
                        statusColor[subscription.status] || 'bg-gray-100 text-gray-700'
                      }`}
                    >
                      {subscription.status_display || subscription.status}
                    </span>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">بداية الفترة الحالية</p>
                    <p className="font-medium">{new Date(subscription.current_period_start).toLocaleDateString()}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">نهاية الفترة الحالية</p>
                    <p className="font-medium">{new Date(subscription.current_period_end).toLocaleDateString()}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">الأيام المتبقية</p>
                    <p className="font-medium">{subscription.remaining_days} يوم</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">التجديد التلقائي</p>
                    <p className="font-medium">{subscription.auto_renew ? 'مفعل' : 'غير مفعل'}</p>
                  </div>
                </div>
              </Card>
            )}

            {/* Upgrade Plan */}
            {plans.length > 0 && (
              <Card title="ترقية الباقة">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">اختر الباقة</label>
                    <select
                      className="input-field"
                      value={upgradePlanId ?? ''}
                      onChange={(e) => setUpgradePlanId(Number(e.target.value))}
                    >
                      {plans.map((p) => (
                        <option key={p.id} value={p.id}>
                          {p.name_ar} — {p.price_monthly} ر.س/شهر
                        </option>
                      ))}
                    </select>
                    <p className="text-xs text-gray-500 mt-1">سيتم تطبيق الشروط حسب نظام الفوترة.</p>
                  </div>
                  <div className="flex items-end">
                    <button
                      disabled={!upgradePlanId || upgradeLoading}
                      onClick={async () => {
                        if (!upgradePlanId) return
                        setUpgradeLoading(true)
                        try {
                          const res = await apiService.upgradePlan(upgradePlanId)
                          showToast(res.message || 'تمت الترقية بنجاح', 'success')
                          // تحديث بيانات الاشتراك بعد الترقية
                          const sub = await apiService.getSubscription()
                          setSubscription(sub)
                        } catch (err: any) {
                          setError(err.response?.data?.detail || 'فشل الترقية')
                          showToast(err.response?.data?.detail || 'فشل الترقية', 'error')
                        } finally {
                          setUpgradeLoading(false)
                        }
                      }}
                      className="px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700 disabled:opacity-50 w-full"
                    >
                      {upgradeLoading ? '...جارٍ الترقية' : 'ترقية الآن'}
                    </button>
                  </div>
                </div>
              </Card>
            )}

            {/* Usage */}
            {usage && (
              <Card title="الاستهلاك">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <UsageItem label="الأحواض" used={usage.ponds_used} limit={usage.ponds_limit} />
                  <UsageItem label="المستخدمون" used={usage.users_used} limit={usage.users_limit} />
                  <UsageItem label="التخزين (GB)" used={usage.storage_used_gb} limit={usage.storage_limit_gb} />
                </div>
              </Card>
            )}

            {/* Invoices */}
            <Card title="الفواتير">
              {invoices.length === 0 ? (
                <p className="text-gray-500">لا توجد فواتير حتى الآن.</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">رقم الفاتورة</th>
                        <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">التاريخ</th>
                        <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">الاستحقاق</th>
                        <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">الحالة</th>
                        <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">الإجمالي</th>
                        <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">تحميل</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {invoices.map((inv) => (
                        <tr key={inv.id}>
                          <td className="px-4 py-2 text-sm text-gray-900">{inv.invoice_number}</td>
                          <td className="px-4 py-2 text-sm text-gray-700">
                            {new Date(inv.invoice_date).toLocaleDateString()}
                          </td>
                          <td className="px-4 py-2 text-sm text-gray-700">
                            {new Date(inv.due_date).toLocaleDateString()}
                          </td>
                          <td className="px-4 py-2 text-sm">
                            <StatusBadge status={inv.status} />
                          </td>
                          <td className="px-4 py-2 text-sm text-gray-900 font-medium">{inv.total_amount} ر.س</td>
                          <td className="px-4 py-2 text-sm">
                            {inv.pdf_url ? (
                              <a className="text-primary-600 hover:underline" href={inv.pdf_url} target="_blank">
                                PDF
                              </a>
                            ) : (
                              <span className="text-gray-400">-</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </Card>
          </>
        )}
      </div>
    </Layout>
  )
}

function UsageItem({ label, used, limit }: { label: string; used: number; limit?: number | null }) {
  const percent = limit && limit > 0 ? Math.min(100, Math.round((used / limit) * 100)) : null
  return (
    <div className="p-4 border border-gray-200 rounded-lg">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-lg font-semibold text-gray-900">
        {used} {limit ? `/ ${limit}` : ''}
      </p>
      {percent !== null && (
        <div className="mt-2 w-full h-2 bg-gray-100 rounded">
          <div className="h-2 bg-primary-500 rounded" style={{ width: `${percent}%` }} />
        </div>
      )}
    </div>
  )
}

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, { text: string; className: string }> = {
    paid: { text: 'مدفوعة', className: 'bg-green-100 text-green-800' },
    issued: { text: 'مصدرة', className: 'bg-blue-100 text-blue-800' },
    overdue: { text: 'متأخرة', className: 'bg-amber-100 text-amber-800' },
    draft: { text: 'مسودة', className: 'bg-gray-100 text-gray-700' },
    cancelled: { text: 'ملغاة', className: 'bg-red-100 text-red-800' },
  }
  const badge = map[status] || map.draft
  return <span className={`px-2 py-1 text-xs rounded ${badge.className}`}>{badge.text}</span>
}

