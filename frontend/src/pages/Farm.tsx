import { useEffect, useState } from 'react'
import Layout from '../components/layout/Layout'
import Card from '../components/common/Card'
import { apiService } from '../services/api'
import type { FarmInfo } from '../types'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { useToast } from '../hooks/useToast'

export default function Farm() {
  const [info, setInfo] = useState<FarmInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)
  const { showToast } = useToast()

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      setError(null)
      try {
        const data = await apiService.getFarmInfo()
        setInfo(data)
      } catch (err: any) {
        setError(err.response?.data?.detail || 'فشل تحميل معلومات المزرعة')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const handleSave = async () => {
    if (!info) return
    setSaving(true)
    setError(null)
    try {
      const updated = await apiService.updateFarmInfo(info)
      setInfo(updated)
      showToast('تم حفظ معلومات المزرعة', 'success')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'فشل الحفظ')
      showToast(err.response?.data?.detail || 'فشل الحفظ', 'error')
    } finally {
      setSaving(false)
    }
  }

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">المزرعة</h1>
          <p className="mt-2 text-gray-600">إدارة معلومات المزرعة</p>
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
          info && (
            <Card title="معلومات المزرعة">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input label="اسم المزرعة" value={info.farm_name} onChange={(v) => setInfo({ ...info, farm_name: v })} />
                <Input
                  label="البريد"
                  value={info.contact_email || ''}
                  onChange={(v) => setInfo({ ...info, contact_email: v })}
                  type="email"
                />
                <Input label="الهاتف" value={info.phone || ''} onChange={(v) => setInfo({ ...info, phone: v })} />
                <Input label="السجل التجاري" value={info.trade_number || ''} onChange={(v) => setInfo({ ...info, trade_number: v })} />
                <Input label="العملة" value={info.currency || ''} onChange={(v) => setInfo({ ...info, currency: v })} />
                <Input label="المنطقة الزمنية" value={info.timezone || ''} onChange={(v) => setInfo({ ...info, timezone: v })} />
                <Input label="رابط الشعار" value={info.logo_url || ''} onChange={(v) => setInfo({ ...info, logo_url: v })} />
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">العنوان</label>
                  <textarea
                    className="input-field"
                    rows={3}
                    value={info.address || ''}
                    onChange={(e) => setInfo({ ...info, address: e.target.value })}
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">ملاحظات</label>
                  <textarea
                    className="input-field"
                    rows={3}
                    value={info.notes || ''}
                    onChange={(e) => setInfo({ ...info, notes: e.target.value })}
                  />
                </div>
                <div className="md:col-span-2">
                  <button
                    onClick={handleSave}
                    disabled={saving}
                    className="px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700 disabled:opacity-50"
                  >
                    {saving ? '...جاري الحفظ' : 'حفظ'}
                  </button>
                </div>
              </div>
            </Card>
          )
        )}
      </div>
    </Layout>
  )
}

function Input({
  label,
  value,
  onChange,
  type = 'text',
}: {
  label: string
  value: string
  onChange: (val: string) => void
  type?: string
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      <input type={type} className="input-field" value={value} onChange={(e) => onChange(e.target.value)} />
    </div>
  )
}

