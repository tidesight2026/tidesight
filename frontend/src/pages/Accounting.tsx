import { useEffect, useState } from 'react'
import Layout from '../components/layout/Layout'
import Card from '../components/common/Card'
import SearchInput from '../components/common/SearchInput'
import { apiService } from '../services/api'
import type { Account, JournalEntry, TrialBalance, BalanceSheet } from '../types'
import LoadingSpinner from '../components/common/LoadingSpinner'
import EmptyState from '../components/common/EmptyState'

export default function Accounting() {
  const [activeTab, setActiveTab] = useState<'accounts' | 'entries' | 'trial-balance' | 'balance-sheet'>('accounts')
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')

  // Accounts
  const [accounts, setAccounts] = useState<Account[]>([])
  const [selectedAccountType, setSelectedAccountType] = useState<string>('')

  // Journal Entries
  const [journalEntries, setJournalEntries] = useState<JournalEntry[]>([])
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')

  // Reports
  const [trialBalance, setTrialBalance] = useState<TrialBalance | null>(null)
  const [balanceSheet, setBalanceSheet] = useState<BalanceSheet | null>(null)
  const [reportDate, setReportDate] = useState(new Date().toISOString().split('T')[0])
  const [loadingReport, setLoadingReport] = useState(false)

  useEffect(() => {
    if (activeTab === 'accounts') {
      fetchAccounts()
    } else if (activeTab === 'entries') {
      fetchJournalEntries()
    } else if (activeTab === 'trial-balance') {
      fetchTrialBalance()
    } else if (activeTab === 'balance-sheet') {
      fetchBalanceSheet()
    }
  }, [activeTab, selectedAccountType, startDate, endDate, reportDate])

  const fetchAccounts = async () => {
    try {
      setLoading(true)
      const data = await apiService.getAccounts(selectedAccountType || undefined)
      setAccounts(data)
    } catch (err) {
      console.error('Error fetching accounts:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchJournalEntries = async () => {
    try {
      setLoading(true)
      const params: any = {}
      if (startDate) params.start_date = startDate
      if (endDate) params.end_date = endDate
      const data = await apiService.getJournalEntries(params)
      setJournalEntries(data)
    } catch (err) {
      console.error('Error fetching journal entries:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchTrialBalance = async () => {
    try {
      setLoadingReport(true)
      const data = await apiService.getTrialBalance(reportDate)
      setTrialBalance(data)
    } catch (err) {
      console.error('Error fetching trial balance:', err)
    } finally {
      setLoadingReport(false)
    }
  }

  const fetchBalanceSheet = async () => {
    try {
      setLoadingReport(true)
      const data = await apiService.getBalanceSheet(reportDate)
      setBalanceSheet(data)
    } catch (err) {
      console.error('Error fetching balance sheet:', err)
    } finally {
      setLoadingReport(false)
    }
  }

  // Filtered accounts
  const filteredAccounts = accounts.filter((account) =>
    account.code.toLowerCase().includes(searchQuery.toLowerCase()) ||
    account.arabic_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    account.name.toLowerCase().includes(searchQuery.toLowerCase())
  )

  // Filtered journal entries
  const filteredEntries = journalEntries.filter((entry) =>
    entry.entry_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
    entry.description.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const accountTypeLabels: Record<string, string> = {
    asset: 'أصول',
    liability: 'خصوم',
    equity: 'حقوق ملكية',
    revenue: 'إيرادات',
    expense: 'مصروفات',
    biological_asset: 'أصول بيولوجية',
  }

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">المحاسبة</h1>
          <p className="mt-2 text-gray-600">إدارة الحسابات والقيود والتقارير المالية</p>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="flex gap-4 overflow-x-auto">
            <button
              onClick={() => setActiveTab('accounts')}
              className={`py-2 px-4 font-medium border-b-2 transition-colors whitespace-nowrap ${
                activeTab === 'accounts'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              📊 الحسابات
            </button>
            <button
              onClick={() => setActiveTab('entries')}
              className={`py-2 px-4 font-medium border-b-2 transition-colors whitespace-nowrap ${
                activeTab === 'entries'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              📝 القيود
            </button>
            <button
              onClick={() => setActiveTab('trial-balance')}
              className={`py-2 px-4 font-medium border-b-2 transition-colors whitespace-nowrap ${
                activeTab === 'trial-balance'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              ⚖️ ميزان المراجعة
            </button>
            <button
              onClick={() => setActiveTab('balance-sheet')}
              className={`py-2 px-4 font-medium border-b-2 transition-colors whitespace-nowrap ${
                activeTab === 'balance-sheet'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              📈 الميزانية العمومية
            </button>
          </nav>
        </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        ) : (
          <>
            {/* Accounts Tab */}
            {activeTab === 'accounts' && (
              <div>
                <Card>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <SearchInput
                      value={searchQuery}
                      onChange={setSearchQuery}
                      placeholder="ابحث في الحسابات..."
                    />
                    <select
                      value={selectedAccountType}
                      onChange={(e) => setSelectedAccountType(e.target.value)}
                      className="input-field"
                    >
                      <option value="">جميع أنواع الحسابات</option>
                      <option value="asset">أصول</option>
                      <option value="liability">خصوم</option>
                      <option value="equity">حقوق ملكية</option>
                      <option value="revenue">إيرادات</option>
                      <option value="expense">مصروفات</option>
                      <option value="biological_asset">أصول بيولوجية</option>
                    </select>
                  </div>
                </Card>

                {filteredAccounts.length === 0 ? (
                  <Card>
                    <EmptyState
                      icon="📊"
                      title="لا توجد حسابات"
                      description="ابدأ بإنشاء دليل الحسابات"
                    />
                  </Card>
                ) : (
                  <div className="space-y-4">
                    {filteredAccounts.map((account) => (
                      <Card key={account.id} className="hover:shadow-md transition-shadow">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <span className="font-mono text-sm text-gray-500">{account.code}</span>
                              <h3 className="font-semibold text-gray-900">{account.arabic_name}</h3>
                              <span className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded">
                                {accountTypeLabels[account.account_type] || account.account_type}
                              </span>
                            </div>
                            <div className="flex items-center gap-6 text-sm">
                              <div>
                                <span className="text-gray-500">الرصيد:</span>
                                <span
                                  className={`font-bold mr-2 ${
                                    account.balance >= 0 ? 'text-green-600' : 'text-red-600'
                                  }`}
                                >
                                  {account.balance.toFixed(2)}
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </Card>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Journal Entries Tab */}
            {activeTab === 'entries' && (
              <div>
                <Card>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                    <SearchInput
                      value={searchQuery}
                      onChange={setSearchQuery}
                      placeholder="ابحث في القيود..."
                    />
                    <input
                      type="date"
                      value={startDate}
                      onChange={(e) => setStartDate(e.target.value)}
                      className="input-field"
                      placeholder="من تاريخ"
                    />
                    <input
                      type="date"
                      value={endDate}
                      onChange={(e) => setEndDate(e.target.value)}
                      className="input-field"
                      placeholder="إلى تاريخ"
                    />
                  </div>
                </Card>

                {filteredEntries.length === 0 ? (
                  <Card>
                    <EmptyState
                      icon="📝"
                      title="لا توجد قيود محاسبية"
                      description="القيود تُنشأ تلقائياً عند تسجيل العمليات"
                    />
                  </Card>
                ) : (
                  <div className="space-y-4">
                    {filteredEntries.map((entry) => (
                      <Card key={entry.id} className="hover:shadow-md transition-shadow">
                        <div className="mb-4">
                          <div className="flex items-center justify-between mb-2">
                            <div>
                              <h3 className="font-semibold text-gray-900">{entry.entry_number}</h3>
                              <p className="text-sm text-gray-600">{entry.description}</p>
                            </div>
                            <div className="text-left">
                              <p className="text-sm text-gray-500">
                                {new Date(entry.entry_date).toLocaleDateString('ar-SA')}
                              </p>
                              {entry.reference_type && (
                                <p className="text-xs text-gray-400">
                                  {entry.reference_type}: {entry.reference_id}
                                </p>
                              )}
                            </div>
                          </div>
                        </div>
                        <div className="space-y-2">
                          {entry.lines.map((line, idx) => (
                            <div
                              key={idx}
                              className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded"
                            >
                              <div className="flex items-center gap-4">
                                <span className="font-mono text-sm text-gray-500">{line.account_code}</span>
                                <span className="text-sm">{line.account_name}</span>
                                {line.description && (
                                  <span className="text-xs text-gray-400">({line.description})</span>
                                )}
                              </div>
                              <div className="flex gap-6">
                                {line.type === 'debit' ? (
                                  <span className="font-medium text-blue-600 w-24 text-left">
                                    {line.amount.toFixed(2)}
                                  </span>
                                ) : (
                                  <span className="text-gray-400 w-24 text-left">-</span>
                                )}
                                {line.type === 'credit' ? (
                                  <span className="font-medium text-green-600 w-24 text-left">
                                    {line.amount.toFixed(2)}
                                  </span>
                                ) : (
                                  <span className="text-gray-400 w-24 text-left">-</span>
                                )}
                              </div>
                            </div>
                          ))}
                          <div className="flex justify-end gap-6 pt-2 border-t border-gray-200">
                            <span className="font-bold text-blue-600 w-24 text-left">
                              {entry.total_debit.toFixed(2)}
                            </span>
                            <span className="font-bold text-green-600 w-24 text-left">
                              {entry.total_credit.toFixed(2)}
                            </span>
                          </div>
                        </div>
                      </Card>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Trial Balance Tab */}
            {activeTab === 'trial-balance' && (
              <div>
                <Card>
                  <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-bold text-gray-900">ميزان المراجعة</h2>
                    <div className="flex gap-2">
                      <input
                        type="date"
                        value={reportDate}
                        onChange={(e) => setReportDate(e.target.value)}
                        className="input-field"
                      />
                      <button
                        onClick={fetchTrialBalance}
                        className="btn-primary"
                        disabled={loadingReport}
                      >
                        {loadingReport ? 'جاري التحميل...' : 'تحديث'}
                      </button>
                    </div>
                  </div>
                </Card>

                {loadingReport ? (
                  <div className="flex justify-center py-12">
                    <LoadingSpinner size="lg" />
                  </div>
                ) : trialBalance ? (
                  <Card>
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">رقم الحساب</th>
                            <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">اسم الحساب</th>
                            <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">مدين</th>
                            <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">دائن</th>
                            <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">الرصيد</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {trialBalance.items.map((item, idx) => (
                            <tr key={idx} className="hover:bg-gray-50">
                              <td className="px-4 py-3 text-sm font-mono text-gray-500">{item.account_code}</td>
                              <td className="px-4 py-3 text-sm text-gray-900">{item.account_name}</td>
                              <td className="px-4 py-3 text-sm text-gray-600 text-left">
                                {item.debit > 0 ? item.debit.toFixed(2) : '-'}
                              </td>
                              <td className="px-4 py-3 text-sm text-gray-600 text-left">
                                {item.credit > 0 ? item.credit.toFixed(2) : '-'}
                              </td>
                              <td className="px-4 py-3 text-sm font-medium text-left">
                                <span
                                  className={
                                    item.balance >= 0 ? 'text-green-600' : 'text-red-600'
                                  }
                                >
                                  {item.balance.toFixed(2)}
                                </span>
                              </td>
                            </tr>
                          ))}
                          <tr className="bg-gray-100 font-bold">
                            <td colSpan={2} className="px-4 py-3 text-sm text-gray-900">
                              الإجمالي
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-900 text-left">
                              {trialBalance.total_debit.toFixed(2)}
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-900 text-left">
                              {trialBalance.total_credit.toFixed(2)}
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-900 text-left">-</td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                    <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                      <p className="text-sm text-blue-900">
                        ✅ الميزان متوازن: مجموع المدين ({trialBalance.total_debit.toFixed(2)}) = مجموع الدائن ({trialBalance.total_credit.toFixed(2)})
                      </p>
                    </div>
                  </Card>
                ) : (
                  <Card>
                    <EmptyState icon="⚖️" title="لا توجد بيانات" description="اختر تاريخ لعرض الميزان" />
                  </Card>
                )}
              </div>
            )}

            {/* Balance Sheet Tab */}
            {activeTab === 'balance-sheet' && (
              <div>
                <Card>
                  <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-bold text-gray-900">الميزانية العمومية</h2>
                    <div className="flex gap-2">
                      <input
                        type="date"
                        value={reportDate}
                        onChange={(e) => setReportDate(e.target.value)}
                        className="input-field"
                      />
                      <button
                        onClick={fetchBalanceSheet}
                        className="btn-primary"
                        disabled={loadingReport}
                      >
                        {loadingReport ? 'جاري التحميل...' : 'تحديث'}
                      </button>
                    </div>
                  </div>
                </Card>

                {loadingReport ? (
                  <div className="flex justify-center py-12">
                    <LoadingSpinner size="lg" />
                  </div>
                ) : balanceSheet ? (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Assets */}
                    <Card>
                      <h3 className="text-lg font-bold text-gray-900 mb-4">الأصول</h3>
                      <div className="space-y-2">
                        {balanceSheet.assets.items.map((item, idx) => (
                          <div key={idx} className="flex justify-between py-2 border-b border-gray-100">
                            <div>
                              <span className="text-sm font-mono text-gray-500 mr-2">{item.code}</span>
                              <span className="text-sm text-gray-700">{item.name}</span>
                            </div>
                            <span className="text-sm font-medium text-gray-900">
                              {item.balance.toFixed(2)}
                            </span>
                          </div>
                        ))}
                        <div className="flex justify-between pt-2 border-t-2 border-gray-300 font-bold">
                          <span>إجمالي الأصول</span>
                          <span>{balanceSheet.assets.total.toFixed(2)}</span>
                        </div>
                      </div>
                    </Card>

                    {/* Liabilities & Equity */}
                    <Card>
                      <div className="space-y-6">
                        <div>
                          <h3 className="text-lg font-bold text-gray-900 mb-4">الخصوم</h3>
                          <div className="space-y-2">
                            {balanceSheet.liabilities.items.map((item, idx) => (
                              <div key={idx} className="flex justify-between py-2 border-b border-gray-100">
                                <div>
                                  <span className="text-sm font-mono text-gray-500 mr-2">{item.code}</span>
                                  <span className="text-sm text-gray-700">{item.name}</span>
                                </div>
                                <span className="text-sm font-medium text-gray-900">
                                  {item.balance.toFixed(2)}
                                </span>
                              </div>
                            ))}
                            <div className="flex justify-between pt-2 border-t-2 border-gray-300 font-bold">
                              <span>إجمالي الخصوم</span>
                              <span>{balanceSheet.liabilities.total.toFixed(2)}</span>
                            </div>
                          </div>
                        </div>

                        <div>
                          <h3 className="text-lg font-bold text-gray-900 mb-4">حقوق الملكية</h3>
                          <div className="space-y-2">
                            {balanceSheet.equity.items.map((item, idx) => (
                              <div key={idx} className="flex justify-between py-2 border-b border-gray-100">
                                <div>
                                  <span className="text-sm font-mono text-gray-500 mr-2">{item.code}</span>
                                  <span className="text-sm text-gray-700">{item.name}</span>
                                </div>
                                <span className="text-sm font-medium text-gray-900">
                                  {item.balance.toFixed(2)}
                                </span>
                              </div>
                            ))}
                            <div className="flex justify-between pt-2 border-t-2 border-gray-300 font-bold">
                              <span>إجمالي حقوق الملكية</span>
                              <span>{balanceSheet.equity.total.toFixed(2)}</span>
                            </div>
                          </div>
                        </div>

                        <div className="pt-4 border-t-2 border-gray-400">
                          <div className="flex justify-between font-bold text-lg">
                            <span>إجمالي الخصوم + حقوق الملكية</span>
                            <span>{balanceSheet.total_liabilities_and_equity.toFixed(2)}</span>
                          </div>
                          <div className="mt-2 p-2 bg-green-50 border border-green-200 rounded">
                            <p className="text-sm text-green-900">
                              ✅ الميزان متوازن: الأصول ({balanceSheet.assets.total.toFixed(2)}) = الخصوم + حقوق الملكية ({balanceSheet.total_liabilities_and_equity.toFixed(2)})
                            </p>
                          </div>
                        </div>
                      </div>
                    </Card>
                  </div>
                ) : (
                  <Card>
                    <EmptyState icon="📈" title="لا توجد بيانات" description="اختر تاريخ لعرض الميزانية" />
                  </Card>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </Layout>
  )
}
