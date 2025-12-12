import { useEffect, useState } from 'react'
import Layout from '../components/layout/Layout'
import Card from '../components/common/Card'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { apiService } from '../services/api'
import type { SaaSStats, TenantSummary, SubscriptionPlan } from '../types'
import { useAuthStore } from '../store/authStore'
import { Navigate } from 'react-router-dom'
import { authUtils } from '../utils/auth'
import { useToast } from '../hooks/useToast'

export default function SuperAdminDashboard() {
  const user = useAuthStore((state) => state.user)
  const [stats, setStats] = useState<SaaSStats | null>(null)
  const [tenants, setTenants] = useState<TenantSummary[]>([])
  const [plans, setPlans] = useState<SubscriptionPlan[]>([])
  const [loadingAction, setLoadingAction] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [actionError, setActionError] = useState<string | null>(null)
  const [createLoading, setCreateLoading] = useState(false)
  const [createError, setCreateError] = useState<string | null>(null)
  const { showToast } = useToast()
  const [form, setForm] = useState({
    farm_name: '',
    subdomain: '',
    email: '',
    admin_username: '',
    admin_email: '',
    admin_password: '',
    plan_id: 0,
    trial_days: 14,
  })

  // حراسة الوصول: فقط للمستخدمين staff/superuser
  if (!user?.is_staff) {
    return <Navigate to="/dashboard" replace />
  }

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      setError(null)
      setActionError(null)
      try {
        const [statsRes, tenantsRes, plansRes] = await Promise.all([
          apiService.getSaasStats(),
          apiService.getTenants(),
          apiService.getPlansAdmin(),
        ])
        setStats(statsRes)
        setTenants(tenantsRes)
        setPlans(plansRes)
        if (plansRes.length > 0 && form.plan_id === 0) {
          setForm((f) => ({ ...f, plan_id: plansRes[0].id }))
        }
      } catch (err: any) {
        console.error('Error loading super admin data', err)
        setError(err.response?.data?.detail || 'فشل تحميل بيانات SaaS')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const reloadTenants = async () => {
    try {
      const tenantsRes = await apiService.getTenants()
      setTenants(tenantsRes)
    } catch (err: any) {
      setActionError(err.response?.data?.detail || 'فشل تحديث قائمة المستأجرين')
    }
  }

  const handleSuspend = async (id: number) => {
    setLoadingAction(true)
    setActionError(null)
    try {
      await apiService.suspendTenant(id)
      await reloadTenants()
    } catch (err: any) {
      setActionError(err.response?.data?.detail || 'فشل تجميد الحساب')
      showToast(err.response?.data?.detail || 'فشل تجميد الحساب', 'error')
    } finally {
      setLoadingAction(false)
    }
  }

  const handleActivate = async (id: number) => {
    setLoadingAction(true)
    setActionError(null)
    try {
      await apiService.activateTenant(id)
      await reloadTenants()
    } catch (err: any) {
      setActionError(err.response?.data?.detail || 'فشل تفعيل الحساب')
      showToast(err.response?.data?.detail || 'فشل تفعيل الحساب', 'error')
    } finally {
      setLoadingAction(false)
    }
  }

  const handleImpersonate = async (id: number) => {
    setLoadingAction(true)
    setActionError(null)
    try {
      const res = await apiService.impersonateTenant(id)
      // حفظ التوكن الجديد ثم إعادة التوجيه
      authUtils.setToken(res.access_token)
      authUtils.setRefreshToken(res.refresh_token)
      window.location.href = res.redirect_url
    } catch (err: any) {
      setActionError(err.response?.data?.detail || 'فشل الدخول كعميل')
      showToast(err.response?.data?.detail || 'فشل الدخول كعميل', 'error')
    } finally {
      setLoadingAction(false)
    }
  }

  const handleCreateTenant = async (e: React.FormEvent) => {
    e.preventDefault()
    setCreateLoading(true)
    setCreateError(null)
    try {
      await apiService.createTenant({
        farm_name: form.farm_name,
        subdomain: form.subdomain,
        email: form.email,
        admin_username: form.admin_username,
        admin_email: form.admin_email,
        admin_password: form.admin_password,
        plan_id: form.plan_id,
        trial_days: form.trial_days,
      })
      // إعادة تحميل قائمة المستأجرين
      await reloadTenants()
      showToast('تم إنشاء المستأجر بنجاح', 'success')
      setForm({
        farm_name: '',
        subdomain: '',
        email: '',
        admin_username: '',
        admin_email: '',
        admin_password: '',
        plan_id: plans.length > 0 ? plans[0].id : 0,
        trial_days: 14,
      })
    } catch (err: any) {
      setCreateError(err.response?.data?.detail || 'فشل إنشاء المستأجر')
      showToast(err.response?.data?.detail || 'فشل إنشاء المستأجر', 'error')
    } finally {
      setCreateLoading(false)
    }
  }

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">لوحة المالك (Super Admin)</h1>
            <p className="mt-2 text-gray-600">إدارة المستأجرين والاشتراكات والإيرادات الشهرية</p>
          </div>
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
            {/* Stats */}
            {stats && (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                <StatCard label="إجمالي الشركات" value={stats.total_tenants} />
                <StatCard label="اشتراكات نشطة" value={stats.active_subscriptions} />
                <StatCard label="تجريبي" value={stats.trial_subscriptions} />
                <StatCard label="ستنتهي قريباً (7 أيام)" value={stats.tenants_expiring_soon} />
                <StatCard label="اشتراكات منتهية/ملغاة" value={stats.expired_subscriptions} />
                <StatCard label="الإيراد الشهري المتكرر (MRR)" value={`${stats.monthly_revenue.toFixed(2)} ر.س`} />
              </div>
            )}

            {/* حالة الاشتراكات (توضيح) */}
            <Card title="توضيح حالات الاشتراك">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm text-gray-700">
                <div className="flex items-start gap-2">
                  <StatusBadge status="active" /> <span>نشط: وصول كامل.</span>
                </div>
                <div className="flex items-start gap-2">
                  <StatusBadge status="trial" /> <span>تجريبي: وصول كامل حتى نهاية الفترة.</span>
                </div>
                <div className="flex items-start gap-2">
                  <StatusBadge status="past_due" /> <span>متأخر: قراءة فقط، يمنع التعديلات حتى الدفع.</span>
                </div>
                <div className="flex items-start gap-2">
                  <StatusBadge status="suspended" /> <span>معلق: الوصول محجوب، بقرار إداري.</span>
                </div>
                <div className="flex items-start gap-2">
                  <StatusBadge status="cancelled" /> <span>ملغي: الوصول محجوب، يلزم إعادة تفعيل أو اشتراك جديد.</span>
                </div>
              </div>
            </Card>

            {/* Create Tenant */}
            <Card title="إنشاء مستأجر جديد">
              {createError && <p className="text-red-600 mb-2 text-sm">{createError}</p>}
              <form className="grid grid-cols-1 md:grid-cols-2 gap-4" onSubmit={handleCreateTenant}>
                <Input label="اسم المزرعة" value={form.farm_name} onChange={(v) => setForm({ ...form, farm_name: v })} required />
                <Input
                  label="النطاق الفرعي (subdomain)"
                  value={form.subdomain}
                  onChange={(v) => setForm({ ...form, subdomain: v })}
                  hint="مثال: farm1"
                  required
                />
                <Input label="بريد المزرعة" value={form.email} onChange={(v) => setForm({ ...form, email: v })} required />
                <Input
                  label="اسم مدير النظام (Tenant Admin)"
                  value={form.admin_username}
                  onChange={(v) => setForm({ ...form, admin_username: v })}
                  required
                />
                <Input
                  label="بريد المدير"
                  value={form.admin_email}
                  onChange={(v) => setForm({ ...form, admin_email: v })}
                  required
                />
                <Input
                  label="كلمة مرور المدير"
                  type="password"
                  value={form.admin_password}
                  onChange={(v) => setForm({ ...form, admin_password: v })}
                  required
                />
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">الباقة</label>
                  <select
                    className="input-field"
                    value={form.plan_id}
                    onChange={(e) => setForm({ ...form, plan_id: Number(e.target.value) })}
                  >
                    {plans.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.name_ar} - {p.price_monthly} ر.س/شهر
                      </option>
                    ))}
                  </select>
                </div>
                <Input
                  label="أيام التجربة"
                  type="number"
                  value={String(form.trial_days)}
                  onChange={(v) => setForm({ ...form, trial_days: Number(v) || 0 })}
                  required
                />
                <div className="md:col-span-2">
                  <button
                    type="submit"
                    disabled={createLoading}
                    className="px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700 disabled:opacity-50"
                  >
                    {createLoading ? '...جارٍ الإنشاء' : 'إنشاء مستأجر'}
                  </button>
                </div>
              </form>
            </Card>

            {/* Tenants Table */}
            <Card title="المستأجرون">
              {tenants.length === 0 ? (
                <p className="text-gray-500">لا يوجد مستأجرون حالياً.</p>
              ) : (
                <div className="overflow-x-auto">
                  {actionError && <p className="text-red-600 mb-2 text-sm">{actionError}</p>}
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">الشركة</th>
                        <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">النطاق</th>
                        <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">الباقة</th>
                        <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">الحالة</th>
                        <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">تاريخ الإنشاء</th>
                        <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">المستخدمون</th>
                        <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">إجراءات</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {tenants.map((t) => (
                        <tr key={t.id}>
                          <td className="px-4 py-2 text-sm text-gray-900">
                            <div className="font-medium">{t.name}</div>
                            <div className="text-xs text-gray-500">{t.email}</div>
                          </td>
                          <td className="px-4 py-2 text-sm text-gray-700">{t.domain}</td>
                          <td className="px-4 py-2 text-sm text-gray-700">{t.plan_name}</td>
                          <td className="px-4 py-2 text-sm">
                            <StatusBadge status={t.subscription_status} />
                          </td>
                          <td className="px-4 py-2 text-sm text-gray-700">
                            {new Date(t.created_on).toLocaleDateString()}
                          </td>
                          <td className="px-4 py-2 text-sm text-gray-700">{t.user_count ?? '-'}</td>
                          <td className="px-4 py-2 text-sm text-gray-700">
                            <TenantActions
                              tenantId={t.id}
                              status={t.subscription_status}
                              onSuspend={handleSuspend}
                              onActivate={handleActivate}
                              onImpersonate={handleImpersonate}
                              loading={loadingAction}
                            />
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

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="p-4 border border-gray-200 rounded-lg bg-white shadow-sm">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="mt-1 text-xl font-semibold text-gray-900">{value}</p>
    </div>
  )
}

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, { text: string; className: string }> = {
    active: { text: 'نشط', className: 'bg-green-100 text-green-800' },
    trial: { text: 'تجريبي', className: 'bg-blue-100 text-blue-800' },
    past_due: { text: 'متأخر', className: 'bg-amber-100 text-amber-800' },
    cancelled: { text: 'ملغي', className: 'bg-red-100 text-red-800' },
    suspended: { text: 'معلق', className: 'bg-red-100 text-red-800' },
    none: { text: 'غير محدد', className: 'bg-gray-100 text-gray-700' },
  }
  const badge = map[status] || map.none
  return <span className={`px-2 py-1 text-xs rounded ${badge.className}`}>{badge.text}</span>
}

