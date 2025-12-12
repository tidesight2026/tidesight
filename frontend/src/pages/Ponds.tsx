import { useEffect, useState, useMemo } from 'react'
import Layout from '../components/layout/Layout'
import Card from '../components/common/Card'
import Modal from '../components/common/Modal'
import ConfirmDialog from '../components/common/ConfirmDialog'
import Toast from '../components/common/Toast'
import SearchInput from '../components/common/SearchInput'
import { useToast } from '../hooks/useToast'
import PondForm from '../components/ponds/PondForm'
import { apiService } from '../services/api'
import type { Pond } from '../types'
import LoadingSpinner from '../components/common/LoadingSpinner'
import EmptyState from '../components/common/EmptyState'

export default function Ponds() {
  const [ponds, setPonds] = useState<Pond[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [selectedPond, setSelectedPond] = useState<Pond | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { toasts, success, error, removeToast } = useToast()

  // Filtered ponds
  const filteredPonds = useMemo(() => {
    return ponds.filter((pond) => {
      const matchesSearch =
        pond.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (pond.location && pond.location.toLowerCase().includes(searchQuery.toLowerCase()))
      const matchesStatus = statusFilter === 'all' || pond.status === statusFilter
      return matchesSearch && matchesStatus
    })
  }, [ponds, searchQuery, statusFilter])

  useEffect(() => {
    fetchPonds()
  }, [])

  const fetchPonds = async () => {
    try {
      setLoading(true)
      const data = await apiService.getPonds()
      setPonds(data)
    } catch (err) {
      error('فشل في جلب البيانات')
    } finally {
      setLoading(false)
    }
  }

  const handleAdd = () => {
    setSelectedPond(null)
    setIsFormOpen(true)
  }

  const handleEdit = (pond: Pond) => {
    setSelectedPond(pond)
    setIsFormOpen(true)
  }

  const handleDelete = (pond: Pond) => {
    setSelectedPond(pond)
    setIsDeleteDialogOpen(true)
  }

  const handleSubmit = async (data: Partial<Pond>) => {
    try {
      setIsSubmitting(true)
      if (selectedPond) {
        await apiService.updatePond(selectedPond.id, data)
        success('تم تحديث الحوض بنجاح')
      } else {
        await apiService.createPond(data)
        success('تم إضافة الحوض بنجاح')
      }
      setIsFormOpen(false)
      setSelectedPond(null)
      await fetchPonds()
    } catch (err) {
      error(selectedPond ? 'فشل في تحديث الحوض' : 'فشل في إضافة الحوض')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleConfirmDelete = async () => {
    if (!selectedPond) return

    try {
      setIsSubmitting(true)
      await apiService.deletePond(selectedPond.id)
      success('تم حذف الحوض بنجاح')
      setIsDeleteDialogOpen(false)
      setSelectedPond(null)
      await fetchPonds()
    } catch (err) {
      error('فشل في حذف الحوض')
    } finally {
      setIsSubmitting(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-700'
      case 'maintenance':
        return 'bg-yellow-100 text-yellow-700'
      case 'empty':
        return 'bg-gray-100 text-gray-700'
      default:
        return 'bg-gray-100 text-gray-700'
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'concrete':
        return '🧱'
      case 'earth':
        return '🌾'
      case 'fiberglass':
        return '🏊'
      case 'cage':
        return '🐟'
      default:
        return '🐟'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active':
        return 'نشط'
      case 'maintenance':
        return 'صيانة'
      case 'empty':
        return 'فارغ'
      case 'inactive':
        return 'غير نشط'
      default:
        return status
    }
  }

  const getTypeText = (type: string) => {
    switch (type) {
      case 'concrete':
        return 'خرسانة'
      case 'earth':
        return 'ترابي'
      case 'fiberglass':
        return 'فيبرجلاس'
      case 'cage':
        return 'قفص'
      default:
        return type
    }
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
          setSelectedPond(null)
        }}
        title={selectedPond ? 'تعديل حوض' : 'إضافة حوض جديد'}
        size="md"
      >
        <PondForm
          pond={selectedPond}
          onSubmit={handleSubmit}
          onCancel={() => {
            setIsFormOpen(false)
            setSelectedPond(null)
          }}
          isLoading={isSubmitting}
        />
      </Modal>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={isDeleteDialogOpen}
        onClose={() => {
          setIsDeleteDialogOpen(false)
          setSelectedPond(null)
        }}
        onConfirm={handleConfirmDelete}
        title="تأكيد الحذف"
        message={`هل أنت متأكد من حذف الحوض "${selectedPond?.name}"؟ هذا الإجراء لا يمكن التراجع عنه.`}
        confirmText="حذف"
        cancelText="إلغاء"
        variant="danger"
      />

      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">الأحواض</h1>
            <p className="mt-2 text-gray-600">إدارة أحواض المزرعة</p>
          </div>
          <button onClick={handleAdd} className="btn-primary">
            ➕ إضافة حوض جديد
          </button>
        </div>

        {/* Search & Filter */}
        <Card>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <SearchInput
              value={searchQuery}
              onChange={setSearchQuery}
              placeholder="ابحث عن حوض..."
            />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="input-field"
            >
              <option value="all">جميع الحالات</option>
              <option value="active">نشط</option>
              <option value="empty">فارغ</option>
              <option value="maintenance">صيانة</option>
              <option value="inactive">غير نشط</option>
            </select>
          </div>
          {filteredPonds.length !== ponds.length && (
            <p className="text-sm text-gray-500 mt-2">
              عرض {filteredPonds.length} من {ponds.length} حوض
            </p>
          )}
        </Card>

        {loading ? (
          <div className="flex justify-center py-12">
            <LoadingSpinner />
          </div>
        ) : filteredPonds.length === 0 ? (
          <Card>
            <EmptyState
              icon="🐟"
              title={searchQuery || statusFilter !== 'all' ? 'لا توجد نتائج' : 'لا توجد أحواض بعد'}
              description={
                searchQuery || statusFilter !== 'all'
                  ? 'جرب تغيير البحث أو الفلتر'
                  : 'ابدأ بإضافة حوض جديد لإدارة المزرعة'
              }
              action={
                !searchQuery && statusFilter === 'all' && (
                  <button onClick={handleAdd} className="btn-primary">
                    إضافة حوض جديد
                  </button>
                )
              }
            />
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredPonds.map((pond) => (
              <Card key={pond.id} className="hover:shadow-lg transition-shadow">
                <div className="space-y-3">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-2xl">{getTypeIcon(pond.pond_type)}</span>
                      <h3 className="text-lg font-semibold text-gray-900">{pond.name}</h3>
                    </div>
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(pond.status)}`}
                    >
                      {getStatusText(pond.status)}
                    </span>
                  </div>

                  <div className="space-y-2 text-sm text-gray-600">
                    <div className="flex justify-between">
                      <span>السعة:</span>
                      <span className="font-medium">{pond.capacity} م³</span>
                    </div>
                    {pond.location && (
                      <div className="flex justify-between">
                        <span>الموقع:</span>
                        <span className="font-medium">{pond.location}</span>
                      </div>
                    )}
                    <div className="flex justify-between">
                      <span>النوع:</span>
                      <span className="font-medium">{getTypeText(pond.pond_type)}</span>
                    </div>
                  </div>

                  <div className="flex gap-2 pt-3 border-t border-gray-200">
                    <button
                      onClick={() => handleEdit(pond)}
                      className="flex-1 btn-secondary text-sm py-2"
                    >
                      تعديل
                    </button>
                    <button
                      onClick={() => handleDelete(pond)}
                      className="flex-1 bg-red-50 hover:bg-red-100 text-red-700 text-sm py-2 rounded-lg transition-colors"
                    >
                      حذف
                    </button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </Layout>
  )
}
