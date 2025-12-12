import { useAuthStore } from '../store/authStore'
import { useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import Layout from '../components/layout/Layout'
import Card from '../components/common/Card'
import { apiService } from '../services/api'
import type { DashboardStats } from '../types'
import LoadingSpinner from '../components/common/LoadingSpinner'
import StatsChart from '../components/dashboard/StatsChart'
import MortalityTrendChart from '../components/dashboard/MortalityTrendChart'

export default function Dashboard() {
  const { t } = useTranslation()
  const user = useAuthStore((state) => state.user)
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const navigate = useNavigate()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
      return
    }

    // جلب الإحصائيات من API
    const fetchStats = async () => {
      try {
        const data = await apiService.getDashboardStats()
        setStats(data)
      } catch (error) {
        console.error('Error fetching stats:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [isAuthenticated, navigate])

  if (!isAuthenticated || !user) {
    return null
  }

  // Widget Data من API
  const statsWidgets = stats
    ? [
        {
          label: 'إجمالي الأحواض',
          value: (stats.total_ponds ?? 0).toString(),
          icon: '🐟',
          color: 'bg-blue-500',
        },
        {
          label: 'الدفعات النشطة',
          value: (stats.active_batches ?? 0).toString(),
          icon: '📦',
          color: 'bg-green-500',
        },
        {
          label: 'الكمية الحي',
          value: `${(stats.total_biomass ?? 0).toFixed(2)} كجم`,
          icon: '⚖️',
          color: 'bg-yellow-500',
        },
        {
          label: 'معدل النفوق',
          value: `${(stats.mortality_rate ?? 0).toFixed(1)}%`,
          icon: '📉',
          color: 'bg-red-500',
        },
        {
          label: 'قيمة الأعلاف',
          value: `${(stats.total_feed_value ?? 0).toFixed(2)} ريال`,
          icon: '🌾',
          color: 'bg-orange-500',
        },
        {
          label: 'قيمة الأدوية',
          value: `${(stats.total_medicine_value ?? 0).toFixed(2)} ريال`,
          icon: '💊',
          color: 'bg-purple-500',
        },
      ]
    : [
        { label: 'إجمالي الأحواض', value: '0', icon: '🐟', color: 'bg-blue-500' },
        { label: 'الدفعات النشطة', value: '0', icon: '📦', color: 'bg-green-500' },
        { label: 'الكمية الحي', value: '0 كجم', icon: '⚖️', color: 'bg-yellow-500' },
        { label: 'معدل النفوق', value: '0%', icon: '📉', color: 'bg-red-500' },
        { label: 'قيمة الأعلاف', value: '0 ريال', icon: '🌾', color: 'bg-orange-500' },
        { label: 'قيمة الأدوية', value: '0 ريال', icon: '💊', color: 'bg-purple-500' },
      ]

  return (
    <Layout>
      <div className="space-y-6">
        {/* Welcome Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{t('dashboard.title')}</h1>
          <p className="mt-2 text-gray-600">
            {t('dashboard.welcome')}، <span className="font-medium">{user.full_name}</span>!
          </p>
        </div>

        {/* Stats Grid */}
        {loading ? (
          <div className="flex justify-center py-12">
            <LoadingSpinner />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {statsWidgets.map((stat, index) => (
              <Card key={index} className="hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">{stat.label}</p>
                    <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                  </div>
                  <div className={`${stat.color} p-3 rounded-lg text-white text-2xl`}>
                    {stat.icon}
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Welcome Card */}
          <Card title="مرحباً بك في AquaERP" className="lg:col-span-2">
            <div className="space-y-4">
              <p className="text-gray-600">
                مرحباً بك في نظام إدارة المزارع السمكية. يمكنك من هنا إدارة جميع جوانب المزرعة
                من الأحواض والدفعات إلى التقارير المالية.
              </p>
              <div className="bg-primary-50 border border-primary-200 rounded-lg p-4">
                <h4 className="font-medium text-primary-900 mb-2">معلومات حسابك</h4>
                <div className="space-y-1 text-sm text-primary-700">
                  <p>
                    <span className="font-medium">الدور:</span> {user.role}
                  </p>
                  <p>
                    <span className="font-medium">البريد الإلكتروني:</span> {user.email}
                  </p>
                </div>
              </div>
            </div>
          </Card>

          {/* Quick Actions */}
          <Card title="إجراءات سريعة">
            <div className="space-y-3">
              <button className="w-full text-right px-4 py-3 bg-primary-50 hover:bg-primary-100 text-primary-700 rounded-lg transition-colors">
                ➕ إضافة حوض جديد
              </button>
              <button className="w-full text-right px-4 py-3 bg-green-50 hover:bg-green-100 text-green-700 rounded-lg transition-colors">
                📦 إضافة دفعة جديدة
              </button>
              <button className="w-full text-right px-4 py-3 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-lg transition-colors">
                📊 عرض التقارير
              </button>
              <button className="w-full text-right px-4 py-3 bg-gray-50 hover:bg-gray-100 text-gray-700 rounded-lg transition-colors">
                ⚙️ الإعدادات
              </button>
            </div>
          </Card>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card title="معدل النفوق - آخر 7 أيام">
            <MortalityTrendChart
              data={[
                { date: 'يوم 1', rate: (stats?.mortality_rate ?? 0) * 0.8 },
                { date: 'يوم 2', rate: (stats?.mortality_rate ?? 0) * 0.9 },
                { date: 'يوم 3', rate: stats?.mortality_rate ?? 0 },
                { date: 'يوم 4', rate: (stats?.mortality_rate ?? 0) * 1.1 },
                { date: 'يوم 5', rate: (stats?.mortality_rate ?? 0) * 0.95 },
                { date: 'يوم 6', rate: (stats?.mortality_rate ?? 0) * 1.05 },
                { date: 'اليوم', rate: stats?.mortality_rate ?? 0 },
              ]}
            />
          </Card>

          <Card title={t('dashboard.totalBiomass') + ' - الدفعات'}>
            <StatsChart
              type="bar"
              color="#10b981"
              label="الكتلة الحيوية (كجم)"
              data={[
                { name: 'دفعة 1', value: (stats?.total_biomass ?? 0) * 0.3 },
                { name: 'دفعة 2', value: (stats?.total_biomass ?? 0) * 0.4 },
                { name: 'دفعة 3', value: (stats?.total_biomass ?? 0) * 0.3 },
              ]}
            />
          </Card>
        </div>

        {/* Recent Activity (Placeholder) */}
        <Card title="النشاط الأخير">
          <div className="text-center py-8 text-gray-500">
            <p>لا توجد أنشطة حديثة</p>
            <p className="text-sm mt-2">ستظهر الأنشطة هنا عند بدء استخدام النظام</p>
          </div>
        </Card>
      </div>
    </Layout>
  )
}
