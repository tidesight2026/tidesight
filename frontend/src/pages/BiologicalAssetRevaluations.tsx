import { useEffect, useState } from 'react'
import Layout from '../components/layout/Layout'
import Card from '../components/common/Card'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { apiService } from '../services/api'
import type { BiologicalAssetRevaluation } from '../types'
import { useToast } from '../hooks/useToast'
import { useTranslation } from 'react-i18next'

export default function BiologicalAssetRevaluations() {
  const { i18n } = useTranslation()
  const [revaluations, setRevaluations] = useState<BiologicalAssetRevaluation[]>([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    batch_id: '',
    start_date: '',
    end_date: '',
  })
  const { showToast } = useToast()

  useEffect(() => {
    fetchRevaluations()
  }, [filters])

  const fetchRevaluations = async () => {
    try {
      setLoading(true)
      const params: any = {}
      if (filters.batch_id) params.batch_id = parseInt(filters.batch_id)
      if (filters.start_date) params.start_date = filters.start_date
      if (filters.end_date) params.end_date = filters.end_date
      
      const data = await apiService.getBiologicalAssetRevaluations(params)
      setRevaluations(data)
    } catch (err: any) {
      showToast(err.response?.data?.detail || 'خطأ في جلب إعادة التقييم', 'error')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('ar-SA', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    })
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ar-SA', {
      style: 'currency',
      currency: 'SAR',
    }).format(amount)
  }

  const getGainLossColor = (amount: number) => {
    if (amount > 0) return 'text-green-600 font-semibold'
    if (amount < 0) return 'text-red-600 font-semibold'
    return 'text-gray-600'
  }

  return (
    <Layout>
      <div className="space-y-6" dir={i18n.dir()}>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">إعادة تقييم الأصول البيولوجية (IAS 41)</h1>
          <p className="mt-2 text-gray-600">إعادة تقييم شهرية للأصول البيولوجية حسب معيار IAS 41</p>
        </div>

        {/* Filters */}
        <Card title="تصفية النتائج">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                رقم الدفعة
              </label>
              <input
                type="number"
                value={filters.batch_id}
                onChange={(e) => setFilters({ ...filters, batch_id: e.target.value })}
                className="input-field"
                placeholder="جميع الدفعات"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                من تاريخ
              </label>
              <input
                type="date"
                value={filters.start_date}
                onChange={(e) => setFilters({ ...filters, start_date: e.target.value })}
                className="input-field"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                إلى تاريخ
              </label>
              <input
                type="date"
                value={filters.end_date}
                onChange={(e) => setFilters({ ...filters, end_date: e.target.value })}
                className="input-field"
              />
            </div>
          </div>
        </Card>

        {/* Summary */}
        {!loading && revaluations.length > 0 && (
          <Card title="ملخص إعادة التقييم">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {revaluations.length}
                </div>
                <div className="text-sm text-gray-600 mt-1">عدد عمليات التقييم</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {formatCurrency(
                    revaluations.reduce((sum, r) => sum + r.carrying_amount, 0)
                  )}
                </div>
                <div className="text-sm text-gray-600 mt-1">إجمالي القيمة الدفترية</div>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {formatCurrency(
                    revaluations.reduce((sum, r) => sum + r.fair_value, 0)
                  )}
                </div>
                <div className="text-sm text-gray-600 mt-1">إجمالي القيمة العادلة</div>
              </div>
              <div className="text-center p-4 bg-yellow-50 rounded-lg">
                <div className={`text-2xl font-bold ${getGainLossColor(
                  revaluations.reduce((sum, r) => sum + r.unrealized_gain_loss, 0)
                )}`}>
                  {formatCurrency(
                    revaluations.reduce((sum, r) => sum + r.unrealized_gain_loss, 0)
                  )}
                </div>
                <div className="text-sm text-gray-600 mt-1">إجمالي الربح/الخسارة غير المحققة</div>
              </div>
            </div>
          </Card>
        )}

        {/* Revaluations Table */}
        <Card>
          {loading ? (
            <div className="flex justify-center py-12">
              <LoadingSpinner />
            </div>
          ) : revaluations.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <p>لا توجد عمليات إعادة تقييم</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      التاريخ
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      الدفعة
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      الوزن (كجم)
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      سعر السوق
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      القيمة الدفترية
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      القيمة العادلة
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      ربح/خسارة غير محققة
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {revaluations.map((rev) => (
                    <tr key={rev.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatDate(rev.revaluation_date)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {rev.batch_number}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {rev.current_weight_kg.toFixed(2)} كجم
                        <br />
                        <span className="text-xs text-gray-400">
                          {rev.current_count} سمكة
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {rev.market_price_per_kg.toFixed(2)} ريال/كجم
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatCurrency(rev.carrying_amount)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {formatCurrency(rev.fair_value)}
                      </td>
                      <td className={`px-6 py-4 whitespace-nowrap text-sm ${getGainLossColor(rev.unrealized_gain_loss)}`}>
                        {formatCurrency(rev.unrealized_gain_loss)}
                        {rev.unrealized_gain_loss > 0 && (
                          <span className="text-xs"> (ربح)</span>
                        )}
                        {rev.unrealized_gain_loss < 0 && (
                          <span className="text-xs"> (خسارة)</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </div>
    </Layout>
  )
}

