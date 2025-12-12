export interface User {
  id: number
  username: string
  email: string
  full_name: string
  role: string
  is_staff: boolean
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface LoginResponse {
  access: string
  refresh: string
  user: User
}

export interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
  isAuthenticated: boolean
}

// SaaS / Billing Types
export interface SubscriptionPlan {
  id: number
  name: string
  name_ar: string
  description?: string
  description_ar?: string
  price_monthly: number
  price_yearly: number
  features: Record<string, boolean>
  quotas: Record<string, number | null>
  trial_days: number
  is_featured: boolean
}

export interface SubscriptionInfo {
  id: number
  plan_name: string
  plan_name_ar: string
  status: string
  status_display: string
  billing_cycle: string
  current_period_start: string
  current_period_end: string
  remaining_days: number
  auto_renew: boolean
  features: Record<string, boolean>
  quotas: Record<string, number | null>
}

export interface UsageStats {
  ponds_used: number
  ponds_limit?: number | null
  users_used: number
  users_limit?: number | null
  storage_used_gb: number
  storage_limit_gb?: number | null
}

export interface SubscriptionInvoice {
  id: number
  invoice_number: string
  invoice_date: string
  due_date: string
  status: string
  total_amount: number
  pdf_url?: string | null
}

export interface FarmInfo {
  farm_name: string
  contact_email?: string | null
  phone?: string | null
  address?: string | null
  trade_number?: string | null
  logo_url?: string | null
  currency?: string | null
  timezone?: string | null
  notes?: string | null
}

// Super Admin / SaaS Management
export interface TenantSummary {
  id: number
  name: string
  email: string
  schema_name: string
  domain: string
  subscription_status: string
  plan_name: string
  end_date?: string | null
  is_active: boolean
  created_on: string
  user_count?: number
}

export interface SaaSStats {
  total_tenants: number
  active_subscriptions: number
  expired_subscriptions: number
  trial_subscriptions: number
  monthly_revenue: number
  tenants_expiring_soon: number
}

// Dashboard Types
export interface DashboardStats {
  total_ponds: number
  active_batches: number
  total_biomass: number
  mortality_rate: number
  total_feed_value: number
  total_medicine_value: number
}

export interface HealthCheck {
  status: string
  service: string
  version: string
}

export interface FarmOverview {
  active_ponds: number
  active_batches: number
  total_biomass_kg: number
  feed_consumption_week_kg: number
  feed_consumption_month_kg: number
  mortality_count_week: number
  mortality_count_month: number
}

export interface BatchPerformanceItem {
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
}

export interface BatchPerformance {
  batches: BatchPerformanceItem[]
}

// Biological Types
export interface Species {
  id: number
  name: string
  arabic_name: string
  scientific_name?: string
  description?: string
}

export interface Pond {
  id: number
  name: string
  pond_type: string
  capacity: number
  location?: string
  status: string
  is_active: boolean
}

export interface Batch {
  id: number
  batch_number: string
  pond: { id: number; name: string }
  species: { id: number; arabic_name: string }
  start_date: string
  initial_count: number
  initial_weight: number
  initial_cost: number
  current_count: number
  status: string
  notes?: string
}

export interface FeedType {
  id: number
  name: string
  arabic_name: string
  protein_percentage?: number
  unit: string
}

export interface FeedInventory {
  id: number
  feed_type: FeedType
  quantity: number
  unit_price: number
  expiry_date?: string
  location?: string
}

export interface Medicine {
  id: number
  name: string
  arabic_name: string
  active_ingredient?: string
  unit: string
}

export interface MedicineInventory {
  id: number
  medicine: Medicine
  quantity: number
  unit_price: number
  expiry_date?: string
  location?: string
}

// Daily Operations Types
export interface FeedingLog {
  id: number
  batch_id: number
  batch_number: string
  feed_type_id: number
  feed_type_name: string
  feeding_date: string
  quantity: number
  unit_price: number
  total_cost: number
  notes?: string
  created_by_id?: number
  created_at: string
}

export interface MortalityLog {
  id: number
  batch_id: number
  batch_number: string
  mortality_date: string
  count: number
  average_weight?: number
  cause?: string
  notes?: string
  created_by_id?: number
  created_at: string
}

export interface BatchStatistics {
  batch_id: number
  batch_number: string
  total_feed_consumed: number
  total_feed_cost: number
  total_mortality: number
  current_count: number
  current_weight: number
  average_weight: number
  mortality_rate: number
  fcr?: number
  avg_daily_feed: number
  feeding_days: number
}

