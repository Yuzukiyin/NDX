import { create } from 'zustand'
import apiClient from '../lib/api'
import type { FundOverview, Transaction, NavHistory, ProfitSummary } from '../types'

interface FundState {
  funds: FundOverview[]
  transactions: Transaction[]
  profitSummary: ProfitSummary | null
  loading: boolean
  error: string | null
  
  fetchFunds: () => Promise<void>
  fetchTransactions: (fundCode?: string) => Promise<void>
  fetchNavHistory: (fundCode: string, startDate?: string, endDate?: string) => Promise<NavHistory[]>
  fetchProfitSummary: () => Promise<void>
  initializeDatabase: () => Promise<void>
  fetchHistoricalNav: (fundCodes?: string[]) => Promise<void>
  updatePending: () => Promise<void>
}

export const useFundStore = create<FundState>((set) => ({
  funds: [],
  transactions: [],
  profitSummary: null,
  loading: false,
  error: null,

  fetchFunds: async () => {
    set({ loading: true, error: null })
    try {
      const response = await apiClient.get<FundOverview[]>('/funds/overview')
      set({ funds: response.data, loading: false })
    } catch (error: any) {
      set({ error: error.response?.data?.detail || '获取基金数据失败', loading: false })
    }
  },

  fetchTransactions: async (fundCode?: string) => {
    set({ loading: true, error: null })
    try {
      const params = fundCode ? { fund_code: fundCode } : {}
      const response = await apiClient.get<Transaction[]>('/funds/transactions', { params })
      set({ transactions: response.data, loading: false })
    } catch (error: any) {
      set({ error: error.response?.data?.detail || '获取交易记录失败', loading: false })
    }
  },

  fetchNavHistory: async (fundCode: string, startDate?: string, endDate?: string) => {
    const params: any = {}
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate
    
    const response = await apiClient.get<NavHistory[]>(`/funds/nav-history/${fundCode}`, { params })
    return response.data
  },

  fetchProfitSummary: async () => {
    try {
      const response = await apiClient.get<ProfitSummary>('/funds/profit-summary')
      set({ profitSummary: response.data })
    } catch (error: any) {
      console.error('获取收益汇总失败:', error)
    }
  },

  initializeDatabase: async () => {
    set({ loading: true, error: null })
    try {
      await apiClient.post('/funds/initialize-database')
      set({ loading: false })
    } catch (error: any) {
      set({ error: error.response?.data?.detail || '初始化数据库失败', loading: false })
      throw error
    }
  },

  fetchHistoricalNav: async (fundCodes?: string[]) => {
    set({ loading: true, error: null })
    try {
      await apiClient.post('/funds/fetch-nav', fundCodes ? { fund_codes: fundCodes } : {})
      set({ loading: false })
    } catch (error: any) {
      set({ error: error.response?.data?.detail || '抓取历史净值失败', loading: false })
      throw error
    }
  },

  updatePending: async () => {
    set({ loading: true, error: null })
    try {
      await apiClient.post('/funds/update-pending')
      set({ loading: false })
    } catch (error: any) {
      set({ error: error.response?.data?.detail || '更新待确认交易失败', loading: false })
      throw error
    }
  },
}))
