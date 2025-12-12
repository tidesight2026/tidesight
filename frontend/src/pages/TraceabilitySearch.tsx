import { useState } from 'react'
import Layout from '../components/layout/Layout'
import Card from '../components/common/Card'
import { apiService } from '../services/api'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { useUIStore } from '../store/uiStore'

type SearchType = 'invoice' | 'batch'

export default function TraceabilitySearch() {
  const [searchType, setSearchType] = useState<SearchType>('invoice')
  const [searchValue, setSearchValue] = useState('')
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<any>(null)
  const { error, success } = useUIStore()

  const handleSearch = async () => {
    if (!searchValue.trim()) {
      error('يرجى إدخال قيمة للبحث')
      return
    }

    setLoading(true)
    setData(null)

    try {
      let result
      if (searchType === 'invoice') {
        // البحث برقم الفاتورة
        const invoiceId = parseInt(searchValue)
        if (isNaN(invoiceId)) {
          error('رقم الفاتورة يجب أن يكون رقماً')
          return
        }
        result = await apiService.getTraceabilityByInvoice(invoiceId)
      } else {
        // البحث برقم الدفعة
        const batchId = parseInt(searchValue)
        if (isNaN(batchId)) {
          error('رقم الدفعة يجب أن يكون رقماً')
          return
        }
        result = await apiService.getTraceabilityByBatch(batchId)
      }

      setData(result)
      success('تم العثور على البيانات بنجاح')
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'حدث خطأ أثناء البحث'
      error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">بحث التتبع</h1>
          <p className="text-gray-600 mt-2">تتبع المنتج من الفاتورة إلى الدفعة أو العكس</p>
        </div>

        {/* Search Form */}
        <Card>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                نوع البحث
              </label>
              <div className="flex gap-4">
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="invoice"
                    checked={searchType === 'invoice'}
                    onChange={(e) => setSearchType(e.target.value as SearchType)}
                    className="ml-2"
                  />
                  <span>بحث برقم الفاتورة</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="batch"
                    checked={searchType === 'batch'}
                    onChange={(e) => setSearchType(e.target.value as SearchType)}
                    className="ml-2"
                  />
                  <span>بحث برقم الدفعة</span>
                </label>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {searchType === 'invoice' ? 'رقم الفاتورة' : 'رقم الدفعة'}
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={searchValue}
                  onChange={(e) => setSearchValue(e.target.value)}
                  placeholder={searchType === 'invoice' ? 'أدخل رقم الفاتورة' : 'أدخل رقم الدفعة'}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      handleSearch()
                    }
                  }}
                />
                <button
                  onClick={handleSearch}
                  disabled={loading}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'جاري البحث...' : 'بحث'}
                </button>
              </div>
            </div>
          </div>
        </Card>

        {/* Loading */}
        {loading && (
          <div className="flex justify-center items-center h-64">
            <LoadingSpinner />
          </div>
        )}

        {/* Results */}
        {data && !loading && (
          <div className="space-y-6">
            {/* Invoice Results */}
            {searchType === 'invoice' && data.invoice && (
              <>
                <Card>
                  <h2 className="text-xl font-semibold mb-4">معلومات الفاتورة</h2>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <span className="text-gray-600">رقم الفاتورة:</span>
                      <span className="font-semibold mr-2">{data.invoice.invoice_number}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">تاريخ الفاتورة:</span>
                      <span className="font-semibold mr-2">{data.invoice.invoice_date}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">المبلغ الإجمالي:</span>
                      <span className="font-semibold mr-2">{data.invoice.total_amount} ريال</span>
                    </div>
                    <div>
                      <span className="text-gray-600">الحالة:</span>
                      <span className="font-semibold mr-2">{data.invoice.status}</span>
                    </div>
                  </div>
                </Card>

                <Card>
                  <h2 className="text-xl font-semibold mb-4">معلومات طلب البيع</h2>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <span className="text-gray-600">رقم الطلب:</span>
                      <span className="font-semibold mr-2">{data.sales_order.order_number}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">اسم العميل:</span>
                      <span className="font-semibold mr-2">{data.sales_order.customer_name}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">تاريخ الطلب:</span>
                      <span className="font-semibold mr-2">{data.sales_order.order_date}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">المبلغ الإجمالي:</span>
                      <span className="font-semibold mr-2">{data.sales_order.total_amount} ريال</span>
                    </div>
                  </div>
                </Card>

                {data.harvests && data.harvests.length > 0 && (
                  <Card>
                    <h2 className="text-xl font-semibold mb-4">معلومات الحصاد</h2>
                    <div className="space-y-4">
                      {data.harvests.map((harvest: any) => (
                        <div key={harvest.id} className="border-b pb-4 last:border-b-0">
                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <span className="text-gray-600">تاريخ الحصاد:</span>
                              <span className="font-semibold mr-2">{harvest.harvest_date}</span>
                            </div>
                            <div>
                              <span className="text-gray-600">الكمية:</span>
                              <span className="font-semibold mr-2">{harvest.quantity_kg} كجم</span>
                            </div>
                            <div>
                              <span className="text-gray-600">العدد:</span>
                              <span className="font-semibold mr-2">{harvest.count}</span>
                            </div>
                            <div>
                              <span className="text-gray-600">متوسط الوزن:</span>
                              <span className="font-semibold mr-2">{harvest.average_weight} كجم</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </Card>
                )}

                {data.batches && data.batches.length > 0 && (
                  <Card>
                    <h2 className="text-xl font-semibold mb-4">معلومات الدفعات</h2>
                    <div className="space-y-4">
                      {data.batches.map((batch: any) => (
                        <div key={batch.id} className="border-b pb-4 last:border-b-0">
                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <span className="text-gray-600">رقم الدفعة:</span>
                              <span className="font-semibold mr-2">{batch.batch_number}</span>
                            </div>
                            <div>
                              <span className="text-gray-600">النوع:</span>
                              <span className="font-semibold mr-2">{batch.species_name}</span>
                            </div>
                            <div>
                              <span className="text-gray-600">الحوض:</span>
                              <span className="font-semibold mr-2">{batch.pond_name}</span>
                            </div>
                            <div>
                              <span className="text-gray-600">تاريخ البدء:</span>
                              <span className="font-semibold mr-2">{batch.start_date}</span>
                            </div>
                            <div>
                              <span className="text-gray-600">العدد الحالي:</span>
                              <span className="font-semibold mr-2">{batch.current_count}</span>
                            </div>
                            <div>
                              <span className="text-gray-600">الوزن الحالي:</span>
                              <span className="font-semibold mr-2">{batch.current_weight} كجم</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </Card>
                )}

                {data.feeding_logs && data.feeding_logs.length > 0 && (
                  <Card>
                    <h2 className="text-xl font-semibold mb-4">سجلات التغذية (آخر 10)</h2>
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">
                              التاريخ
                            </th>
                            <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">
                              الكمية (كجم)
                            </th>
                            <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">
                              نوع العلف
                            </th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {data.feeding_logs.slice(0, 10).map((log: any) => (
                            <tr key={log.id}>
                              <td className="px-4 py-2 text-sm">{log.feeding_date}</td>
                              <td className="px-4 py-2 text-sm">{log.quantity}</td>
                              <td className="px-4 py-2 text-sm">{log.feed_type_name}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </Card>
                )}
              </>
            )}

            {/* Batch Results */}
            {searchType === 'batch' && data.batch && (
              <>
                <Card>
                  <h2 className="text-xl font-semibold mb-4">معلومات الدفعة</h2>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <span className="text-gray-600">رقم الدفعة:</span>
                      <span className="font-semibold mr-2">{data.batch.batch_number}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">النوع:</span>
                      <span className="font-semibold mr-2">{data.batch.species_name}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">الحوض:</span>
                      <span className="font-semibold mr-2">{data.batch.pond_name}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">تاريخ البدء:</span>
                      <span className="font-semibold mr-2">{data.batch.start_date}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">العدد الحالي:</span>
                      <span className="font-semibold mr-2">{data.batch.current_count}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">الوزن الحالي:</span>
                      <span className="font-semibold mr-2">{data.batch.current_weight} كجم</span>
                    </div>
                  </div>
                </Card>

                {data.harvests && data.harvests.length > 0 && (
                  <Card>
                    <h2 className="text-xl font-semibold mb-4">الحصاد المرتبط</h2>
                    <div className="space-y-4">
                      {data.harvests.map((harvest: any) => (
                        <div key={harvest.id} className="border-b pb-4 last:border-b-0">
                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <span className="text-gray-600">تاريخ الحصاد:</span>
                              <span className="font-semibold mr-2">{harvest.harvest_date}</span>
                            </div>
                            <div>
                              <span className="text-gray-600">الكمية:</span>
                              <span className="font-semibold mr-2">{harvest.quantity_kg} كجم</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </Card>
                )}

                {data.sales_orders && data.sales_orders.length > 0 && (
                  <Card>
                    <h2 className="text-xl font-semibold mb-4">طلبات البيع المرتبطة</h2>
                    <div className="space-y-4">
                      {data.sales_orders.map((order: any) => (
                        <div key={order.id} className="border-b pb-4 last:border-b-0">
                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <span className="text-gray-600">رقم الطلب:</span>
                              <span className="font-semibold mr-2">{order.order_number}</span>
                            </div>
                            <div>
                              <span className="text-gray-600">اسم العميل:</span>
                              <span className="font-semibold mr-2">{order.customer_name}</span>
                            </div>
                            <div>
                              <span className="text-gray-600">تاريخ الطلب:</span>
                              <span className="font-semibold mr-2">{order.order_date}</span>
                            </div>
                            <div>
                              <span className="text-gray-600">المبلغ:</span>
                              <span className="font-semibold mr-2">{order.total_amount} ريال</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </Card>
                )}

                {data.invoices && data.invoices.length > 0 && (
                  <Card>
                    <h2 className="text-xl font-semibold mb-4">الفواتير المرتبطة</h2>
                    <div className="space-y-4">
                      {data.invoices.map((invoice: any) => (
                        <div key={invoice.id} className="border-b pb-4 last:border-b-0">
                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <span className="text-gray-600">رقم الفاتورة:</span>
                              <span className="font-semibold mr-2">{invoice.invoice_number}</span>
                            </div>
                            <div>
                              <span className="text-gray-600">تاريخ الفاتورة:</span>
                              <span className="font-semibold mr-2">{invoice.invoice_date}</span>
                            </div>
                            <div>
                              <span className="text-gray-600">المبلغ:</span>
                              <span className="font-semibold mr-2">{invoice.total_amount} ريال</span>
                            </div>
                            <div>
                              <span className="text-gray-600">الحالة:</span>
                              <span className="font-semibold mr-2">{invoice.status}</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </Card>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </Layout>
  )
}
