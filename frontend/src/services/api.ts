import axios from 'axios'
import type { AxiosError } from 'axios'
import { authUtils } from '../utils/auth'
import { API_BASE_URL } from '../utils/constants'
import type {
  LoginCredentials,
  LoginResponse,
  User,
  DashboardStats,
  HealthCheck,
  Species,
  Pond,
  Batch,
  FeedType,
  FeedInventory,
  Medicine,
  MedicineInventory,
  FeedingLog,
  MortalityLog,
  BatchStatistics,
  Account,
  JournalEntry,
  TrialBalance,
  BalanceSheet,
  Harvest,
  SalesOrder,
  Invoice,
  CostPerKgReportItem,
  BatchProfitabilityItem,
  FeedEfficiencyItem,
  MortalityAnalysisItem,
  AuditLog,
  BiologicalAssetRevaluation,
  SubscriptionInfo,
  SubscriptionPlan,
  UsageStats,
  SubscriptionInvoice,
  TenantSummary,
  SaaSStats,
  FarmInfo,
} from '../types'

class ApiService {
  private api: ReturnType<typeof axios.create>

  constructor() {
    this.api = axios.create({
      baseURL: `${API_BASE_URL}/api`,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor
    this.api.interceptors.request.use(
      (config) => {
        const token = authUtils.getToken()
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor
    this.api.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const status = error.response?.status
        
        // Handle 401 Unauthorized - Token expired or invalid
        if (status === 401) {
          authUtils.clear()
          // Delay redirect to allow error message to be shown
          setTimeout(() => {
            window.location.href = '/login'
          }, 1000)
        }
        
        // Handle 403 Forbidden - No permission
        if (status === 403) {
          // Error will be handled by the calling component
        }
        
        // Handle 500+ Server errors
        if (status && status >= 500) {
          console.error('Server error:', error.response?.data)
        }
        
        return Promise.reject(error)
      }
    )
  }

  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const response = await this.api.post<LoginResponse>('/auth/login', credentials)
    return response.data
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.api.get<User>('/auth/me')
    return response.data
  }

  async refreshToken(refreshToken: string): Promise<{ access: string }> {
    const response = await this.api.post<{ access: string }>('/auth/refresh', { refresh: refreshToken })
    return response.data
  }

  async logout(): Promise<void> {
    await this.api.post('/auth/logout')
  }

  // Dashboard APIs
  async getDashboardStats(): Promise<DashboardStats> {
    const response = await this.api.get<DashboardStats>('/dashboard/stats')
    return response.data
  }

  async getFarmOverview(): Promise<{
    active_ponds: number
    active_batches: number
    total_biomass_kg: number
    feed_consumption_week_kg: number
    feed_consumption_month_kg: number
    mortality_count_week: number
    mortality_count_month: number
  }> {
    const response = await this.api.get('/dashboard/farm-overview')
    return response.data
  }

  async getBatchPerformance(): Promise<{
    batches: Array<{
      batch_id: number
      batch_number: string
      species_name: string
      pond_name: string
      fcr: number | null
      average_weight_kg: number
      mortality_rate: number
      weight_gain_rate_daily: number | null
      days_active: number
      current_count: number
      current_weight_kg: number
    }>
  }> {
    const response = await this.api.get('/dashboard/batch-performance')
    return response.data
  }

  async healthCheck(): Promise<HealthCheck> {
    const response = await this.api.get<HealthCheck>('/dashboard/health')
    return response.data
  }

  // Species APIs
  async getSpecies(): Promise<Species[]> {
    const response = await this.api.get<Species[]>('/species/')
    return response.data
  }

  // Ponds APIs
  async getPonds(): Promise<Pond[]> {
    const response = await this.api.get<Pond[]>('/ponds/')
    return response.data
  }

  async getPond(id: number): Promise<Pond> {
    const response = await this.api.get<Pond>(`/ponds/${id}`)
    return response.data
  }

  async createPond(data: Partial<Pond>): Promise<Pond> {
    const response = await this.api.post<Pond>('/ponds/', data)
    return response.data
  }

  async updatePond(id: number, data: Partial<Pond>): Promise<Pond> {
    const response = await this.api.put<Pond>(`/ponds/${id}`, data)
    return response.data
  }

  async deletePond(id: number): Promise<void> {
    await this.api.delete(`/ponds/${id}`)
  }

  // Batches APIs
  async getBatches(): Promise<Batch[]> {
    const response = await this.api.get<Batch[]>('/batches/')
    return response.data
  }

  async getBatch(id: number): Promise<Batch> {
    const response = await this.api.get<Batch>(`/batches/${id}`)
    return response.data
  }

  async createBatch(data: Partial<Batch>): Promise<Batch> {
    const response = await this.api.post<Batch>('/batches/', data)
    return response.data
  }

  async updateBatch(id: number, data: Partial<Batch>): Promise<Batch> {
    const response = await this.api.put<Batch>(`/batches/${id}`, data)
    return response.data
  }

  async deleteBatch(id: number): Promise<void> {
    await this.api.delete(`/batches/${id}`)
  }

  // Inventory APIs - Feeds
  async getFeedTypes(): Promise<FeedType[]> {
    const response = await this.api.get<FeedType[]>('/inventory/feeds/types')
    return response.data
  }

  async getFeedInventory(): Promise<FeedInventory[]> {
    const response = await this.api.get<FeedInventory[]>('/inventory/feeds')
    return response.data
  }

  async getFeedInventoryItem(id: number): Promise<FeedInventory> {
    const response = await this.api.get<FeedInventory>(`/inventory/feeds/${id}`)
    return response.data
  }

  async createFeedInventory(data: {
    feed_type_id: number
    quantity: number
    unit_price?: number
    expiry_date?: string
    location?: string
    notes?: string
  }): Promise<FeedInventory> {
    const response = await this.api.post<FeedInventory>('/inventory/feeds', data)
    return response.data
  }

  async updateFeedInventory(
    id: number,
    data: {
      quantity?: number
      unit_price?: number
      expiry_date?: string
      location?: string
      notes?: string
    }
  ): Promise<FeedInventory> {
    const response = await this.api.put<FeedInventory>(`/inventory/feeds/${id}`, data)
    return response.data
  }

  async deleteFeedInventory(id: number): Promise<void> {
    await this.api.delete(`/inventory/feeds/${id}`)
  }

  // Inventory APIs - Medicines
  async getMedicineTypes(): Promise<Medicine[]> {
    const response = await this.api.get<Medicine[]>('/inventory/medicines/types')
    return response.data
  }

  async getMedicineInventory(): Promise<MedicineInventory[]> {
    const response = await this.api.get<MedicineInventory[]>('/inventory/medicines')
    return response.data
  }

  async getMedicineInventoryItem(id: number): Promise<MedicineInventory> {
    const response = await this.api.get<MedicineInventory>(`/inventory/medicines/${id}`)
    return response.data
  }

  async createMedicineInventory(data: {
    medicine_id: number
    quantity: number
    unit_price?: number
    expiry_date?: string
    location?: string
    notes?: string
  }): Promise<MedicineInventory> {
    const response = await this.api.post<MedicineInventory>('/inventory/medicines', data)
    return response.data
  }

  async updateMedicineInventory(
    id: number,
    data: {
      quantity?: number
      unit_price?: number
      expiry_date?: string
      location?: string
      notes?: string
    }
  ): Promise<MedicineInventory> {
    const response = await this.api.put<MedicineInventory>(`/inventory/medicines/${id}`, data)
    return response.data
  }

  async deleteMedicineInventory(id: number): Promise<void> {
    await this.api.delete(`/inventory/medicines/${id}`)
  }

  // Daily Operations APIs - Feeding
  async getFeedingLogs(batchId?: number): Promise<FeedingLog[]> {
    const params = batchId ? { batch_id: batchId } : {}
    const response = await this.api.get<FeedingLog[]>('/operations/feeding', { params })
    return response.data
  }

  async getFeedingLog(id: number): Promise<FeedingLog> {
    const response = await this.api.get<FeedingLog>(`/operations/feeding/${id}`)
    return response.data
  }

  async createFeedingLog(data: {
    batch_id: number
    feed_type_id: number
    feeding_date: string
    quantity: number
    unit_price: number
    notes?: string
  }): Promise<FeedingLog> {
    const response = await this.api.post<FeedingLog>('/operations/feeding', data)
    return response.data
  }

  async updateFeedingLog(
    id: number,
    data: {
      feed_type_id?: number
      feeding_date?: string
      quantity?: number
      unit_price?: number
      notes?: string
    }
  ): Promise<FeedingLog> {
    const response = await this.api.put<FeedingLog>(`/operations/feeding/${id}`, data)
    return response.data
  }

  async deleteFeedingLog(id: number): Promise<void> {
    await this.api.delete(`/operations/feeding/${id}`)
  }

  // Daily Operations APIs - Mortality
  async getMortalityLogs(batchId?: number): Promise<MortalityLog[]> {
    const params = batchId ? { batch_id: batchId } : {}
    const response = await this.api.get<MortalityLog[]>('/operations/mortality', { params })
    return response.data
  }

  async getMortalityLog(id: number): Promise<MortalityLog> {
    const response = await this.api.get<MortalityLog>(`/operations/mortality/${id}`)
    return response.data
  }

  async createMortalityLog(data: {
    batch_id: number
    mortality_date: string
    count: number
    average_weight?: number
    cause?: string
    notes?: string
  }): Promise<MortalityLog> {
    const response = await this.api.post<MortalityLog>('/operations/mortality', data)
    return response.data
  }

  async updateMortalityLog(
    id: number,
    data: {
      mortality_date?: string
      count?: number
      average_weight?: number
      cause?: string
      notes?: string
    }
  ): Promise<MortalityLog> {
    const response = await this.api.put<MortalityLog>(`/operations/mortality/${id}`, data)
    return response.data
  }

  async deleteMortalityLog(id: number): Promise<void> {
    await this.api.delete(`/operations/mortality/${id}`)
  }

  // Daily Operations APIs - Statistics
  async getBatchStatistics(batchId: number): Promise<BatchStatistics> {
    const response = await this.api.get<BatchStatistics>(`/operations/batch-stats/${batchId}`)
    return response.data
  }

  // Accounting APIs - Accounts
  async getAccounts(accountType?: string): Promise<Account[]> {
    const params = accountType ? { account_type: accountType } : {}
    const response = await this.api.get<Account[]>('/accounting/accounts', { params })
    return response.data
  }

  async getAccount(id: number): Promise<Account> {
    const response = await this.api.get<Account>(`/accounting/accounts/${id}`)
    return response.data
  }

  // Accounting APIs - Journal Entries
  async getJournalEntries(params?: {
    start_date?: string
    end_date?: string
    reference_type?: string
  }): Promise<JournalEntry[]> {
    const response = await this.api.get<JournalEntry[]>('/accounting/journal-entries', { params })
    return response.data
  }

  async getJournalEntry(id: number): Promise<JournalEntry> {
    const response = await this.api.get<JournalEntry>(`/accounting/journal-entries/${id}`)
    return response.data
  }

  async createJournalEntry(data: {
    entry_date: string
    description: string
    reference_type?: string
    reference_id?: number
    lines: Array<{
      account_id: number
      type: 'debit' | 'credit'
      amount: number
      description?: string
    }>
  }): Promise<JournalEntry> {
    const response = await this.api.post<JournalEntry>('/accounting/journal-entries', data)
    return response.data
  }

  // Accounting APIs - Reports
  async getTrialBalance(asOfDate?: string): Promise<TrialBalance> {
    const params = asOfDate ? { as_of_date: asOfDate } : {}
    const response = await this.api.get<TrialBalance>('/accounting/trial-balance', { params })
    return response.data
  }

  async getBalanceSheet(asOfDate?: string): Promise<BalanceSheet> {
    const params = asOfDate ? { as_of_date: asOfDate } : {}
    const response = await this.api.get<BalanceSheet>('/accounting/balance-sheet', { params })
    return response.data
  }

  // Sales APIs - Harvests
  async getHarvests(params?: { batch_id?: number; status?: string }): Promise<Harvest[]> {
    const response = await this.api.get<Harvest[]>('/sales/harvests', { params })
    return response.data
  }

  async createHarvest(data: {
    batch_id: number
    harvest_date: string
    quantity_kg: number
    count: number
    average_weight?: number
    fair_value?: number
    cost_per_kg?: number
    status?: string
    notes?: string
  }): Promise<Harvest> {
    const response = await this.api.post<Harvest>('/sales/harvests', data)
    return response.data
  }

  // Sales APIs - Sales Orders
  async getSalesOrders(status?: string): Promise<SalesOrder[]> {
    const params = status ? { status } : {}
    const response = await this.api.get<SalesOrder[]>('/sales/sales-orders', { params })
    return response.data
  }

  async createSalesOrder(data: {
    order_date: string
    customer_name: string
    customer_phone?: string
    customer_address?: string
    vat_rate?: number
    lines: Array<{ harvest_id: number; quantity_kg: number; unit_price: number }>
    notes?: string
  }): Promise<SalesOrder> {
    const response = await this.api.post<SalesOrder>('/sales/sales-orders', data)
    return response.data
  }

  // Sales APIs - Invoices
  async getInvoices(status?: string): Promise<Invoice[]> {
    const params = status ? { status } : {}
    const response = await this.api.get<Invoice[]>('/sales/invoices', { params })
    return response.data
  }

  async createInvoice(sales_order_id: number): Promise<Invoice> {
    const response = await this.api.post<Invoice>('/sales/invoices', {
      sales_order_id,
    })
    return response.data
  }

  // Reports APIs
  async getCostPerKgReport(batchId?: number): Promise<CostPerKgReportItem[]> {
    const params = batchId ? { batch_id: batchId } : {}
    const response = await this.api.get<CostPerKgReportItem[]>('/reports/cost-per-kg', { params })
    return response.data
  }

  async getBatchProfitabilityReport(batchId?: number): Promise<BatchProfitabilityItem[]> {
    const params = batchId ? { batch_id: batchId } : {}
    const response = await this.api.get<BatchProfitabilityItem[]>('/reports/batch-profitability', { params })
    return response.data
  }

  async getFeedEfficiencyReport(batchId?: number): Promise<FeedEfficiencyItem[]> {
    const params = batchId ? { batch_id: batchId } : {}
    const response = await this.api.get<FeedEfficiencyItem[]>('/reports/feed-efficiency', { params })
    return response.data
  }

  async getMortalityAnalysisReport(batchId?: number): Promise<MortalityAnalysisItem[]> {
    const params = batchId ? { batch_id: batchId } : {}
    const response = await this.api.get<MortalityAnalysisItem[]>('/reports/mortality-analysis', { params })
    return response.data
  }

  // PDF Export
  async downloadInvoicePdf(invoiceId: number): Promise<Blob> {
    const response = await this.api.get(`/sales/invoices/${invoiceId}/pdf`, {
      responseType: 'blob',
    })
    return response.data
  }

  // Traceability APIs
  async getTraceabilityByInvoice(invoiceId: number): Promise<any> {
    const response = await this.api.get(`/traceability/by-invoice/${invoiceId}`)
    return response.data
  }

  async getTraceabilityByBatch(batchId: number): Promise<any> {
    const response = await this.api.get(`/traceability/by-batch/${batchId}`)
    return response.data
  }

  // Audit Log APIs
  async getAuditLogs(params?: {
    action_type?: string
    entity_type?: string
    user_id?: number
    start_date?: string
    end_date?: string
    limit?: number
  }): Promise<AuditLog[]> {
    const response = await this.api.get<AuditLog[]>('/audit/logs', { params })
    return response.data
  }

  async getAuditLog(logId: number): Promise<AuditLog> {
    const response = await this.api.get<AuditLog>(`/audit/logs/${logId}`)
    return response.data
  }

  // Biological Asset Revaluation APIs (IAS 41)
  async getBiologicalAssetRevaluations(params?: {
    batch_id?: number
    start_date?: string
    end_date?: string
  }): Promise<BiologicalAssetRevaluation[]> {
    const response = await this.api.get<BiologicalAssetRevaluation[]>('/accounting/biological-asset-revaluations', { params })
    return response.data
  }

  async getBiologicalAssetRevaluation(revaluationId: number): Promise<BiologicalAssetRevaluation> {
    const response = await this.api.get<BiologicalAssetRevaluation>(`/accounting/biological-asset-revaluations/${revaluationId}`)
    return response.data
  }

  // Billing APIs (Tenant)
  async getSubscription(): Promise<SubscriptionInfo> {
    const response = await this.api.get<SubscriptionInfo>('/billing/subscription')
    return response.data
  }

  async getUsageStats(): Promise<UsageStats> {
    const response = await this.api.get<UsageStats>('/billing/usage')
    return response.data
  }

  async getSubscriptionInvoices(): Promise<SubscriptionInvoice[]> {
    const response = await this.api.get<SubscriptionInvoice[]>('/billing/invoices')
    return response.data
  }

  async upgradePlan(planId: number): Promise<{ success: boolean; message: string }> {
    const response = await this.api.post<{ success: boolean; message: string }>('/billing/upgrade', null, {
      params: { plan_id: planId },
    })
    return response.data
  }

  // Super Admin SaaS APIs (Public schema)
  async getSaasStats(): Promise<SaaSStats> {
    const response = await this.api.get<SaaSStats>('/saas/stats')
    return response.data
  }

  async getTenants(): Promise<TenantSummary[]> {
    const response = await this.api.get<TenantSummary[]>('/saas/tenants')
    return response.data
  }

  async getPlansAdmin(): Promise<SubscriptionPlan[]> {
    const response = await this.api.get<SubscriptionPlan[]>('/saas/plans')
    return response.data
  }

  // يمكن استخدام نفس قائمة الباقات للترقية من طرف العميل
  async getPlansPublic(): Promise<SubscriptionPlan[]> {
    const response = await this.api.get<SubscriptionPlan[]>('/saas/plans')
    return response.data
  }

  async createTenant(payload: {
    farm_name: string
    subdomain: string
    email: string
    admin_username: string
    admin_email: string
    admin_password: string
    plan_id: number
    trial_days?: number
  }): Promise<{ success: boolean; tenant_id: number; subdomain: string; message: string }> {
    const response = await this.api.post('/saas/tenants/create', payload)
    return response.data
  }

  async suspendTenant(tenantId: number): Promise<{ success: boolean; message: string }> {
    const response = await this.api.post(`/saas/tenants/${tenantId}/suspend`)
    return response.data
  }

  async activateTenant(tenantId: number): Promise<{ success: boolean; message: string }> {
    const response = await this.api.post(`/saas/tenants/${tenantId}/activate`)
    return response.data
  }

  async impersonateTenant(tenantId: number): Promise<{
    access_token: string
    refresh_token: string
    tenant_id: number
    redirect_url: string
  }> {
    const response = await this.api.post(`/saas/tenants/${tenantId}/impersonate`)
    return response.data
  }

  // Farm Info
  async getFarmInfo(): Promise<FarmInfo> {
    const response = await this.api.get<FarmInfo>('/farm/')
    return response.data
  }

  async updateFarmInfo(payload: FarmInfo): Promise<FarmInfo> {
    const response = await this.api.put<FarmInfo>('/farm/', payload)
    return response.data
  }

  // Users (Tenant scope)
  async listUsers(): Promise<User[]> {
    const response = await this.api.get<User[]>('/users')
    return response.data
  }

  async createUser(data: {
    full_name: string
    username: string
    email: string
    password: string
    role: string
    phone?: string
  }): Promise<User> {
    const response = await this.api.post<User>('/users', data)
    return response.data
  }

  async updateUser(userId: number, data: Partial<{ email: string; full_name: string; role: string; phone: string; is_active: boolean }>): Promise<User> {
    const response = await this.api.put<User>(`/users/${userId}`, data)
    return response.data
  }
}

export const apiService = new ApiService()

