import { useEffect, useState } from 'react'
import Layout from '../components/layout/Layout'
import Card from '../components/common/Card'
import SearchInput from '../components/common/SearchInput'
import Modal from '../components/common/Modal'
import { apiService } from '../services/api'
import type { Invoice, SalesOrder } from '../types'
import LoadingSpinner from '../components/common/LoadingSpinner'
import EmptyState from '../components/common/EmptyState'
import { useToast } from '../hooks/useToast'

export default function Invoices() {
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [orders, setOrders] = useState<SalesOrder[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedStatus, setSelectedStatus] = useState<string>('')
  const [selectedInvoice, setSelectedInvoice] = useState<Invoice | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [selectedOrderId, setSelectedOrderId] = useState<number | ''>('')
  const [submitting, setSubmitting] = useState(false)
  const { showToast } = useToast()

  useEffect(() => {
    fetchInvoices()
    fetchOrders()
  }, [selectedStatus])

  const fetchInvoices = async () => {
    try {
      setLoading(true)
      const data = await apiService.getInvoices(selectedStatus || undefined)
      setInvoices(data)
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'خطأ في جلب الفواتير', 'error')
    } finally {
      setLoading(false)
    }
  }

  const fetchOrders = async () => {
    try {
      const data = await apiService.getSalesOrders('confirmed')
      setOrders(data.filter((o) => o.status === 'confirmed'))
    } catch (err) {
      console.error('Error fetching orders:', err)
    }
  }

  const filteredInvoices = invoices.filter(
    (inv) =>
      inv.invoice_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
      inv.invoice_date.includes(searchQuery)
  )

  const handleCreateInvoice = async () => {
    if (!selectedOrderId) {
      showToast('يجب اختيار طلب البيع', 'error')
      return
    }

    try {
      setSubmitting(true)
      await apiService.createInvoice(selectedOrderId as number)
      showToast('تم إنشاء الفاتورة بنجاح', 'success')
      setIsCreateModalOpen(false)
      setSelectedOrderId('')
      fetchInvoices()
      fetchOrders()
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'خطأ في إنشاء الفاتورة', 'error')
    } finally {
      setSubmitting(false)
    }
  }

  const getStatusBadge = (status: string) => {
    const badges: Record<string, { text: string; className: string }> = {
      draft: { text: 'مسودة', className: 'bg-gray-100 text-gray-800' },
      issued: { text: 'مصدرة', className: 'bg-blue-100 text-blue-800' },
      paid: { text: 'مدفوعة', className: 'bg-green-100 text-green-800' },
      cancelled: { text: 'ملغاة', className: 'bg-red-100 text-red-800' },
    }
    const badge = badges[status] || badges.draft
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
            <h1 className="text-3xl font-bold text-gray-900">الفواتير</h1>
            <p className="mt-2 text-gray-600">إدارة الفواتير الضريبية</p>
          </div>
          <button onClick={() => setIsCreateModalOpen(true)} className="btn-primary">
            + فاتورة جديدة
          </button>
        </div>

        <Card>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <SearchInput value={searchQuery} onChange={setSearchQuery} placeholder="ابحث..." />
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="input-field"
            >
              <option value="">جميع الحالات</option>
              <option value="draft">مسودة</option>
              <option value="issued">مصدرة</option>
              <option value="paid">مدفوعة</option>
              <option value="cancelled">ملغاة</option>
            </select>
          </div>
        </Card>

        {loading ? (
          <div className="flex justify-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        ) : filteredInvoices.length === 0 ? (
          <Card>
            <EmptyState icon="🧾" title="لا توجد فواتير" description="ابدأ بإنشاء فاتورة جديدة" />
          </Card>
        ) : (
          <div className="space-y-4">
            {filteredInvoices.map((invoice) => (
              <div
                key={invoice.id}
                onClick={() => {
                  setSelectedInvoice(invoice)
                  setIsModalOpen(true)
                }}
              >
                <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                <div className="flex justify-between items-start">
                  <div>
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {invoice.invoice_number}
                      </h3>
                      {getStatusBadge(invoice.status)}
                      {invoice.zatca_status && (
                        <span className="px-2 py-1 text-xs font-medium rounded bg-blue-100 text-blue-800">
                          ZATCA: {invoice.zatca_status}
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600">
                      تاريخ الفاتورة: {new Date(invoice.invoice_date).toLocaleDateString('ar-SA')}
                    </p>
                    {invoice.qr_code && (
                      <p className="text-xs text-gray-500 mt-1">✅ QR Code متوفر</p>
                    )}
                  </div>
                  <div className="text-left">
                    <p className="text-lg font-bold text-gray-900">
                      {invoice.total_amount.toFixed(2)} ريال
                    </p>
                    <p className="text-sm text-gray-500">
                      شامل الضريبة: {invoice.vat_amount.toFixed(2)} ريال
                    </p>
                  </div>
                </div>
                </Card>
              </div>
            ))}
          </div>
        )}

        {/* Invoice Details Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={() => {
            setIsModalOpen(false)
            setSelectedInvoice(null)
          }}
          title={selectedInvoice ? `فاتورة ${selectedInvoice.invoice_number}` : 'تفاصيل الفاتورة'}
        >
          {selectedInvoice && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">رقم الفاتورة</label>
                  <p className="text-gray-900 font-medium">{selectedInvoice.invoice_number}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">تاريخ الفاتورة</label>
                  <p className="text-gray-900">
                    {new Date(selectedInvoice.invoice_date).toLocaleDateString('ar-SA')}
                  </p>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">الحالة</label>
                <div className="mt-1">{getStatusBadge(selectedInvoice.status)}</div>
              </div>

              <div className="border-t border-gray-200 pt-4 space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">المجموع الفرعي:</span>
                  <span className="font-medium">{selectedInvoice.subtotal.toFixed(2)} ريال</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">الضريبة:</span>
                  <span className="font-medium">{selectedInvoice.vat_amount.toFixed(2)} ريال</span>
                </div>
                <div className="flex justify-between text-base font-bold border-t border-gray-300 pt-2">
                  <span>الإجمالي:</span>
                  <span className="text-primary-600">
                    {selectedInvoice.total_amount.toFixed(2)} ريال
                  </span>
                </div>
              </div>

              {selectedInvoice.qr_code && (
                <div className="border-t border-gray-200 pt-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    QR Code (ZATCA)
                  </label>
                  <div className="bg-gray-50 p-3 rounded border break-all text-xs font-mono">
                    {selectedInvoice.qr_code.substring(0, 100)}...
                  </div>
                </div>
              )}

              {selectedInvoice.uuid && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">UUID</label>
                  <p className="text-xs font-mono text-gray-600">{selectedInvoice.uuid}</p>
                </div>
              )}

              <div className="flex gap-3 justify-end pt-4 border-t border-gray-200">
                <button
                  type="button"
                  onClick={() => {
                    setIsModalOpen(false)
                    setSelectedInvoice(null)
                  }}
                  className="btn-secondary"
                >
                  إغلاق
                </button>
                {selectedInvoice && (
                  <button
                    type="button"
                    onClick={async () => {
                      try {
                        const blob = await apiService.downloadInvoicePdf(selectedInvoice.id)
                        const url = window.URL.createObjectURL(blob)
                        const link = document.createElement('a')
                        link.href = url
                        link.download = `invoice_${selectedInvoice.invoice_number}.pdf`
                        document.body.appendChild(link)
                        link.click()
                        document.body.removeChild(link)
                        window.URL.revokeObjectURL(url)
                        showToast('تم تحميل PDF بنجاح', 'success')
                      } catch (err: any) {
                        showToast(err.response?.data?.detail || 'خطأ في تحميل PDF', 'error')
                      }
                    }}
                    className="btn-primary"
                  >
                    📄 تحميل PDF
                  </button>
                )}
              </div>
            </div>
          )}
        </Modal>

        {/* Create Invoice Modal */}
        <Modal
          isOpen={isCreateModalOpen}
          onClose={() => {
            setIsCreateModalOpen(false)
            setSelectedOrderId('')
          }}
          title="إنشاء فاتورة جديدة"
        >
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                طلب البيع <span className="text-red-500">*</span>
              </label>
              <select
                required
                value={selectedOrderId}
                onChange={(e) => setSelectedOrderId(e.target.value ? parseInt(e.target.value) : '')}
                className="input-field"
              >
                <option value="">اختر طلب البيع</option>
                {orders.map((order) => (
                  <option key={order.id} value={order.id}>
                    {order.order_number} - {order.customer_name} - {order.total_amount.toFixed(2)} ريال
                  </option>
                ))}
              </select>
              <p className="text-xs text-gray-500 mt-1">
                فقط طلبات البيع المؤكدة يمكن تحويلها إلى فواتير
              </p>
            </div>

            {selectedOrderId && (
              <div className="bg-gray-50 p-4 rounded-lg">
                {(() => {
                  const order = orders.find((o) => o.id === selectedOrderId)
                  return order ? (
                    <div className="space-y-2">
                      <p className="text-sm font-medium text-gray-700">
                        العميل: {order.customer_name}
                      </p>
                      <p className="text-sm text-gray-600">
                        المجموع: {order.subtotal.toFixed(2)} ريال
                      </p>
                      <p className="text-sm text-gray-600">
                        الضريبة: {order.vat_amount.toFixed(2)} ريال
                      </p>
                      <p className="text-base font-bold text-gray-900">
                        الإجمالي: {order.total_amount.toFixed(2)} ريال
                      </p>
                    </div>
                  ) : null
                })()}
              </div>
            )}

            <div className="flex gap-3 justify-end pt-4">
              <button
                type="button"
                onClick={() => {
                  setIsCreateModalOpen(false)
                  setSelectedOrderId('')
                }}
                className="btn-secondary"
              >
                إلغاء
              </button>
              <button
                type="button"
                onClick={handleCreateInvoice}
                className="btn-primary"
                disabled={submitting || !selectedOrderId}
              >
                {submitting ? 'جاري الإنشاء...' : 'إنشاء الفاتورة'}
              </button>
            </div>
          </div>
        </Modal>
      </div>
    </Layout>
  )
}

