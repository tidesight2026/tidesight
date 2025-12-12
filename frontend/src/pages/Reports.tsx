import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import Layout from '../components/layout/Layout'
import Card from '../components/common/Card'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { apiService } from '../services/api'
import type {
  CostPerKgReportItem,
  BatchProfitabilityItem,
  FeedEfficiencyItem,
  MortalityAnalysisItem,
} from '../types'
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts'

export default function Reports() {
  const { t } = useTranslation()
  const [activeTab, setActiveTab] = useState<'cost' | 'profitability' | 'efficiency' | 'mortality'>('cost')
  const [loading, setLoading] = useState(false)
  
  // Reports data
  const [costPerKg, setCostPerKg] = useState<CostPerKgReportItem[]>([])
  const [profitability, setProfitability] = useState<BatchProfitabilityItem[]>([])
  const [feedEfficiency, setFeedEfficiency] = useState<FeedEfficiencyItem[]>([])
  const [mortalityAnalysis, setMortalityAnalysis] = useState<MortalityAnalysisItem[]>([])

  useEffect(() => {
    loadReport()
  }, [activeTab])

  const loadReport = async () => {
    setLoading(true)
    try {
      switch (activeTab) {
        case 'cost':
          const costData = await apiService.getCostPerKgReport()
          setCostPerKg(costData)
          break
        case 'profitability':
          const profitData = await apiService.getBatchProfitabilityReport()
          setProfitability(profitData)
          break
        case 'efficiency':
          const efficiencyData = await apiService.getFeedEfficiencyReport()
          setFeedEfficiency(efficiencyData)
          break
        case 'mortality':
          const mortalityData = await apiService.getMortalityAnalysisReport()
          setMortalityAnalysis(mortalityData)
          break
      }
    } catch (error) {
      console.error('Error loading report:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{t('reports.title', 'التقارير')}</h1>
          <p className="mt-2 text-gray-600">عرض تقارير الأداء والربحية</p>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8" aria-label="Tabs">
            <button
              onClick={() => setActiveTab('cost')}
              className={`${
                activeTab === 'cost'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              تكلفة الكيلو
            </button>
            <button
              onClick={() => setActiveTab('profitability')}
              className={`${
                activeTab === 'profitability'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              ربحية الدفعات
            </button>
            <button
              onClick={() => setActiveTab('efficiency')}
              className={`${
                activeTab === 'efficiency'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              كفاءة الأعلاف
            </button>
            <button
              onClick={() => setActiveTab('mortality')}
              className={`${
                activeTab === 'mortality'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              تحليل النفوق
            </button>
          </nav>
        </div>

        {/* Report Content */}
        {loading ? (
          <div className="flex justify-center py-12">
            <LoadingSpinner />
          </div>
        ) : (
          <>
            {/* Cost per Kg Report */}
            {activeTab === 'cost' && (
              <div className="space-y-6">
                <Card title="تقرير تكلفة الكيلوجرام">
                  {costPerKg.length === 0 ? (
                    <p className="text-gray-500 text-center py-8">لا توجد بيانات</p>
                  ) : (
                    <>
                      <div className="mb-6">
                        <ResponsiveContainer width="100%" height={300}>
                          <BarChart data={costPerKg}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="batch_number" angle={-15} textAnchor="end" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Bar dataKey="cost_per_kg" fill="#3b82f6" name="التكلفة لكل كجم (ريال)" />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                      <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                          <thead className="bg-gray-50">
                            <tr>
                              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">الدفعة</th>
                              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">النوع</th>
                              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">التكلفة الإجمالية</th>
                              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">الوزن (كجم)</th>
                              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">التكلفة لكل كجم</th>
                            </tr>
                          </thead>
                          <tbody className="bg-white divide-y divide-gray-200">
                            {costPerKg.map((item) => (
                              <tr key={item.batch_id}>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{item.batch_number}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.species_name}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.total_cost.toFixed(2)} ريال</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.total_weight_kg.toFixed(2)}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-primary-600">{item.cost_per_kg.toFixed(2)} ريال</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </>
                  )}
                </Card>
              </div>
            )}

            {/* Profitability Report */}
            {activeTab === 'profitability' && (
              <div className="space-y-6">
                <Card title="تقرير ربحية الدفعات">
                  {profitability.length === 0 ? (
                    <p className="text-gray-500 text-center py-8">لا توجد بيانات</p>
                  ) : (
                    <>
                      <div className="mb-6">
                        <ResponsiveContainer width="100%" height={300}>
                          <BarChart data={profitability}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="batch_number" angle={-15} textAnchor="end" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Bar dataKey="total_cost" fill="#ef4444" name="التكلفة (ريال)" />
                            <Bar dataKey="total_revenue" fill="#10b981" name="الإيرادات (ريال)" />
                            <Bar dataKey="profit" fill="#3b82f6" name="الربح (ريال)" />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                      <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                          <thead className="bg-gray-50">
                            <tr>
                              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">الدفعة</th>
                              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">التكلفة</th>
                              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">الإيرادات</th>
                              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">الربح</th>
                              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">نسبة الربح</th>
                            </tr>
                          </thead>
                          <tbody className="bg-white divide-y divide-gray-200">
                            {profitability.map((item) => (
                              <tr key={item.batch_id}>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{item.batch_number}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.total_cost.toFixed(2)} ريال</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.total_revenue.toFixed(2)} ريال</td>
                                <td className={`px-6 py-4 whitespace-nowrap text-sm font-bold ${item.profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                  {item.profit.toFixed(2)} ريال
                                </td>
                                <td className={`px-6 py-4 whitespace-nowrap text-sm font-bold ${item.profit_margin >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                  {item.profit_margin.toFixed(2)}%
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </>
                  )}
                </Card>
              </div>
            )}

            {/* Feed Efficiency Report */}
            {activeTab === 'efficiency' && (
              <div className="space-y-6">
                <Card title="تقرير كفاءة الأعلاف (FCR)">
                  {feedEfficiency.length === 0 ? (
                    <p className="text-gray-500 text-center py-8">لا توجد بيانات</p>
                  ) : (
                    <>
                      <div className="mb-6">
                        <ResponsiveContainer width="100%" height={300}>
                          <LineChart data={feedEfficiency.filter(item => item.fcr)}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="batch_number" angle={-15} textAnchor="end" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Line type="monotone" dataKey="fcr" stroke="#3b82f6" name="FCR" />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                      <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                          <thead className="bg-gray-50">
                            <tr>
                              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">الدفعة</th>
                              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">العلف المستهلك (كجم)</th>
                              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">زيادة الوزن (كجم)</th>
                              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">FCR</th>
                              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">متوسط العلف اليومي</th>
                            </tr>
                          </thead>
                          <tbody className="bg-white divide-y divide-gray-200">
                            {feedEfficiency.map((item) => (
                              <tr key={item.batch_id}>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{item.batch_number}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.total_feed_consumed_kg.toFixed(2)}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.total_weight_gain_kg.toFixed(2)}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-primary-600">
                                  {item.fcr ? item.fcr.toFixed(2) : 'غير متاح'}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.avg_daily_feed_kg.toFixed(2)} كجم/يوم</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </>
                  )}
                </Card>
              </div>
            )}

            {/* Mortality Analysis Report */}
            {activeTab === 'mortality' && (
              <div className="space-y-6">
                <Card title="تحليل النفوق">
                  {mortalityAnalysis.length === 0 ? (
                    <p className="text-gray-500 text-center py-8">لا توجد بيانات</p>
                  ) : (
                    <>
                      <div className="mb-6">
                        <ResponsiveContainer width="100%" height={300}>
                          <BarChart data={mortalityAnalysis}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="batch_number" angle={-15} textAnchor="end" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Bar dataKey="mortality_rate" fill="#ef4444" name="معدل النفوق (%)" />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                      <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                          <thead className="bg-gray-50">
                            <tr>
                              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">الدفعة</th>
                              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">العدد الأولي</th>
                              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">العدد الحالي</th>
                              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">إجمالي النفوق</th>
                              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">معدل النفوق</th>
                              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">متوسط النفوق اليومي</th>
                            </tr>
                          </thead>
                          <tbody className="bg-white divide-y divide-gray-200">
                            {mortalityAnalysis.map((item) => (
                              <tr key={item.batch_id}>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{item.batch_number}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.initial_count}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.current_count}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-red-600 font-medium">{item.total_mortality}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-red-600">{item.mortality_rate.toFixed(2)}%</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.avg_daily_mortality.toFixed(2)}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </>
                  )}
                </Card>
              </div>
            )}
          </>
        )}
      </div>
    </Layout>
  )
}
