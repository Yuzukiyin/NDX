import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Plus, RefreshCw, TrendingUp
} from 'lucide-react'
import Layout from '../components/Layout'

export default function ToolsPage() {
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  // 添加交易表单状态
  const [showAddTransaction, setShowAddTransaction] = useState(false)
  const [transactionForm, setTransactionForm] = useState({
    fund_code: '',
    fund_name: '',
    transaction_date: new Date().toISOString().split('T')[0],
    transaction_type: '买入',
    amount: '',
    note: ''
  })

  const handleAddTransaction = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setMessage('')

    try {
      const apiUrl = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/funds/transactions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          ...transactionForm,
          amount: parseFloat(transactionForm.amount)
        })
      })

      if (response.ok) {
        setMessage('✅ 交易记录添加成功!')
        setTransactionForm({
          fund_code: '',
          fund_name: '',
          transaction_date: new Date().toISOString().split('T')[0],
          transaction_type: '买入',
          amount: '',
          note: ''
        })
        setShowAddTransaction(false)
      } else {
        const error = await response.json()
        setMessage(`❌ 添加失败: ${error.detail}`)
      }
    } catch (error: any) {
      setMessage(`❌ 网络错误: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleFetchNav = async () => {
    setLoading(true)
    setMessage('正在抓取历史净值...')
    try {
      const apiUrl = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000'
      const token = localStorage.getItem('access_token')
      const response = await fetch(`${apiUrl}/funds/fetch-nav`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
      })
      if (response.ok) {
        setMessage('✅ 历史净值抓取完成!')
      } else {
        const error = await response.json()
        setMessage(`❌ 抓取失败: ${error.detail}`)
      }
    } catch (error: any) {
      setMessage(`❌ 网络错误: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleUpdatePending = async () => {
    setLoading(true)
    setMessage('正在更新待确认交易...')
    try {
      const apiUrl = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000'
      const token = localStorage.getItem('access_token')
      const response = await fetch(`${apiUrl}/funds/update-pending`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      if (response.ok) {
        setMessage('✅ 待确认交易更新完成!')
      } else {
        const error = await response.json()
        setMessage(`❌ 更新失败: ${error.detail}`)
      }
    } catch (error: any) {
      setMessage(`❌ 网络错误: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const tools = [
    {
      title: '添加交易记录',
      description: '手动添加买入/卖出记录',
      icon: Plus,
      color: 'blue',
      action: () => setShowAddTransaction(true)
    },
    {
      title: '抓取历史净值',
      description: '从东方财富获取最新净值数据',
      icon: TrendingUp,
      color: 'green',
      action: handleFetchNav
    },
    {
      title: '更新待确认交易',
      description: '更新待确认交易的净值和份额',
      icon: RefreshCw,
      color: 'orange',
      action: handleUpdatePending
    }
  ]

  return (
    <Layout>
      <div className="space-y-10">
        {/* Page Header */}
        <div className="flex items-end justify-between border-b border-gray-200 pb-6">
          <div>
            <h1 className="text-5xl font-black text-gray-900 tracking-tight mb-3">工具箱</h1>
            <p className="text-gray-500 text-lg">基金管理工具集</p>
          </div>
        </div>

        {/* Message Display */}
        {message && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`p-4 rounded-2xl font-medium ${
              message.includes('✅')
                ? 'bg-green-50 text-green-800 border border-green-200'
                : 'bg-red-50 text-red-800 border border-red-200'
            }`}
          >
            {message}
          </motion.div>
        )}

        {/* Tools Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {tools.map((tool, index) => {
            const Icon = tool.icon
            const colorMap: Record<string, { bg: string; icon: string; hover: string }> = {
              blue: { bg: 'from-blue-500/20 to-blue-600/20', icon: 'text-blue-600', hover: 'hover:shadow-blue-200/50' },
              green: { bg: 'from-green-500/20 to-green-600/20', icon: 'text-green-600', hover: 'hover:shadow-green-200/50' },
              orange: { bg: 'from-orange-500/20 to-orange-600/20', icon: 'text-orange-600', hover: 'hover:shadow-orange-200/50' },
              purple: { bg: 'from-purple-500/20 to-purple-600/20', icon: 'text-purple-600', hover: 'hover:shadow-purple-200/50' }
            }
            const colors = colorMap[tool.color]

            return (
              <motion.button
                key={tool.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                whileHover={{ y: -6, scale: 1.02 }}
                onClick={tool.action}
                disabled={loading}
                className={`
                  relative bg-gradient-to-br ${colors.bg} rounded-3xl p-8 
                  border border-gray-200/60 shadow-lg ${colors.hover}
                  hover:shadow-2xl transition-all duration-300 
                  disabled:opacity-50 disabled:cursor-not-allowed
                  text-left group
                `}
              >
                <div className="relative z-10">
                  <div className={`${colors.icon.replace('text-', 'bg-')}/10 w-16 h-16 rounded-2xl flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300`}>
                    <Icon className={`w-8 h-8 ${colors.icon}`} />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">{tool.title}</h3>
                  <p className="text-gray-600">{tool.description}</p>
                </div>
              </motion.button>
            )
          })}
        </div>

        {/* Add Transaction Modal */}
        {showAddTransaction && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-white rounded-3xl p-8 max-w-2xl w-full mx-4 shadow-2xl"
            >
              <h2 className="text-3xl font-bold text-gray-900 mb-6">添加交易记录</h2>
              <form onSubmit={handleAddTransaction} className="space-y-6">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">基金代码</label>
                    <input
                      type="text"
                      required
                      value={transactionForm.fund_code}
                      onChange={(e) => setTransactionForm({ ...transactionForm, fund_code: e.target.value })}
                      className="w-full px-4 py-3 rounded-2xl border border-gray-300 focus:border-gray-900 focus:ring-2 focus:ring-gray-900/20 outline-none"
                      placeholder="例如: 021000"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">基金名称</label>
                    <input
                      type="text"
                      value={transactionForm.fund_name}
                      onChange={(e) => setTransactionForm({ ...transactionForm, fund_name: e.target.value })}
                      className="w-full px-4 py-3 rounded-2xl border border-gray-300 focus:border-gray-900 focus:ring-2 focus:ring-gray-900/20 outline-none"
                      placeholder="可选"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">交易日期</label>
                    <input
                      type="date"
                      required
                      value={transactionForm.transaction_date}
                      onChange={(e) => setTransactionForm({ ...transactionForm, transaction_date: e.target.value })}
                      className="w-full px-4 py-3 rounded-2xl border border-gray-300 focus:border-gray-900 focus:ring-2 focus:ring-gray-900/20 outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">交易类型</label>
                    <select
                      value={transactionForm.transaction_type}
                      onChange={(e) => setTransactionForm({ ...transactionForm, transaction_type: e.target.value })}
                      className="w-full px-4 py-3 rounded-2xl border border-gray-300 focus:border-gray-900 focus:ring-2 focus:ring-gray-900/20 outline-none"
                    >
                      <option value="买入">买入</option>
                      <option value="卖出">卖出</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">金额 (元)</label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    value={transactionForm.amount}
                    onChange={(e) => setTransactionForm({ ...transactionForm, amount: e.target.value })}
                    className="w-full px-4 py-3 rounded-2xl border border-gray-300 focus:border-gray-900 focus:ring-2 focus:ring-gray-900/20 outline-none"
                    placeholder="0.00"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">备注</label>
                  <textarea
                    value={transactionForm.note}
                    onChange={(e) => setTransactionForm({ ...transactionForm, note: e.target.value })}
                    className="w-full px-4 py-3 rounded-2xl border border-gray-300 focus:border-gray-900 focus:ring-2 focus:ring-gray-900/20 outline-none"
                    rows={3}
                    placeholder="可选备注信息"
                  />
                </div>

                <div className="flex gap-4">
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 bg-gray-900 text-white px-6 py-3 rounded-2xl font-bold hover:bg-gray-800 transition-colors disabled:opacity-50"
                  >
                    {loading ? '提交中...' : '提交'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowAddTransaction(false)}
                    className="flex-1 bg-gray-100 text-gray-900 px-6 py-3 rounded-2xl font-bold hover:bg-gray-200 transition-colors"
                  >
                    取消
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </div>
    </Layout>
  )
}
