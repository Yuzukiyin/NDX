import { useEffect } from 'react'
import { motion } from 'framer-motion'
import { useFundStore } from '../stores/fundStore'

export default function TransactionsPage() {
  const { transactions, fetchTransactions, loading } = useFundStore()

  useEffect(() => {
    fetchTransactions()
  }, [])

  if (loading) return <div>加载中...</div>

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">交易记录</h1>
      <div className="bg-white rounded-3xl shadow-soft overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-600">日期</th>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-600">基金</th>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-600">类型</th>
              <th className="px-6 py-3 text-right text-sm font-medium text-gray-600">金额</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {transactions.map((tx) => (
              <motion.tr
                key={tx.transaction_id}
                whileHover={{ backgroundColor: '#f9fafb' }}
                className="elastic-animation"
              >
                <td className="px-6 py-4 text-sm">{tx.transaction_date}</td>
                <td className="px-6 py-4 text-sm">{tx.fund_name}</td>
                <td className="px-6 py-4 text-sm">
                  <span className={`px-3 py-1 rounded-full text-xs ${
                    tx.transaction_type === '买入' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                  }`}>
                    {tx.transaction_type}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-right font-medium">¥{tx.amount.toFixed(2)}</td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