// Accounting Types
export interface Account {
  id: number
  code: string
  name: string
  arabic_name: string
  account_type: string
  parent_id?: number
  description?: string
  balance: number
  is_active: boolean
}

export interface JournalEntryLine {
  id: number
  account_id: number
  account_code: string
  account_name: string
  type: 'debit' | 'credit'
  amount: number
  description?: string
}

export interface JournalEntry {
  id: number
  entry_number: string
  entry_date: string
  description: string
  reference_type?: string
  reference_id?: number
  is_posted: boolean
  total_debit: number
  total_credit: number
  lines: JournalEntryLine[]
  created_by_id?: number
  created_at: string
}

export interface TrialBalanceItem {
  account_id: number
  account_code: string
  account_name: string
  debit: number
  credit: number
  balance: number
}

export interface TrialBalance {
  date: string
  items: TrialBalanceItem[]
  total_debit: number
  total_credit: number
}

export interface BalanceSheet {
  date: string
  assets: {
    items: Array<{ code: string; name: string; balance: number }>
    total: number
  }
  liabilities: {
    items: Array<{ code: string; name: string; balance: number }>
    total: number
  }
  equity: {
    items: Array<{ code: string; name: string; balance: number }>
    total: number
  }
  total_liabilities_and_equity: number
}

// Sales Types
export interface Harvest {
  id: number
  batch_id: number
  batch_number: string
  harvest_date: string
  quantity_kg: number
  count: number
  average_weight: number
  fair_value: number
  cost_per_kg: number
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled'
  notes?: string
  created_by_id?: number
  created_at: string
}

export interface SalesOrderLine {
  id: number
  harvest_id: number
  quantity_kg: number
  unit_price: number
  line_total: number
}

export interface SalesOrder {
  id: number
  order_number: string
  order_date: string
  customer_name: string
  customer_phone?: string
  customer_address?: string
  subtotal: number
  vat_rate: number
  vat_amount: number
  total_amount: number
  status: 'draft' | 'confirmed' | 'invoiced' | 'delivered' | 'cancelled'
  notes?: string
  lines: SalesOrderLine[]
  created_by_id?: number
  created_at: string
}

export interface Invoice {
  id: number
  invoice_number: string
  sales_order_id: number
  invoice_date: string
  subtotal: number
  vat_amount: number
  total_amount: number
  status: 'draft' | 'issued' | 'paid' | 'cancelled'
  qr_code?: string
  uuid?: string
  zatca_status?: string
  created_by_id?: number
  created_at: string
}

// Reports Types
export interface CostPerKgReportItem {
  batch_id: number
  batch_number: string
  species_name: string
  total_feed_cost: number
  total_cost: number
  total_weight_kg: number
  cost_per_kg: number
  status: string
}

export interface BatchProfitabilityItem {
  batch_id: number
  batch_number: string
  species_name: string
  pond_name: string
  initial_cost: number
  total_feed_cost: number
  total_medicine_cost: number
  total_cost: number
  total_revenue: number
  profit: number
  profit_margin: number
  status: string
}

export interface FeedEfficiencyItem {
  batch_id: number
  batch_number: string
  species_name: string
  total_feed_consumed_kg: number
  total_weight_gain_kg: number
  fcr?: number
  avg_daily_feed_kg: number
  feeding_days: number
}

export interface MortalityAnalysisItem {
  batch_id: number
  batch_number: string
  species_name: string
  pond_name: string
  initial_count: number
  current_count: number
  total_mortality: number
  mortality_rate: number
  avg_daily_mortality: number
  mortality_days: number
  status: string
}

// Audit Log Types
export interface AuditLog {
  id: number
  action_type: string
  action_type_display: string
  entity_type: string
  entity_type_display: string
  entity_id?: number
  entity_description?: string
  user_id?: number
  user_name?: string
  user_ip?: string
  old_values?: Record<string, any>
  new_values?: Record<string, any>
  description?: string
  notes?: string
  created_at: string
}

// IAS 41 Biological Asset Revaluation Types
export interface BiologicalAssetRevaluation {
  id: number
  batch_id: number
  batch_number: string
  revaluation_date: string
  carrying_amount: number
  fair_value: number
  market_price_per_kg: number
  current_weight_kg: number
  current_count: number
  unrealized_gain_loss: number
  journal_entry_id?: number
  notes?: string
  created_at: string
}