// Action buttons row
function TenantActions({
  tenantId,
  status,
  onSuspend,
  onActivate,
  onImpersonate,
  loading,
}: {
  tenantId: number
  status: string
  onSuspend: (id: number) => void
  onActivate: (id: number) => void
  onImpersonate: (id: number) => void
  loading: boolean
}) {
  const confirmSuspend = () =>
    window.confirm('سيتم تجميد الحساب ومنع الوصول. هل أنت متأكد من المتابعة؟')
  const confirmActivate = () => window.confirm('سيتم تفعيل الحساب وتمكين الوصول. هل أنت متأكد؟')

  return (
    <div className="flex flex-wrap gap-2">
      <button
        disabled={loading || status === 'cancelled' || status === 'suspended'}
        onClick={() => {
          if (confirmSuspend()) onSuspend(tenantId)
        }}
        className="px-3 py-1 text-xs rounded border border-red-200 bg-red-50 text-red-700 hover:bg-red-100 disabled:opacity-50"
      >
        تجميد
      </button>
      <button
        disabled={loading}
        onClick={() => {
          if (confirmActivate()) onActivate(tenantId)
        }}
        className="px-3 py-1 text-xs rounded border border-green-200 bg-green-50 text-green-700 hover:bg-green-100 disabled:opacity-50"
      >
        تفعيل
      </button>
      <button
        disabled={loading}
        onClick={() => onImpersonate(tenantId)}
        className="px-3 py-1 text-xs rounded border border-blue-200 bg-blue-50 text-blue-700 hover:bg-blue-100 disabled:opacity-50"
      >
        دخول كـ...
      </button>
    </div>
  )
}

function Input({
  label,
  value,
  onChange,
  hint,
  type = 'text',
  required = false,
}: {
  label: string
  value: string
  onChange: (val: string) => void
  hint?: string
  type?: string
  required?: boolean
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      <input
        type={type}
        className="input-field"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        required={required}
      />
      {hint && <p className="text-xs text-gray-500 mt-1">{hint}</p>}
    </div>
  )
}

