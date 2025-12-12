import { useEffect, useState } from 'react'
import Layout from '../components/layout/Layout'
import Card from '../components/common/Card'
import SearchInput from '../components/common/SearchInput'
import Modal from '../components/common/Modal'
import { apiService } from '../services/api'
import type { SalesOrder, Harvest } from '../types'
import LoadingSpinner from '../components/common/LoadingSpinner'
import EmptyState from '../components/common/EmptyState'
import { useToast } from '../hooks/useToast'

export default function SalesOrders() {
  const [orders, setOrders] = useState<SalesOrder[]>([])
  const [harvests, setHarvests] = useState<Harvest[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedStatus, setSelectedStatus] = useState<string>('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [formData, setFormData] = useState({
    order_date: new Date().toISOString().split('T')[0],
    customer_name: '',
    customer_phone: '',
    customer_address: '',
    vat_rate: 15,
    notes: '',
    lines: [] as Array<{ harvest_id: number; quantity_kg: number; unit_price: number }>,
  })
  const [submitting, setSubmitting] = useState(false)
  const { showToast } = useToast()

  useEffect(() => {
    fetchOrders()
    fetchHarvests()
  }, [selectedStatus])

  const fetchOrders = async () => {
    try {
      setLoading(true)
      const data = await apiService.getSalesOrders(selectedStatus || undefined)
      setOrders(data)
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'خطأ في جلب طلبات البيع', 'error')
    } finally {
      setLoading(false)
    }
  }

  const fetchHarvests = async () => {
    try {
      const data = await apiService.getHarvests({ status: 'completed' })
      setHarvests(data)
    } catch (err) {
      console.error('Error fetching harvests:', err)
    }
  }

  const filteredOrders = orders.filter(
    (o) =>
      o.order_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
      o.customer_name.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const addLine = () => {
    setFormData({
      ...formData,
      lines: [
        ...formData.lines,
        { harvest_id: harvests[0]?.id || 0, quantity_kg: 0, unit_price: 0 },
      ],
    })
  }

  const removeLine = (index: number) => {
    setFormData({
      ...formData,
      lines: formData.lines.filter((_, i) => i !== index),
    })
  }

  const updateLine = (index: number, field: string, value: any) => {
    const newLines = [...formData.lines]
    newLines[index] = { ...newLines[index], [field]: value }
    setFormData({ ...formData, lines: newLines })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (formData.lines.length === 0) {
      showToast('يجب إضافة بند واحد على الأقل', 'error')
      return
    }

    try {
      setSubmitting(true)
      await apiService.createSalesOrder(formData)
      showToast('تم إنشاء طلب البيع بنجاح', 'success')
      setIsModalOpen(false)
      resetForm()
      fetchOrders()
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'خطأ في إنشاء طلب البيع', 'error')
    } finally {
      setSubmitting(false)
    }
  }

  const resetForm = () => {
    setFormData({
      order_date: new Date().toISOString().split('T')[0],
      customer_name: '',
      customer_phone: '',
      customer_address: '',
      vat_rate: 15,
      notes: '',
      lines: [],
    })
  }

  const calculateSubtotal = () => {
    return formData.lines.reduce((sum, line) => sum + line.quantity_kg * line.unit_price, 0)
  }

  const calculateVat = () => {
    return (calculateSubtotal() * formData.vat_rate) / 100
  }

  const calculateTotal = () => {
    return calculateSubtotal() + calculateVat()
  }

  const getStatusBadge = (status: string) => {
    const badges: Record<string, { text: string; className: string }> = {
      draft: { text: 'مسودة', className: 'bg-gray-100 text-gray-800' },
      confirmed: { text: 'مؤكد', className: 'bg-blue-100 text-blue-800' },
      invoiced: { text: 'مفوتر', className: 'bg-green-100 text-green-800' },
      delivered: { text: 'تم التسليم', className: 'bg-purple-100 text-purple-800' },
      cancelled: { text: 'ملغي', className: 'bg-red-100 text-red-800' },
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
            <h1 className="text-3xl font-bold text-gray-900">طلبات البيع</h1>
            <p className="mt-2 text-gray-600">إدارة طلبات بيع الأسماك</p>
          </div>
          <button onClick={() => setIsModalOpen(true)} className="btn-primary">
            + طلب بيع جديد
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
              <option value="confirmed">مؤكد</option>
              <option value="invoiced">مفوتر</option>
              <option value="delivered">تم التسليم</option>
              <option value="cancelled">ملغي</option>
            </select>
          </div>
        </Card>

        {loading ? (
          <div className="flex justify-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        ) : filteredOrders.length === 0 ? (
          <Card>
            <EmptyState icon="📋" title="لا توجد طلبات بيع" description="ابدأ بإنشاء طلب بيع جديد" />
          </Card>
        ) : (
          <div className="space-y-4">
            {filteredOrders.map((order) => (
              <Card key={order.id} className="hover:shadow-lg transition-shadow">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">{order.order_number}</h3>
                      {getStatusBadge(order.status)}
                    </div>
                    <p className="text-sm text-gray-600">
                      العميل: <span className="font-medium">{order.customer_name}</span>
                    </p>
                    <p className="text-sm text-gray-500">
                      {new Date(order.order_date).toLocaleDateString('ar-SA')}
                    </p>
                  </div>
                  <div className="text-left">
                    <p className="text-lg font-bold text-gray-900">
                      {order.total_amount.toFixed(2)} ريال
                    </p>
                    <p className="text-sm text-gray-500">
                      المجموع: {order.subtotal.toFixed(2)} + ضريبة: {order.vat_amount.toFixed(2)}
                    </p>
                  </div>
                </div>
                <div className="border-t border-gray-200 pt-4">
                  <p className="text-sm font-medium text-gray-700 mb-2">البنود:</p>
                  <div className="space-y-2">
                    {order.lines.map((line, idx) => (
                      <div key={idx} className="flex justify-between text-sm bg-gray-50 p-2 rounded">
                        <span className="text-gray-600">
                          {line.quantity_kg} كجم × {line.unit_price.toFixed(2)} ريال
                        </span>
                        <span className="font-medium">{line.line_total.toFixed(2)} ريال</span>
                      </div>
                    ))}
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
          title="طلب بيع جديد"
        >
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  تاريخ الطلب <span className="text-red-500">*</span>
                </label>
                <input
                  type="date"
                  required
                  value={formData.order_date}
                  onChange={(e) => setFormData({ ...formData, order_date: e.target.value })}
                  className="input-field"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  معدل الضريبة (%) <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  step="0.01"
                  required
                  value={formData.vat_rate}
                  onChange={(e) =>
                    setFormData({ ...formData, vat_rate: parseFloat(e.target.value) })
                  }
                  className="input-field"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                اسم العميل <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                required
                value={formData.customer_name}
                onChange={(e) => setFormData({ ...formData, customer_name: e.target.value })}
                className="input-field"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">هاتف العميل</label>
                <input
                  type="tel"
                  value={formData.customer_phone}
                  onChange={(e) => setFormData({ ...formData, customer_phone: e.target.value })}
                  className="input-field"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">عنوان العميل</label>
                <input
                  type="text"
                  value={formData.customer_address}
                  onChange={(e) =>
                    setFormData({ ...formData, customer_address: e.target.value })
                  }
                  className="input-field"
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="block text-sm font-medium text-gray-700">بنود الطلب</label>
                <button
                  type="button"
                  onClick={addLine}
                  className="text-sm text-primary-600 hover:text-primary-700"
                >
                  + إضافة بند
                </button>
              </div>
              <div className="space-y-2 border rounded-lg p-3 max-h-60 overflow-y-auto">
                {formData.lines.length === 0 ? (
                  <p className="text-sm text-gray-500 text-center py-4">
                    لا توجد بنود. اضغط "إضافة بند" لإضافة بند جديد.
                  </p>
                ) : (
                  formData.lines.map((line, idx) => (
                    <div key={idx} className="grid grid-cols-12 gap-2 items-end bg-gray-50 p-2 rounded">
                      <div className="col-span-4">
                        <label className="block text-xs text-gray-600 mb-1">الحصاد</label>
                        <select
                          required
                          value={line.harvest_id}
                          onChange={(e) =>
                            updateLine(idx, 'harvest_id', parseInt(e.target.value))
                          }
                          className="input-field text-sm"
                        >
                          <option value="">اختر</option>
                          {harvests.map((h) => (
                            <option key={h.id} value={h.id}>
                              {h.batch_number} - {h.quantity_kg} كجم
                            </option>
                          ))}
                        </select>
                      </div>
                      <div className="col-span-3">
                        <label className="block text-xs text-gray-600 mb-1">الكمية (كجم)</label>
                        <input
                          type="number"
                          step="0.01"
                          required
                          value={line.quantity_kg}
                          onChange={(e) =>
                            updateLine(idx, 'quantity_kg', parseFloat(e.target.value))
                          }
                          className="input-field text-sm"
                        />
                      </div>
                      <div className="col-span-3">
                        <label className="block text-xs text-gray-600 mb-1">السعر (ريال)</label>
                        <input
                          type="number"
                          step="0.01"
                          required
                          value={line.unit_price}
                          onChange={(e) =>
                            updateLine(idx, 'unit_price', parseFloat(e.target.value))
                          }
                          className="input-field text-sm"
                        />
                      </div>
                      <div className="col-span-2">
                        <button
                          type="button"
                          onClick={() => removeLine(idx)}
                          className="w-full btn-secondary text-sm py-2"
                        >
                          حذف
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            <div className="bg-gray-50 p-4 rounded-lg space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">المجموع الفرعي:</span>
                <span className="font-medium">{calculateSubtotal().toFixed(2)} ريال</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">الضريبة ({formData.vat_rate}%):</span>
                <span className="font-medium">{calculateVat().toFixed(2)} ريال</span>
              </div>
              <div className="flex justify-between text-base font-bold border-t border-gray-300 pt-2">
                <span>الإجمالي:</span>
                <span className="text-primary-600">{calculateTotal().toFixed(2)} ريال</span>
              </div>
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

