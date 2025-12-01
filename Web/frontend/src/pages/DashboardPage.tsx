// Placeholder pages - simplified versions
import { useEffect } from 'react'
import { motion } from 'framer-motion'
import { useFundStore } from '../stores/fundStore'

export default function DashboardPage() {
  const { profitSummary, funds, fetchProfitSummary, fetchFunds } = useFundStore()

  useEffect(() => {
    fetchProfitSummary()
    fetchFunds()
  }, [])

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">仪表盘</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard title="总市值" value={`¥${profitSummary?.total_value.toFixed(2) || '0.00'}`} />
        <StatCard title="总收益" value={`¥${profitSummary?.total_profit.toFixed(2) || '0.00'}`} />
        <StatCard title="收益率" value={`${profitSummary?.total_return_rate.toFixed(2) || '0.00'}%`} />
        <StatCard title="基金数量" value={profitSummary?.total_funds || 0} />
      </div>
    </div>
  )
}

function StatCard({ title, value }: { title: string; value: string | number }) {
  return (
    <motion.div
      whileHover={{ scale: 1.05, y: -5 }}
      className="bg-white rounded-3xl shadow-soft p-6 elastic-animation"
    >
      <p className="text-gray-600 text-sm mb-2">{title}</p>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
    </motion.div>
  )
}
