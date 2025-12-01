import { useEffect } from 'react'
import { motion } from 'framer-motion'
import { useFundStore } from '../stores/fundStore'

export default function FundsPage() {
  const { funds, fetchFunds, loading } = useFundStore()

  useEffect(() => {
    fetchFunds()
  }, [])

  if (loading) return <div>加载中...</div>

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">我的基金</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {funds.map((fund) => (
          <FundCard key={fund.fund_code} fund={fund} />
        ))}
      </div>
    </div>
  )
}

function FundCard({ fund }: { fund: any }) {
  const profitColor = fund.profit >= 0 ? 'text-green-600' : 'text-red-600'
  
  return (
    <motion.div
      whileHover={{ scale: 1.03, y: -5 }}
      className="bg-white rounded-3xl shadow-soft p-6 elastic-animation"
    >
      <h3 className="font-bold text-lg mb-2">{fund.fund_name}</h3>
      <p className="text-gray-600 text-sm mb-4">{fund.fund_code}</p>
      <div className="space-y-2">
        <div className="flex justify-between">
          <span className="text-gray-600">持有份额</span>
          <span className="font-medium">{fund.total_shares.toFixed(2)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-600">当前市值</span>
          <span className="font-medium">¥{fund.current_value.toFixed(2)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-600">总收益</span>
          <span className={`font-bold ${profitColor}`}>¥{fund.profit.toFixed(2)}</span>
        </div>
      </div>
    </motion.div>
  )
}
