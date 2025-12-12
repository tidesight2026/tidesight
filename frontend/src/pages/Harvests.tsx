import { useEffect, useState } from 'react'
import Layout from '../components/layout/Layout'
import Card from '../components/common/Card'
import SearchInput from '../components/common/SearchInput'
import Modal from '../components/common/Modal'
import { apiService } from '../services/api'
import type { Harvest, Batch } from '../types'
import LoadingSpinner from '../components/common/LoadingSpinner'
import EmptyState from '../components/common/EmptyState'
import { useToast } from '../hooks/useToast'

export default function Harvests() {
  const [harvests, setHarvests] = useState<Harvest[]>([])
  const [batches, setBatches] = useState<Batch[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedBatch, setSelectedBatch] = useState<number | ''>('')
  const [selectedStatus, setSelectedStatus] = useState<string>('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedHarvest, setSelectedHarvest] = useState<Harvest | null>(null)
  const [formData, setFormData] = useState({
    batch_id: '',
    harvest_date: new Date().toISOString().split('T')[0],
    quantity_kg: '',
    count: '',
    average_weight: '',
    fair_value: '',
    cost_per_kg: '',
    status: 'pending' as const,
    notes: '',
  })
  const [submitting, setSubmitting] = useState(false)
  const { showToast } = useToast()

  useEffect(() => {
    fetchHarvests()
    fetchBatches()
  }, [selectedBatch, selectedStatus])

  const fetchHarvests = async () => {
    try {
      setLoading(true)
      const params: any = {}
      if (selectedBatch) params.batch_id = selectedBatch
      if (selectedStatus) params.status = selectedStatus
      const data = await apiService.getHarvests(params)
      setHarvests(data)
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'خطأ في جلب الحصاد', 'error')
    } finally {
      setLoading(false)
    }
  }

  const fetchBatches = async () => {
    try {
      const data = await apiService.getBatches()
      setBatches(data.filter((b) => b.status === 'active'))
    } catch (err) {
      console.error('Error fetching batches:', err)
    }
  }

  const filteredHarvests = harvests.filter(
    (h) =>
      h.batch_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
      h.harvest_date.includes(searchQuery)
  )

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      setSubmitting(true)
      const payload = {
        batch_id: parseInt(formData.batch_id),
        harvest_date: formData.harvest_date,
        quantity_kg: parseFloat(formData.quantity_kg),
        count: parseInt(formData.count),
        average_weight: formData.average_weight ? parseFloat(formData.average_weight) : undefined,
        fair_value: formData.fair_value ? parseFloat(formData.fair_value) : undefined,
        cost_per_kg: formData.cost_per_kg ? parseFloat(formData.cost_per_kg) : undefined,
        status: formData.status,
        notes: formData.notes || undefined,
      }
      await apiService.createHarvest(payload)
      showToast('تم إنشاء الحصاد بنجاح', 'success')
      setIsModalOpen(false)
      resetForm()
      fetchHarvests()
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'خطأ في إنشاء الحصاد', 'error')
    } finally {
      setSubmitting(false)
    }
  }

  const resetForm = () => {
    setFormData({
      batch_id: '',
      harvest_date: new Date().toISOString().split('T')[0],
      quantity_kg: '',
      count: '',
      average_weight: '',
      fair_value: '',
      cost_per_kg: '',
      status: 'pending',
      notes: '',
    })
    setSelectedHarvest(null)
  }

  const getStatusBadge = (status: string) => {
    const badges: Record<string, { text: string; className: string }> = {
      pending: { text: 'قيد الانتظار', className: 'bg-yellow-100 text-yellow-800' },
      in_progress: { text: 'قيد التنفيذ', className: 'bg-blue-100 text-blue-800' },
      completed: { text: 'مكتمل', className: 'bg-green-100 text-green-800' },
      cancelled: { text: 'ملغي', className: 'bg-red-100 text-red-800' },
    }
    const badge = badges[status] || badges.pending
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded ${badge.className}`}>
        {badge.text}
      </span>
    )
  }

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">الحصاد</h1>
            <p className="mt-2 text-gray-600">إدارة حصاد الأسماك وتحويلها إلى مخزون تام</p>
          </div>
          <button onClick={() => setIsModalOpen(true)} className="btn-primary">
            + إضافة حصاد
          </button>
        </div>

        <Card>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <SearchInput value={searchQuery} onChange={setSearchQuery} placeholder="ابحث..." />
            <select
              value={selectedBatch}
              onChange={(e) => setSelectedBatch(e.target.value ? parseInt(e.target.value) : '')}
              className="input-field"
            >
              <option value="">جميع الدفعات</option>
              {batches.map((batch) => (
                <option key={batch.id} value={batch.id}>
                  {batch.batch_number}
                </option>
              ))}
            </select>
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="input-field"
            >
              <option value="">جميع الحالات</option>
              <option value="pending">قيد الانتظار</option>
              <option value="in_progress">قيد التنفيذ</option>
              <option value="completed">مكتمل</option>
              <option value="cancelled">ملغي</option>
            </select>
          </div>
        </Card>

        {loading ? (
          <div className="flex justify-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        ) : filteredHarvests.length === 0 ? (
          <Card>
            <EmptyState
              icon="🌾"
              title="لا يوجد حصاد"
              description="ابدأ بإضافة حصاد جديد"
            />
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredHarvests.map((harvest) => (
              <Card key={harvest.id} className="hover:shadow-lg transition-shadow">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h3 className="font-semibold text-gray-900">{harvest.batch_number}</h3>
                    <p className="text-sm text-gray-500">
                      {new Date(harvest.harvest_date).toLocaleDateString('ar-SA')}
                    </p>
                  </div>
                  {getStatusBadge(harvest.status)}
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">الكمية:</span>
                    <span className="font-medium">{harvest.quantity_kg} كجم</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">العدد:</span>
                    <span className="font-medium">{harvest.count} سمكة</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">متوسط الوزن:</span>
                    <span className="font-medium">{harvest.average_weight.toFixed(3)} كجم</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">القيمة العادلة:</span>
                    <span className="font-medium text-green-600">
                      {harvest.fair_value.toFixed(2)} ريال
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">التكلفة/كجم:</span>
                    <span className="font-medium">{harvest.cost_per_kg.toFixed(2)} ريال</span>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}

        {/* Create/Edit Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={() => {
            setIsModalOpen(false)
            resetForm()
          }}
          title={selectedHarvest ? 'تعديل الحصاد' : 'إضافة حصاد جديد'}
        >
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                الدفعة <span className="text-red-500">*</span>
              </label>
              <select
                required
                value={formData.batch_id}
                onChange={(e) => setFormData({ ...formData, batch_id: e.target.value })}
                className="input-field"
              >
                <option value="">اختر الدفعة</option>
                {batches.map((batch) => (
                  <option key={batch.id} value={batch.id}>
                    {batch.batch_number} - {batch.species?.arabic_name || 'غير محدد'}
                  </option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  تاريخ الحصاد <span className="text-red-500">*</span>
                </label>
                <input
                  type="date"
                  required
                  value={formData.harvest_date}
                  onChange={(e) => setFormData({ ...formData, harvest_date: e.target.value })}
                  className="input-field"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  الحالة <span className="text-red-500">*</span>
                </label>
                <select
                  required
                  value={formData.status}
                  onChange={(e) =>
                    setFormData({ ...formData, status: e.target.value as any })
                  }
                  className="input-field"
                >
                  <option value="pending">قيد الانتظار</option>
                  <option value="in_progress">قيد التنفيذ</option>
                  <option value="completed">مكتمل</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  الكمية (كجم) <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  step="0.01"
                  required
                  value={formData.quantity_kg}
                  onChange={(e) => setFormData({ ...formData, quantity_kg: e.target.value })}
                  className="input-field"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  العدد <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  required
                  value={formData.count}
                  onChange={(e) => setFormData({ ...formData, count: e.target.value })}
                  className="input-field"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  متوسط الوزن (كجم)
                </label>
                <input
                  type="number"
                  step="0.001"
                  value={formData.average_weight}
                  onChange={(e) => setFormData({ ...formData, average_weight: e.target.value })}
                  className="input-field"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  التكلفة/كجم (ريال)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.cost_per_kg}
                  onChange={(e) => setFormData({ ...formData, cost_per_kg: e.target.value })}
                  className="input-field"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                القيمة العادلة (ريال)
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.fair_value}
                onChange={(e) => setFormData({ ...formData, fair_value: e.target.value })}
                className="input-field"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">ملاحظات</label>
              <textarea
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                className="input-field"
                rows={3}
              />
            </div>

            <div className="flex gap-3 justify-end pt-4">
              <button
                type="button"
                onClick={() => {
                  setIsModalOpen(false)
                  resetForm()
                }}
                className="btn-secondary"
              >
                إلغاء
              </button>
              <button type="submit" className="btn-primary" disabled={submitting}>
                {submitting ? 'جاري الحفظ...' : 'حفظ'}
              </button>
            </div>
          </form>
        </Modal>
      </div>
    </Layout>
  )
}

