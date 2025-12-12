import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import Layout from '../components/layout/Layout'
import Card from '../components/common/Card'
import { apiService } from '../services/api'
import type { FarmOverview } from '../types'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function FarmOverview() {
  const { t } = useTranslation()
  const [data, setData] = useState<FarmOverview | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await apiService.getFarmOverview()
        setData(response)
      } catch (error) {
        console.error('Error fetching farm overview:', error)
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

  if (!data) {
    return (
      <Layout>
        <div className="text-center py-8">
          <p className="text-gray-500">لا توجد بيانات متاحة</p>
        </div>
      </Layout>
    )
  }

  // بيانات للرسم البياني
  const feedConsumptionData = [
    { name: 'الأسبوع الماضي', value: data.feed_consumption_week_kg },
    { name: 'الشهر الماضي', value: data.feed_consumption_month_kg },
  ]

  const mortalityData = [
    { name: 'الأسبوع الماضي', value: data.mortality_count_week },
    { name: 'الشهر الماضي', value: data.mortality_count_month },
  ]

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">نظرة عامة على المزرعة</h1>
          <p className="text-gray-600 mt-2">مؤشرات المزرعة العامة والأداء</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">الأحواض النشطة</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{data.active_ponds}</p>
              </div>
              <div className="text-4xl">🐟</div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">الدفعات النشطة</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{data.active_batches}</p>
              </div>
              <div className="text-4xl">📦</div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">الكتلة الحية الإجمالية</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {data.total_biomass_kg.toFixed(2)} كجم
                </p>
              </div>
              <div className="text-4xl">⚖️</div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">استهلاك العلف (شهري)</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {data.feed_consumption_month_kg.toFixed(2)} كجم
                </p>
              </div>
              <div className="text-4xl">🌾</div>
            </div>
          </Card>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <h2 className="text-xl font-semibold mb-4">استهلاك العلف</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={feedConsumptionData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="value" fill="#3b82f6" name="الكمية (كجم)" />
              </BarChart>
            </ResponsiveContainer>
          </Card>

          <Card>
            <h2 className="text-xl font-semibold mb-4">النفوق</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={mortalityData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="value" fill="#ef4444" name="عدد النفوق" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </div>

        {/* Additional Info */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <h3 className="text-lg font-semibold mb-3">معلومات إضافية</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">استهلاك العلف (أسبوعي):</span>
                <span className="font-semibold">{data.feed_consumption_week_kg.toFixed(2)} كجم</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">النفوق (أسبوعي):</span>
                <span className="font-semibold">{data.mortality_count_week} سمكة</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">النفوق (شهري):</span>
                <span className="font-semibold">{data.mortality_count_month} سمكة</span>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </Layout>
  )
}
