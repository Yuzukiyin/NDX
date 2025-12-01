export interface User {
  id: number
  email: string
  username: string
  is_active: boolean
  is_verified: boolean
  created_at: string
  last_login: string | null
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  username: string
  password: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface FundOverview {
  fund_code: string
  fund_name: string
  total_shares: number
  total_cost: number
  average_buy_nav: number
  current_nav: number
  current_value: number
  profit: number
  profit_rate: number
  first_buy_date: string | null
  last_transaction_date: string | null
  last_nav_date: string | null
  daily_growth_rate: number
}

export interface Transaction {
  transaction_id: number
  fund_code: string
  fund_name: string
  transaction_date: string
  nav_date: string | null
  transaction_type: string
  target_amount: number | null
  shares: number | null
  unit_nav: number | null
  amount: number
  note: string | null
  created_at: string
}

export interface NavHistory {
  price_date: string
  unit_nav: number
  cumulative_nav: number | null
  daily_growth_rate: number | null
}

export interface ProfitSummary {
  total_funds: number
  total_shares: number
  total_cost: number
  total_value: number
  total_profit: number
  total_return_rate: number
}
