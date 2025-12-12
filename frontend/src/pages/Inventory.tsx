import { useEffect, useState, useMemo } from 'react'
import Layout from '../components/layout/Layout'
import Card from '../components/common/Card'
import Modal from '../components/common/Modal'
import ConfirmDialog from '../components/common/ConfirmDialog'
import Toast from '../components/common/Toast'
import SearchInput from '../components/common/SearchInput'
import { useToast } from '../hooks/useToast'
import FeedInventoryForm from '../components/inventory/FeedInventoryForm'
import MedicineInventoryForm from '../components/inventory/MedicineInventoryForm'
import { apiService } from '../services/api'
import type { FeedInventory, MedicineInventory } from '../types'
import LoadingSpinner from '../components/common/LoadingSpinner'
import EmptyState from '../components/common/EmptyState'

export default function Inventory() {
  const [feedInventory, setFeedInventory] = useState<FeedInventory[]>([])
  const [medicineInventory, setMedicineInventory] = useState<MedicineInventory[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'feeds' | 'medicines'>('feeds')
  const [searchQuery, setSearchQuery] = useState('')

  // Feed Inventory State
  const [isFeedFormOpen, setIsFeedFormOpen] = useState(false)
  const [isFeedDeleteDialogOpen, setIsFeedDeleteDialogOpen] = useState(false)
  const [selectedFeedItem, setSelectedFeedItem] = useState<FeedInventory | null>(null)
  const [isFeedSubmitting, setIsFeedSubmitting] = useState(false)

  // Medicine Inventory State
  const [isMedicineFormOpen, setIsMedicineFormOpen] = useState(false)
  const [isMedicineDeleteDialogOpen, setIsMedicineDeleteDialogOpen] = useState(false)
  const [selectedMedicineItem, setSelectedMedicineItem] = useState<MedicineInventory | null>(null)
  const [isMedicineSubmitting, setIsMedicineSubmitting] = useState(false)

  const { toasts, success, error, removeToast } = useToast()

  useEffect(() => {
    fetchInventory()
  }, [])

  const fetchInventory = async () => {
    try {
      setLoading(true)
      const [feeds, medicines] = await Promise.all([
        apiService.getFeedInventory(),
        apiService.getMedicineInventory(),
      ])
      setFeedInventory(feeds)
      setMedicineInventory(medicines)
    } catch (err) {
      error('فشل في جلب البيانات')
    } finally {
      setLoading(false)
    }
  }

  // Feed Inventory Handlers
  const handleAddFeed = () => {
    setSelectedFeedItem(null)
    setIsFeedFormOpen(true)
  }

  const handleEditFeed = (item: FeedInventory) => {
    setSelectedFeedItem(item)
    setIsFeedFormOpen(true)
  }

  const handleDeleteFeed = (item: FeedInventory) => {
    setSelectedFeedItem(item)
    setIsFeedDeleteDialogOpen(true)
  }

  const handleFeedSubmit = async (data: {
    feed_type_id: number
    quantity: number
    unit_price: number
    expiry_date?: string
    location?: string
    notes?: string
  }) => {
    try {
      setIsFeedSubmitting(true)
      if (selectedFeedItem) {
        await apiService.updateFeedInventory(selectedFeedItem.id, data)
        success('تم تحديث مخزون العلف بنجاح')
      } else {
        await apiService.createFeedInventory(data)
        success('تم إضافة مخزون العلف بنجاح')
      }
      setIsFeedFormOpen(false)
      setSelectedFeedItem(null)
      await fetchInventory()
    } catch (err) {
      error(selectedFeedItem ? 'فشل في تحديث المخزون' : 'فشل في إضافة المخزون')
    } finally {
      setIsFeedSubmitting(false)
    }
  }

  const handleConfirmFeedDelete = async () => {
    if (!selectedFeedItem) return

    try {
      setIsFeedSubmitting(true)
      await apiService.deleteFeedInventory(selectedFeedItem.id)
      success('تم حذف مخزون العلف بنجاح')
      setIsFeedDeleteDialogOpen(false)
      setSelectedFeedItem(null)
      await fetchInventory()
    } catch (err) {
      error('فشل في حذف المخزون')
    } finally {
      setIsFeedSubmitting(false)
    }
  }

  // Medicine Inventory Handlers
  const handleAddMedicine = () => {
    setSelectedMedicineItem(null)
    setIsMedicineFormOpen(true)
  }

  const handleEditMedicine = (item: MedicineInventory) => {
    setSelectedMedicineItem(item)
    setIsMedicineFormOpen(true)
  }

  const handleDeleteMedicine = (item: MedicineInventory) => {
    setSelectedMedicineItem(item)
    setIsMedicineDeleteDialogOpen(true)
  }

  const handleMedicineSubmit = async (data: {
    medicine_id: number
    quantity: number
    unit_price: number
    expiry_date?: string
    location?: string
    notes?: string
  }) => {
    try {
      setIsMedicineSubmitting(true)
      if (selectedMedicineItem) {
        await apiService.updateMedicineInventory(selectedMedicineItem.id, data)
        success('تم تحديث مخزون الدواء بنجاح')
      } else {
        await apiService.createMedicineInventory(data)
        success('تم إضافة مخزون الدواء بنجاح')
      }
      setIsMedicineFormOpen(false)
      setSelectedMedicineItem(null)
      await fetchInventory()
    } catch (err) {
      error(selectedMedicineItem ? 'فشل في تحديث المخزون' : 'فشل في إضافة المخزون')
    } finally {
      setIsMedicineSubmitting(false)
    }
  }

  const handleConfirmMedicineDelete = async () => {
    if (!selectedMedicineItem) return

    try {
      setIsMedicineSubmitting(true)
      await apiService.deleteMedicineInventory(selectedMedicineItem.id)
      success('تم حذف مخزون الدواء بنجاح')
      setIsMedicineDeleteDialogOpen(false)
      setSelectedMedicineItem(null)
      await fetchInventory()
    } catch (err) {
      error('فشل في حذف المخزون')
    } finally {
      setIsMedicineSubmitting(false)
    }
  }

  // Filtered inventory
  const filteredFeedInventory = useMemo(() => {
    return feedInventory.filter((item) =>
      item.feed_type.arabic_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (item.location && item.location.toLowerCase().includes(searchQuery.toLowerCase()))
    )
  }, [feedInventory, searchQuery])

  const filteredMedicineInventory = useMemo(() => {
    return medicineInventory.filter((item) =>
      item.medicine.arabic_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (item.location && item.location.toLowerCase().includes(searchQuery.toLowerCase()))
    )
  }, [medicineInventory, searchQuery])

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

      {/* Feed Inventory Modal */}
      <Modal
        isOpen={isFeedFormOpen}
        onClose={() => {
          setIsFeedFormOpen(false)
          setSelectedFeedItem(null)
        }}
        title={selectedFeedItem ? 'تعديل مخزون علف' : 'إضافة مخزون علف جديد'}
        size="md"
      >
        <FeedInventoryForm
          item={selectedFeedItem}
          onSubmit={handleFeedSubmit}
          onCancel={() => {
            setIsFeedFormOpen(false)
            setSelectedFeedItem(null)
          }}
          isLoading={isFeedSubmitting}
        />
      </Modal>

      {/* Medicine Inventory Modal */}
      <Modal
        isOpen={isMedicineFormOpen}
        onClose={() => {
          setIsMedicineFormOpen(false)
          setSelectedMedicineItem(null)
        }}
        title={selectedMedicineItem ? 'تعديل مخزون دواء' : 'إضافة مخزون دواء جديد'}
        size="md"
      >
        <MedicineInventoryForm
          item={selectedMedicineItem}
          onSubmit={handleMedicineSubmit}
          onCancel={() => {
            setIsMedicineFormOpen(false)
            setSelectedMedicineItem(null)
          }}
          isLoading={isMedicineSubmitting}
        />
      </Modal>

      {/* Feed Delete Confirmation */}
      <ConfirmDialog
        isOpen={isFeedDeleteDialogOpen}
        onClose={() => {
          setIsFeedDeleteDialogOpen(false)
          setSelectedFeedItem(null)
        }}
        onConfirm={handleConfirmFeedDelete}
        title="تأكيد الحذف"
        message={`هل أنت متأكد من حذف مخزون "${selectedFeedItem?.feed_type.arabic_name}"؟`}
        confirmText="حذف"
        cancelText="إلغاء"
        variant="danger"
      />

      {/* Medicine Delete Confirmation */}
      <ConfirmDialog
        isOpen={isMedicineDeleteDialogOpen}
        onClose={() => {
          setIsMedicineDeleteDialogOpen(false)
          setSelectedMedicineItem(null)
        }}
        onConfirm={handleConfirmMedicineDelete}
        title="تأكيد الحذف"
        message={`هل أنت متأكد من حذف مخزون "${selectedMedicineItem?.medicine.arabic_name}"؟`}
        confirmText="حذف"
        cancelText="إلغاء"
        variant="danger"
      />

      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">المخزون</h1>
            <p className="mt-2 text-gray-600">إدارة مخزون الأعلاف والأدوية</p>
          </div>
          {activeTab === 'feeds' ? (
            <button onClick={handleAddFeed} className="btn-primary">
              ➕ إضافة علف جديد
            </button>
          ) : (
            <button onClick={handleAddMedicine} className="btn-primary">
              ➕ إضافة دواء جديد
            </button>
          )}
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="flex gap-4">
            <button
              onClick={() => {
                setActiveTab('feeds')
                setSearchQuery('')
              }}
              className={`py-2 px-4 font-medium border-b-2 transition-colors ${
                activeTab === 'feeds'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              📋 الأعلاف ({feedInventory.length})
            </button>
            <button
              onClick={() => {
                setActiveTab('medicines')
                setSearchQuery('')
              }}
              className={`py-2 px-4 font-medium border-b-2 transition-colors ${
                activeTab === 'medicines'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              💊 الأدوية ({medicineInventory.length})
            </button>
          </nav>
        </div>

        {/* Search */}
        <Card>
          <SearchInput
            value={searchQuery}
            onChange={setSearchQuery}
            placeholder={activeTab === 'feeds' ? 'ابحث عن علف...' : 'ابحث عن دواء...'}
          />
          {(activeTab === 'feeds' && filteredFeedInventory.length !== feedInventory.length) ||
          (activeTab === 'medicines' && filteredMedicineInventory.length !== medicineInventory.length) ? (
            <p className="text-sm text-gray-500 mt-2">
              عرض{' '}
              {activeTab === 'feeds'
                ? filteredFeedInventory.length
                : filteredMedicineInventory.length}{' '}
              من {activeTab === 'feeds' ? feedInventory.length : medicineInventory.length} عنصر
            </p>
          ) : null}
        </Card>

        {loading ? (
          <div className="flex justify-center py-12">
            <LoadingSpinner />
          </div>
        ) : (
          <>
            {/* Feed Inventory */}
            {activeTab === 'feeds' && (
              <div>
                {filteredFeedInventory.length === 0 ? (
                  <Card>
                    <EmptyState
                      icon="📋"
                      title={searchQuery ? 'لا توجد نتائج' : 'لا يوجد مخزون أعلاف'}
                      description={
                        searchQuery
                          ? 'جرب تغيير البحث'
                          : 'ابدأ بإضافة علف جديد للمخزون'
                      }
                      action={
                        !searchQuery && (
                          <button onClick={handleAddFeed} className="btn-primary">
                            إضافة علف جديد
                          </button>
                        )
                      }
                    />
                  </Card>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {filteredFeedInventory.map((item) => (
                      <Card key={item.id} className="hover:shadow-lg transition-shadow">
                        <div className="space-y-3">
                          <h3 className="font-semibold text-gray-900">{item.feed_type.arabic_name}</h3>
                          <div className="space-y-2 text-sm">
                            <div className="flex justify-between">
                              <span className="text-gray-500">الكمية:</span>
                              <span className="font-medium">
                                {item.quantity} {item.feed_type.unit}
                              </span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-500">سعر الوحدة:</span>
                              <span className="font-medium">{item.unit_price} ريال</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-500">إجمالي القيمة:</span>
                              <span className="font-medium text-primary-600">
                                {(item.quantity * item.unit_price).toFixed(2)} ريال
                              </span>
                            </div>
                            {item.location && (
                              <div className="flex justify-between">
                                <span className="text-gray-500">الموقع:</span>
                                <span className="font-medium">{item.location}</span>
                              </div>
                            )}
                            {item.expiry_date && (
                              <div className="flex justify-between">
                                <span className="text-gray-500">انتهاء الصلاحية:</span>
                                <span
                                  className={`font-medium ${
                                    new Date(item.expiry_date) < new Date()
                                      ? 'text-red-600'
                                      : new Date(item.expiry_date) <
                                        new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)
                                      ? 'text-yellow-600'
                                      : 'text-gray-900'
                                  }`}
                                >
                                  {new Date(item.expiry_date).toLocaleDateString('ar-SA')}
                                </span>
                              </div>
                            )}
                          </div>
                          <div className="flex gap-2 pt-3 border-t border-gray-200">
                            <button
                              onClick={() => handleEditFeed(item)}
                              className="flex-1 btn-secondary text-sm py-2"
                            >
                              تعديل
                            </button>
                            <button
                              onClick={() => handleDeleteFeed(item)}
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
            )}

            {/* Medicine Inventory */}
            {activeTab === 'medicines' && (
              <div>
                {filteredMedicineInventory.length === 0 ? (
                  <Card>
                    <EmptyState
                      icon="💊"
                      title={searchQuery ? 'لا توجد نتائج' : 'لا يوجد مخزون أدوية'}
                      description={
                        searchQuery
                          ? 'جرب تغيير البحث'
                          : 'ابدأ بإضافة دواء جديد للمخزون'
                      }
                      action={
                        !searchQuery && (
                          <button onClick={handleAddMedicine} className="btn-primary">
                            إضافة دواء جديد
                          </button>
                        )
                      }
                    />
                  </Card>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {filteredMedicineInventory.map((item) => (
                      <Card key={item.id} className="hover:shadow-lg transition-shadow">
                        <div className="space-y-3">
                          <h3 className="font-semibold text-gray-900">{item.medicine.arabic_name}</h3>
                          <div className="space-y-2 text-sm">
                            <div className="flex justify-between">
                              <span className="text-gray-500">الكمية:</span>
                              <span className="font-medium">
                                {item.quantity} {item.medicine.unit}
                              </span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-500">سعر الوحدة:</span>
                              <span className="font-medium">{item.unit_price} ريال</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-500">إجمالي القيمة:</span>
                              <span className="font-medium text-primary-600">
                                {(item.quantity * item.unit_price).toFixed(2)} ريال
                              </span>
                            </div>
                            {item.location && (
                              <div className="flex justify-between">
                                <span className="text-gray-500">الموقع:</span>
                                <span className="font-medium">{item.location}</span>
                              </div>
                            )}
                            {item.expiry_date && (
                              <div className="flex justify-between">
                                <span className="text-gray-500">انتهاء الصلاحية:</span>
                                <span
                                  className={`font-medium ${
                                    new Date(item.expiry_date) < new Date()
                                      ? 'text-red-600'
                                      : new Date(item.expiry_date) <
                                        new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)
                                      ? 'text-yellow-600'
                                      : 'text-gray-900'
                                  }`}
                                >
                                  {new Date(item.expiry_date).toLocaleDateString('ar-SA')}
                                </span>
                              </div>
                            )}
                          </div>
                          <div className="flex gap-2 pt-3 border-t border-gray-200">
                            <button
                              onClick={() => handleEditMedicine(item)}
                              className="flex-1 btn-secondary text-sm py-2"
                            >
                              تعديل
                            </button>
                            <button
                              onClick={() => handleDeleteMedicine(item)}
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
            )}
          </>
        )}
      </div>
    </Layout>
  )
}
