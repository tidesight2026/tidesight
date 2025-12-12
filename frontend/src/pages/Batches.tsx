import { useEffect, useState, useMemo } from 'react'
import Layout from '../components/layout/Layout'
import Card from '../components/common/Card'
import Modal from '../components/common/Modal'
import ConfirmDialog from '../components/common/ConfirmDialog'
import Toast from '../components/common/Toast'
import SearchInput from '../components/common/SearchInput'
import { useToast } from '../hooks/useToast'
import BatchForm from '../components/batches/BatchForm'
import { apiService } from '../services/api'
import type { Batch } from '../types'
import LoadingSpinner from '../components/common/LoadingSpinner'
import EmptyState from '../components/common/EmptyState'

export default function Batches() {
  const [batches, setBatches] = useState<Batch[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [selectedBatch, setSelectedBatch] = useState<Batch | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { toasts, success, error, removeToast } = useToast()

  // Filtered batches
  const filteredBatches = useMemo(() => {
    return batches.filter((batch) => {
      const matchesSearch =
        batch.batch_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
        batch.species.arabic_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        batch.pond.name.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesStatus = statusFilter === 'all' || batch.status === statusFilter
      return matchesSearch && matchesStatus
    })
  }, [batches, searchQuery, statusFilter])

  useEffect(() => {
    fetchBatches()
  }, [])

  const fetchBatches = async () => {
    try {
      setLoading(true)
      const data = await apiService.getBatches()
      setBatches(data)
    } catch (err) {
      error('فشل في جلب البيانات')
    } finally {
      setLoading(false)
    }
  }

  const handleAdd = () => {
    setSelectedBatch(null)
    setIsFormOpen(true)
  }

  const handleEdit = (batch: Batch) => {
    setSelectedBatch(batch)
    setIsFormOpen(true)
  }

  const handleDelete = (batch: Batch) => {
    setSelectedBatch(batch)
    setIsDeleteDialogOpen(true)
  }

  const handleSubmit = async (data: {
    pond_id: number
    species_id: number
    batch_number: string
    start_date: string
    initial_count: number
    initial_weight: number
    initial_cost: number
    notes?: string
  }) => {
    try {
      setIsSubmitting(true)
      if (selectedBatch) {
        // عند التعديل، نحدث فقط الحقول المسموح بتعديلها
        await apiService.updateBatch(selectedBatch.id, {
          current_count: data.initial_count,
          status: 'active',
          notes: data.notes,
        })
        success('تم تحديث الدفعة بنجاح')
      } else {
        await apiService.createBatch(data)
        success('تم إضافة الدفعة بنجاح')
      }
      setIsFormOpen(false)
      setSelectedBatch(null)
      await fetchBatches()
    } catch (err) {
      error(selectedBatch ? 'فشل في تحديث الدفعة' : 'فشل في إضافة الدفعة')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleConfirmDelete = async () => {
    if (!selectedBatch) return

    try {
      setIsSubmitting(true)
      await apiService.deleteBatch(selectedBatch.id)
      success('تم إنهاء الدفعة بنجاح')
      setIsDeleteDialogOpen(false)
      setSelectedBatch(null)
      await fetchBatches()
    } catch (err) {
      error('فشل في إنهاء الدفعة')
    } finally {
      setIsSubmitting(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-700 border-green-300'
      case 'harvested':
        return 'bg-blue-100 text-blue-700 border-blue-300'
      case 'terminated':
        return 'bg-red-100 text-red-700 border-red-300'
      default:
        return 'bg-gray-100 text-gray-700 border-gray-300'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active':
        return 'نشط'
      case 'harvested':
        return 'محصود'
      case 'terminated':
        return 'منتهي'
      default:
        return status
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return '🟢'
      case 'harvested':
        return '🔵'
      case 'terminated':
        return '🔴'
      default:
        return '⚪'
    }
  }

  // تحديد ما إذا كانت الدفعة قريبة من الحصاد
  const isNearHarvest = (batch: Batch) => {
    if (batch.status !== 'active') return false
    // يمكن إضافة منطق أكثر تعقيداً هنا
    // مثلاً: إذا كان متوسط الوزن أكبر من حد معين
    return false // مؤقتاً
  }

  return (
    <Layout>
      {/* Toast Container */}
      {toasts.map((toast) => (
        <Toast
          key={toast.id}
          message={toast.message}
          type={toast.type}
          onClose={() => removeToast(toast.id)}
        />
      ))}

      {/* Add/Edit Modal */}
      <Modal
        isOpen={isFormOpen}
        onClose={() => {
          setIsFormOpen(false)
          setSelectedBatch(null)
        }}
        title={selectedBatch ? 'تعديل دفعة' : 'إضافة دفعة جديدة'}
        size="lg"
      >
        <BatchForm
          batch={selectedBatch}
          onSubmit={handleSubmit}
          onCancel={() => {
            setIsFormOpen(false)
            setSelectedBatch(null)
          }}
          isLoading={isSubmitting}
        />
      </Modal>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={isDeleteDialogOpen}
        onClose={() => {
          setIsDeleteDialogOpen(false)
          setSelectedBatch(null)
        }}
        onConfirm={handleConfirmDelete}
        title="إنهاء الدفعة"
        message={`هل أنت متأكد من إنهاء الدفعة "${selectedBatch?.batch_number}"؟ هذا الإجراء سيغير حالة الدفعة إلى "منتهي".`}
        confirmText="إنهاء"
        cancelText="إلغاء"
        variant="warning"
      />

      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">الدفعات</h1>
            <p className="mt-2 text-gray-600">إدارة دفعات السمك</p>
          </div>
          <button onClick={handleAdd} className="btn-primary">
            ➕ إضافة دفعة جديدة
          </button>
        </div>

        {/* Search & Filter */}
        <Card>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <SearchInput
              value={searchQuery}
              onChange={setSearchQuery}
              placeholder="ابحث عن دفعة..."
            />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="input-field"
            >
              <option value="all">جميع الحالات</option>
              <option value="active">نشط</option>
              <option value="harvested">محصود</option>
              <option value="terminated">منتهي</option>
            </select>
          </div>
          {filteredBatches.length !== batches.length && (
            <p className="text-sm text-gray-500 mt-2">
              عرض {filteredBatches.length} من {batches.length} دفعة
            </p>
          )}
        </Card>

        {loading ? (
          <div className="flex justify-center py-12">
            <LoadingSpinner />
          </div>
        ) : filteredBatches.length === 0 ? (
          <Card>
            <EmptyState
              icon="📦"
              title={searchQuery || statusFilter !== 'all' ? 'لا توجد نتائج' : 'لا توجد دفعات بعد'}
              description={
                searchQuery || statusFilter !== 'all'
                  ? 'جرب تغيير البحث أو الفلتر'
                  : 'ابدأ بإضافة دفعة جديدة لإدارة الإنتاج'
              }
              action={
                !searchQuery && statusFilter === 'all' && (
                  <button onClick={handleAdd} className="btn-primary">
                    إضافة دفعة جديدة
                  </button>
                )
              }
            />
          </Card>
        ) : (
          <div className="space-y-4">
            {filteredBatches.map((batch) => (
              <Card key={batch.id} className="hover:shadow-lg transition-shadow">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                  <div>
                    <p className="text-sm text-gray-500 mb-1">رقم الدفعة</p>
                    <p className="font-semibold text-gray-900">{batch.batch_number}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500 mb-1">النوع السمكي</p>
                    <p className="font-semibold text-gray-900">{batch.species.arabic_name}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500 mb-1">الحوض</p>
                    <p className="font-semibold text-gray-900">{batch.pond.name}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500 mb-1">الحالة</p>
                    <div className="flex gap-2 flex-wrap">
                      <span
                        className={`inline-flex items-center gap-1 px-3 py-1 text-xs font-medium rounded-full border ${getStatusColor(batch.status)}`}
                      >
                        {getStatusIcon(batch.status)} {getStatusText(batch.status)}
                      </span>
                      {isNearHarvest(batch) && (
                        <span className="inline-flex items-center gap-1 px-3 py-1 text-xs font-medium rounded-full border bg-yellow-100 text-yellow-700 border-yellow-300">
                          ⚠️ قريبة من الحصاد
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="pt-4 border-t border-gray-200 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <p className="text-gray-500">العدد الأولي</p>
                    <p className="font-medium">{batch.initial_count.toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">العدد الحالي</p>
                    <p className="font-medium text-primary-600">
                      {batch.current_count.toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-500">الوزن الأولي</p>
                    <p className="font-medium">{batch.initial_weight} كجم</p>
                  </div>
                  <div>
                    <p className="text-gray-500">تاريخ البدء</p>
                    <p className="font-medium">
                      {new Date(batch.start_date).toLocaleDateString('ar-SA')}
                    </p>
                  </div>
                </div>

                {batch.notes && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <p className="text-sm text-gray-500 mb-1">ملاحظات</p>
                    <p className="text-sm text-gray-700">{batch.notes}</p>
                  </div>
                )}

                <div className="flex gap-2 mt-4 pt-4 border-t border-gray-200">
                  <button
                    onClick={() => handleEdit(batch)}
                    className="flex-1 btn-secondary text-sm py-2"
                    disabled={batch.status !== 'active'}
                  >
                    تعديل
                  </button>
                  <button
                    onClick={() => handleDelete(batch)}
                    className="flex-1 bg-red-50 hover:bg-red-100 text-red-700 text-sm py-2 rounded-lg transition-colors"
                    disabled={batch.status === 'terminated' || isSubmitting}
                  >
                    {batch.status === 'terminated' ? 'منتهي' : 'إنهاء'}
                  </button>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </Layout>
  )
}
