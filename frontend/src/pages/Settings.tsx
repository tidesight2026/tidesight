import { useEffect, useState } from 'react'
import Layout from '../components/layout/Layout'
import Card from '../components/common/Card'
import { useAuthStore } from '../store/authStore'
import { apiService } from '../services/api'
import type { User } from '../types'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { useToast } from '../hooks/useToast'

export default function Settings() {
  const currentUser = useAuthStore((state) => state.user)
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [creating, setCreating] = useState(false)
  const { showToast } = useToast()

  const [form, setForm] = useState({
    full_name: '',
    username: '',
    email: '',
    password: '',
    role: 'worker',
  })

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      setError(null)
      try {
        const list = await apiService.listUsers()
        setUsers(list)
      } catch (err: any) {
        setError(err.response?.data?.error || 'فشل تحميل المستخدمين')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    setCreating(true)
    setError(null)
    try {
      await apiService.createUser({
        full_name: form.full_name,
        username: form.username,
        email: form.email,
        password: form.password,
        role: form.role,
      })
      showToast('تم إنشاء المستخدم', 'success')
      const list = await apiService.listUsers()
      setUsers(list)
      setForm({ full_name: '', username: '', email: '', password: '', role: 'worker' })
    } catch (err: any) {
      setError(err.response?.data?.error || 'فشل إنشاء المستخدم')
      showToast(err.response?.data?.error || 'فشل إنشاء المستخدم', 'error')
    } finally {
      setCreating(false)
    }
  }

  const handleToggleActive = async (userId: number, active: boolean) => {
    setError(null)
    try {
      await apiService.updateUser(userId, { is_active: active })
      const list = await apiService.listUsers()
      setUsers(list)
    } catch (err: any) {
      setError(err.response?.data?.error || 'فشل تحديث الحالة')
      showToast(err.response?.data?.error || 'فشل تحديث الحالة', 'error')
    }
  }

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">الإعدادات</h1>
          <p className="mt-2 text-gray-600">إدارة الحساب والمستخدمين والأدوار</p>
        </div>

        {/* حسابي */}
        <Card title="معلومات الحساب">
          {currentUser && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <ReadOnly label="الاسم الكامل" value={currentUser.full_name} />
              <ReadOnly label="اسم المستخدم" value={currentUser.username} />
              <ReadOnly label="البريد الإلكتروني" value={currentUser.email} />
              <ReadOnly label="الدور" value={currentUser.role} />
            </div>
          )}
        </Card>

        {/* المستخدمون */}
        <Card title="إدارة المستخدمين">
          {loading ? (
            <div className="flex justify-center py-10">
              <LoadingSpinner />
            </div>
          ) : error ? (
            <p className="text-red-600">{error}</p>
          ) : (
            <>
              <div className="overflow-x-auto mb-4">
                <table className="min-w-full divide-y divide-gray-200 text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">الاسم</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">البريد</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">الدور</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">الحالة</th>
                      <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">إجراء</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {users.map((u) => (
                      <tr key={u.id}>
                        <td className="px-4 py-2 text-gray-900">{u.full_name}</td>
                        <td className="px-4 py-2 text-gray-700">{u.email}</td>
                        <td className="px-4 py-2 text-gray-700">{u.role}</td>
                        <td className="px-4 py-2">
                          <span
                            className={`px-2 py-1 text-xs rounded ${
                              u.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
                            }`}
                          >
                            {u.is_active ? 'نشط' : 'موقوف'}
                          </span>
                        </td>
                        <td className="px-4 py-2">
                          <button
                            onClick={() => handleToggleActive(u.id, !u.is_active)}
                            className="text-sm text-primary-600 hover:underline"
                          >
                            {u.is_active ? 'إيقاف' : 'تفعيل'}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* إنشاء مستخدم */}
              <form className="grid grid-cols-1 md:grid-cols-2 gap-4" onSubmit={handleCreate}>
                <Input label="الاسم الكامل" value={form.full_name} onChange={(v) => setForm({ ...form, full_name: v })} required />
                <Input label="اسم المستخدم" value={form.username} onChange={(v) => setForm({ ...form, username: v })} required />
                <Input label="البريد" type="email" value={form.email} onChange={(v) => setForm({ ...form, email: v })} required />
                <Input label="كلمة المرور" type="password" value={form.password} onChange={(v) => setForm({ ...form, password: v })} required />
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">الدور</label>
                  <select
                    className="input-field"
                    value={form.role}
                    onChange={(e) => setForm({ ...form, role: e.target.value })}
                  >
                    <option value="owner">Owner</option>
                    <option value="manager">Manager</option>
                    <option value="accountant">Accountant</option>
                    <option value="worker">Worker</option>
                    <option value="viewer">Viewer</option>
                  </select>
                </div>
                <div className="md:col-span-2">
                  <button
                    type="submit"
                    disabled={creating}
                    className="px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700 disabled:opacity-50"
                  >
                    {creating ? '...جارٍ الإنشاء' : 'إنشاء مستخدم'}
                  </button>
                </div>
              </form>
            </>
          )}
        </Card>
      </div>
    </Layout>
  )
}

function ReadOnly({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      <input type="text" value={value} disabled className="input-field bg-gray-50" />
    </div>
  )
}

function Input({
  label,
  value,
  onChange,
  type = 'text',
  required = false,
}: {
  label: string
  value: string
  onChange: (val: string) => void
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
        required={required}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  )
}

