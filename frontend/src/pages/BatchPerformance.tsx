import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import Layout from '../components/layout/Layout'
import Card from '../components/common/Card'
import { apiService } from '../services/api'
import type { BatchPerformance, BatchPerformanceItem } from '../types'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts'

export default function BatchPerformance() {
  const { t } = useTranslation()
  const [data, setData] = useState<BatchPerformance | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await apiService.getBatchPerformance()
        setData(response)
      } catch (error) {
        console.error('Error fetching batch performance:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  if (loading) {
    return (
      <Layout>
        <div className="flex justify-center items-center h-64">
          <LoadingSpinner />
        </div>
      </Layout>
    )
  }

  if (!data || data.batches.length === 0) {
    return (
      <Layout>
        <div className="text-center py-8">
          <p className="text-gray-500">لا توجد دفعات نشطة</p>
        </div>
      </Layout>
    )
  }

  // إعداد بيانات للرسوم البيانية
  const fcrData = data.batches
    .filter(b => b.fcr !== null)
    .map(b => ({
      name: b.batch_number,
      fcr: b.fcr,
    }))

  const mortalityRateData = data.batches.map(b => ({
    name: b.batch_number,
    rate: b.mortality_rate,
  }))

  const weightGainData = data.batches
    .filter(b => b.weight_gain_rate_daily !== null)
    .map(b => ({
      name: b.batch_number,
      rate: b.weight_gain_rate_daily,
    }))

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">أداء الدفعات</h1>
          <p className="text-gray-600 mt-2">مؤشرات الأداء لجميع الدفعات النشطة</p>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <h2 className="text-xl font-semibold mb-4">معامل تحويل العلف (FCR)</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={fcrData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="fcr" fill="#3b82f6" name="FCR" />
              </BarChart>
            </ResponsiveContainer>
          </Card>

          <Card>
            <h2 className="text-xl font-semibold mb-4">معدل النفوق (%)</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={mortalityRateData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="rate" fill="#ef4444" name="معدل النفوق (%)" />
              </BarChart>
            </ResponsiveContainer>
          </Card>

          <Card>
            <h2 className="text-xl font-semibold mb-4">معدل النمو اليومي (كجم/يوم)</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={weightGainData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="rate" stroke="#10b981" name="معدل النمو (كجم/يوم)" />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </div>

        {/* Table */}
        <Card>
          <h2 className="text-xl font-semibold mb-4">جدول أداء الدفعات</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    رقم الدفعة
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    النوع
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    الحوض
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    FCR
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    متوسط الوزن (كجم)
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    معدل النفوق (%)
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    معدل النمو (كجم/يوم)
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    الأيام النشطة
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    العدد الحالي
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    الوزن الحالي (كجم)
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {data.batches.map((batch) => (
                  <tr key={batch.batch_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {batch.batch_number}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {batch.species_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {batch.pond_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {batch.fcr !== null ? batch.fcr.toFixed(2) : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {batch.average_weight_kg.toFixed(3)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {batch.mortality_rate.toFixed(2)}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {batch.weight_gain_rate_daily !== null
                        ? batch.weight_gain_rate_daily.toFixed(3)
                        : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {batch.days_active}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {batch.current_count}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {batch.current_weight_kg.toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </Layout>
  )
}
