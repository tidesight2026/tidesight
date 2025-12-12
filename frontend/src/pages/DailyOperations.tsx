import { useEffect, useState, useMemo } from 'react'
import Layout from '../components/layout/Layout'
import Card from '../components/common/Card'
import Modal from '../components/common/Modal'
import ConfirmDialog from '../components/common/ConfirmDialog'
import Toast from '../components/common/Toast'
import SearchInput from '../components/common/SearchInput'
import { useToast } from '../hooks/useToast'
import FeedingLogForm from '../components/operations/FeedingLogForm'
import MortalityLogForm from '../components/operations/MortalityLogForm'
import { apiService } from '../services/api'
import type { FeedingLog, MortalityLog, Batch, FeedType, BatchStatistics } from '../types'
import LoadingSpinner from '../components/common/LoadingSpinner'
import EmptyState from '../components/common/EmptyState'

export default function DailyOperations() {
  const [feedingLogs, setFeedingLogs] = useState<FeedingLog[]>([])
  const [mortalityLogs, setMortalityLogs] = useState<MortalityLog[]>([])
  const [batches, setBatches] = useState<Batch[]>([])
  const [feedTypes, setFeedTypes] = useState<FeedType[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'feeding' | 'mortality' | 'stats'>('feeding')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedBatchId, setSelectedBatchId] = useState<number | null>(null)

  // Forms State
  const [isFeedingFormOpen, setIsFeedingFormOpen] = useState(false)
  const [selectedFeedingLog, setSelectedFeedingLog] = useState<FeedingLog | null>(null)
  const [isFeedingSubmitting, setIsFeedingSubmitting] = useState(false)

  const [isMortalityFormOpen, setIsMortalityFormOpen] = useState(false)
  const [selectedMortalityLog, setSelectedMortalityLog] = useState<MortalityLog | null>(null)
  const [isMortalitySubmitting, setIsMortalitySubmitting] = useState(false)

  // Delete Dialogs
  const [isFeedingDeleteDialogOpen, setIsFeedingDeleteDialogOpen] = useState(false)
  const [isMortalityDeleteDialogOpen, setIsMortalityDeleteDialogOpen] = useState(false)

  // Statistics
  const [selectedBatchStats, setSelectedBatchStats] = useState<BatchStatistics | null>(null)
  const [loadingStats, setLoadingStats] = useState(false)

  const { toasts, success, error, removeToast } = useToast()

  useEffect(() => {
    fetchData()
  }, [selectedBatchId])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [feeds, mortalities, batchesData, feedTypesData] = await Promise.all([
        apiService.getFeedingLogs(selectedBatchId || undefined),
        apiService.getMortalityLogs(selectedBatchId || undefined),
        apiService.getBatches(),
        apiService.getFeedTypes(),
      ])
      setFeedingLogs(feeds)
      setMortalityLogs(mortalities)
      setBatches(batchesData)
      setFeedTypes(feedTypesData)
    } catch (err) {
      console.error('Error fetching data:', err)
      error('فشل في جلب البيانات')
    } finally {
      setLoading(false)
    }
  }

  // Filtered logs
  const filteredFeedingLogs = useMemo(() => {
    return feedingLogs.filter((log) =>
      log.batch_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.feed_type_name.toLowerCase().includes(searchQuery.toLowerCase())
    )
  }, [feedingLogs, searchQuery])

  const filteredMortalityLogs = useMemo(() => {
    return mortalityLogs.filter((log) =>
      log.batch_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (log.cause && log.cause.toLowerCase().includes(searchQuery.toLowerCase()))
    )
  }, [mortalityLogs, searchQuery])

  // Feeding Log Handlers
  const handleAddFeeding = () => {
    setSelectedFeedingLog(null)
    setIsFeedingFormOpen(true)
  }

  const handleEditFeeding = (log: FeedingLog) => {
    setSelectedFeedingLog(log)
    setIsFeedingFormOpen(true)
  }

  const handleDeleteFeeding = (log: FeedingLog) => {
    setSelectedFeedingLog(log)
    setIsFeedingDeleteDialogOpen(true)
  }

  const handleFeedingSubmit = async (data: Partial<FeedingLog>) => {
    try {
      setIsFeedingSubmitting(true)
      if (selectedFeedingLog) {
        await apiService.updateFeedingLog(selectedFeedingLog.id, data)
        success('تم تحديث سجل التغذية بنجاح')
      } else {
        await apiService.createFeedingLog(data as any)
        success('تم إضافة سجل التغذية بنجاح')
      }
      setIsFeedingFormOpen(false)
      setSelectedFeedingLog(null)
      await fetchData()
    } catch (err) {
      console.error('Error submitting feeding log:', err)
      error(selectedFeedingLog ? 'فشل في تحديث سجل التغذية' : 'فشل في إضافة سجل التغذية')
    } finally {
      setIsFeedingSubmitting(false)
    }
  }

  const handleConfirmFeedingDelete = async () => {
    if (!selectedFeedingLog) return
    try {
      setIsFeedingSubmitting(true)
      await apiService.deleteFeedingLog(selectedFeedingLog.id)
      success('تم حذف سجل التغذية بنجاح')
      setIsFeedingDeleteDialogOpen(false)
      setSelectedFeedingLog(null)
      await fetchData()
    } catch (err) {
      error('فشل في حذف سجل التغذية')
    } finally {
      setIsFeedingSubmitting(false)
    }
  }

  // Mortality Log Handlers
  const handleAddMortality = () => {
    setSelectedMortalityLog(null)
    setIsMortalityFormOpen(true)
  }

  const handleEditMortality = (log: MortalityLog) => {
    setSelectedMortalityLog(log)
    setIsMortalityFormOpen(true)
  }

  const handleDeleteMortality = (log: MortalityLog) => {
    setSelectedMortalityLog(log)
    setIsMortalityDeleteDialogOpen(true)
  }

  const handleMortalitySubmit = async (data: Partial<MortalityLog>) => {
    try {
      setIsMortalitySubmitting(true)
      if (selectedMortalityLog) {
        await apiService.updateMortalityLog(selectedMortalityLog.id, data)
        success('تم تحديث سجل النفوق بنجاح')
      } else {
        await apiService.createMortalityLog(data as any)
        success('تم إضافة سجل النفوق بنجاح')
      }
      setIsMortalityFormOpen(false)
      setSelectedMortalityLog(null)
      await fetchData()
    } catch (err) {
      console.error('Error submitting mortality log:', err)
      error(selectedMortalityLog ? 'فشل في تحديث سجل النفوق' : 'فشل في إضافة سجل النفوق')
    } finally {
      setIsMortalitySubmitting(false)
    }
  }

  const handleConfirmMortalityDelete = async () => {
    if (!selectedMortalityLog) return
    try {
      setIsMortalitySubmitting(true)
      await apiService.deleteMortalityLog(selectedMortalityLog.id)
      success('تم حذف سجل النفوق بنجاح')
      setIsMortalityDeleteDialogOpen(false)
      setSelectedMortalityLog(null)
      await fetchData()
    } catch (err) {
      error('فشل في حذف سجل النفوق')
    } finally {
      setIsMortalitySubmitting(false)
    }
  }

  // Statistics Handler
  const handleViewStats = async (batchId: number) => {
    try {
      setLoadingStats(true)
      const stats = await apiService.getBatchStatistics(batchId)
      setSelectedBatchStats(stats)
      setActiveTab('stats')
    } catch (err) {
      error('فشل في جلب الإحصائيات')
    } finally {
      setLoadingStats(false)
    }
  }

  const activeBatches = batches.filter((b) => b.status === 'active')

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">العمليات اليومية</h1>
            <p className="mt-2 text-gray-600">تسجيل التغذية والنفوق اليومية</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleAddFeeding}
              className="btn-primary"
              style={{ display: activeTab === 'feeding' ? 'block' : 'none' }}
            >
              ➕ إضافة تغذية
            </button>
            <button
              onClick={handleAddMortality}
              className="btn-primary"
              style={{ display: activeTab === 'mortality' ? 'block' : 'none' }}
            >
              ➕ إضافة نفوق
            </button>
          </div>
        </div>

        {/* Filter by Batch */}
        <Card>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">فلترة حسب الدفعة</label>
              <select
                value={selectedBatchId || ''}
                onChange={(e) => setSelectedBatchId(e.target.value ? Number(e.target.value) : null)}
                className="input-field"
              >
                <option value="">جميع الدفعات</option>
                {activeBatches.map((batch) => (
                  <option key={batch.id} value={batch.id}>
                    {batch.batch_number} - {batch.species.arabic_name}
                  </option>
                ))}
              </select>
            </div>
            <SearchInput
              value={searchQuery}
              onChange={setSearchQuery}
              placeholder="ابحث في السجلات..."
            />
          </div>
        </Card>

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="flex gap-4">
            <button
              onClick={() => setActiveTab('feeding')}
              className={`py-2 px-4 font-medium border-b-2 transition-colors ${
                activeTab === 'feeding'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              🍽️ التغذية ({feedingLogs.length})
            </button>
            <button
              onClick={() => setActiveTab('mortality')}
              className={`py-2 px-4 font-medium border-b-2 transition-colors ${
                activeTab === 'mortality'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              💀 النفوق ({mortalityLogs.length})
            </button>
            <button
              onClick={() => setActiveTab('stats')}
              className={`py-2 px-4 font-medium border-b-2 transition-colors ${
                activeTab === 'stats'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              📊 الإحصائيات
            </button>
          </nav>
        </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        ) : (
          <>
            {/* Feeding Logs Tab */}
            {activeTab === 'feeding' && (
              <div>
                {filteredFeedingLogs.length === 0 ? (
                  <Card>
                    <EmptyState
                      icon="🍽️"
                      title={searchQuery || selectedBatchId ? 'لا توجد نتائج' : 'لا توجد سجلات تغذية'}
                      description={
                        searchQuery || selectedBatchId
                          ? 'جرب تغيير البحث أو الفلتر'
                          : 'ابدأ بإضافة سجل تغذية جديد'
                      }
                    />
                  </Card>
                ) : (
                  <div className="space-y-4">
                    {filteredFeedingLogs.map((log) => (
                      <Card key={log.id} className="hover:shadow-md transition-shadow">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <h3 className="font-semibold text-gray-900">{log.batch_number}</h3>
                              <span className="text-sm text-gray-500">•</span>
                              <span className="text-sm text-gray-600">{log.feed_type_name}</span>
                            </div>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                              <div>
                                <span className="text-gray-500">التاريخ:</span>
                                <span className="font-medium mr-2">
                                  {new Date(log.feeding_date).toLocaleDateString('ar-SA')}
                                </span>
                              </div>
                              <div>
                                <span className="text-gray-500">الكمية:</span>
                                <span className="font-medium mr-2">{log.quantity} كجم</span>
                              </div>
                              <div>
                                <span className="text-gray-500">التكلفة:</span>
                                <span className="font-medium mr-2">{log.total_cost.toFixed(2)} ريال</span>
                              </div>
                              <div>
                                <span className="text-gray-500">السعر/كجم:</span>
                                <span className="font-medium mr-2">{log.unit_price.toFixed(2)} ريال</span>
                              </div>
                            </div>
                            {log.notes && (
                              <p className="text-sm text-gray-600 mt-2">
                                <span className="font-medium">ملاحظات:</span> {log.notes}
                              </p>
                            )}
                          </div>
                          <div className="flex gap-2">
                            <button
                              onClick={() => handleEditFeeding(log)}
                              className="btn-secondary text-sm py-2 px-4"
                            >
                              تعديل
                            </button>
                            <button
                              onClick={() => handleDeleteFeeding(log)}
                              className="bg-red-50 hover:bg-red-100 text-red-700 text-sm py-2 px-4 rounded-lg transition-colors"
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

            {/* Mortality Logs Tab */}
            {activeTab === 'mortality' && (
              <div>
                {filteredMortalityLogs.length === 0 ? (
                  <Card>
                    <EmptyState
                      icon="💀"
                      title={searchQuery || selectedBatchId ? 'لا توجد نتائج' : 'لا توجد سجلات نفوق'}
                      description={
                        searchQuery || selectedBatchId
                          ? 'جرب تغيير البحث أو الفلتر'
                          : 'ابدأ بإضافة سجل نفوق جديد'
                      }
                    />
                  </Card>
                ) : (
                  <div className="space-y-4">
                    {filteredMortalityLogs.map((log) => (
                      <Card key={log.id} className="hover:shadow-md transition-shadow">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <h3 className="font-semibold text-gray-900">{log.batch_number}</h3>
                              <span className="text-sm text-gray-500">•</span>
                              <span className="text-red-600 font-medium">{log.count} سمكة</span>
                            </div>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                              <div>
                                <span className="text-gray-500">التاريخ:</span>
                                <span className="font-medium mr-2">
                                  {new Date(log.mortality_date).toLocaleDateString('ar-SA')}
                                </span>
                              </div>
                              {log.average_weight && (
                                <div>
                                  <span className="text-gray-500">متوسط الوزن:</span>
                                  <span className="font-medium mr-2">{log.average_weight.toFixed(3)} كجم</span>
                                </div>
                              )}
                              {log.cause && (
                                <div>
                                  <span className="text-gray-500">السبب:</span>
                                  <span className="font-medium mr-2">{log.cause}</span>
                                </div>
                              )}
                            </div>
                            {log.notes && (
                              <p className="text-sm text-gray-600 mt-2">
                                <span className="font-medium">ملاحظات:</span> {log.notes}
                              </p>
                            )}
                          </div>
                          <div className="flex gap-2">
                            <button
                              onClick={() => handleEditMortality(log)}
                              className="btn-secondary text-sm py-2 px-4"
                            >
                              تعديل
                            </button>
                            <button
                              onClick={() => handleDeleteMortality(log)}
                              className="bg-red-50 hover:bg-red-100 text-red-700 text-sm py-2 px-4 rounded-lg transition-colors"
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

            {/* Statistics Tab */}
            {activeTab === 'stats' && (
              <div>
                {selectedBatchStats ? (
                  <Card>
                    <div className="mb-4">
                      <h2 className="text-2xl font-bold text-gray-900 mb-2">
                        إحصائيات الدفعة: {selectedBatchStats.batch_number}
                      </h2>
                      <button
                        onClick={() => setSelectedBatchStats(null)}
                        className="text-sm text-primary-600 hover:text-primary-700"
                      >
                        ← العودة
                      </button>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                        <p className="text-sm text-blue-600 mb-1">إجمالي العلف المستهلك</p>
                        <p className="text-2xl font-bold text-blue-900">
                          {selectedBatchStats.total_feed_consumed.toFixed(2)} كجم
                        </p>
                      </div>
                      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                        <p className="text-sm text-green-600 mb-1">إجمالي تكلفة العلف</p>
                        <p className="text-2xl font-bold text-green-900">
                          {selectedBatchStats.total_feed_cost.toFixed(2)} ريال
                        </p>
                      </div>
                      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                        <p className="text-sm text-red-600 mb-1">إجمالي النفوق</p>
                        <p className="text-2xl font-bold text-red-900">{selectedBatchStats.total_mortality} سمكة</p>
                      </div>
                      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                        <p className="text-sm text-yellow-600 mb-1">العدد الحالي</p>
                        <p className="text-2xl font-bold text-yellow-900">{selectedBatchStats.current_count} سمكة</p>
                      </div>
                      <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                        <p className="text-sm text-purple-600 mb-1">الوزن الحالي</p>
                        <p className="text-2xl font-bold text-purple-900">
                          {selectedBatchStats.current_weight.toFixed(2)} كجم
                        </p>
                      </div>
                      <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
                        <p className="text-sm text-indigo-600 mb-1">متوسط الوزن</p>
                        <p className="text-2xl font-bold text-indigo-900">
                          {selectedBatchStats.average_weight.toFixed(3)} كجم
                        </p>
                      </div>
                      {selectedBatchStats.fcr && (
                        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                          <p className="text-sm text-orange-600 mb-1">معدل التحويل الغذائي (FCR)</p>
                          <p className="text-2xl font-bold text-orange-900">
                            {selectedBatchStats.fcr.toFixed(2)}
                          </p>
                        </div>
                      )}
                      <div className="bg-teal-50 border border-teal-200 rounded-lg p-4">
                        <p className="text-sm text-teal-600 mb-1">معدل النفوق</p>
                        <p className="text-2xl font-bold text-teal-900">
                          {selectedBatchStats.mortality_rate.toFixed(2)}%
                        </p>
                      </div>
                      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                        <p className="text-sm text-gray-600 mb-1">متوسط التغذية اليومي</p>
                        <p className="text-2xl font-bold text-gray-900">
                          {selectedBatchStats.avg_daily_feed.toFixed(2)} كجم
                        </p>
                      </div>
                    </div>
                  </Card>
                ) : (
                  <Card>
                    <EmptyState
                      icon="📊"
                      title="اختر دفعة لعرض الإحصائيات"
                      description="اختر دفعة من القائمة لعرض إحصائياتها الشاملة"
                    />
                    <div className="mt-6 space-y-2">
                      {activeBatches.map((batch) => (
                        <button
                          key={batch.id}
                          onClick={() => handleViewStats(batch.id)}
                          className="w-full text-right px-4 py-3 bg-gray-50 hover:bg-gray-100 text-gray-700 rounded-lg transition-colors"
                          disabled={loadingStats}
                        >
                          {batch.batch_number} - {batch.species.arabic_name}
                          {loadingStats && ' (جاري التحميل...)'}
                        </button>
                      ))}
                    </div>
                  </Card>
                )}
              </div>
            )}
          </>
        )}

        {/* Modals */}
        <Modal
          isOpen={isFeedingFormOpen}
          onClose={() => {
            setIsFeedingFormOpen(false)
            setSelectedFeedingLog(null)
          }}
          title={selectedFeedingLog ? 'تعديل سجل التغذية' : 'إضافة سجل تغذية جديد'}
        >
          <FeedingLogForm
            feedingLog={selectedFeedingLog}
            batches={activeBatches}
            feedTypes={feedTypes}
            onSubmit={handleFeedingSubmit}
            onCancel={() => {
              setIsFeedingFormOpen(false)
              setSelectedFeedingLog(null)
            }}
            isLoading={isFeedingSubmitting}
          />
        </Modal>

        <Modal
          isOpen={isMortalityFormOpen}
          onClose={() => {
            setIsMortalityFormOpen(false)
            setSelectedMortalityLog(null)
          }}
          title={selectedMortalityLog ? 'تعديل سجل النفوق' : 'إضافة سجل نفوق جديد'}
        >
          <MortalityLogForm
            mortalityLog={selectedMortalityLog}
            batches={activeBatches}
            onSubmit={handleMortalitySubmit}
            onCancel={() => {
              setIsMortalityFormOpen(false)
              setSelectedMortalityLog(null)
            }}
            isLoading={isMortalitySubmitting}
          />
        </Modal>

        {/* Delete Dialogs */}
        <ConfirmDialog
          isOpen={isFeedingDeleteDialogOpen}
          onClose={() => {
            setIsFeedingDeleteDialogOpen(false)
            setSelectedFeedingLog(null)
          }}
          onConfirm={handleConfirmFeedingDelete}
          title="تأكيد الحذف"
          message={`هل أنت متأكد من حذف سجل التغذية للدفعة "${selectedFeedingLog?.batch_number}"؟`}
        />

        <ConfirmDialog
          isOpen={isMortalityDeleteDialogOpen}
          onClose={() => {
            setIsMortalityDeleteDialogOpen(false)
            setSelectedMortalityLog(null)
          }}
          onConfirm={handleConfirmMortalityDelete}
          title="تأكيد الحذف"
          message={`هل أنت متأكد من حذف سجل النفوق للدفعة "${selectedMortalityLog?.batch_number}"؟`}
        />

        {/* Toast Notifications */}
        {toasts.map((toast) => (
          <Toast
            key={toast.id}
            message={toast.message}
            type={toast.type}
            onClose={() => removeToast(toast.id)}
          />
        ))}
      </div>
    </Layout>
  )
}

