import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Plus, ArrowUpDown, ChevronLeft, ChevronRight, X, Calendar } from 'lucide-react'
import { useFundStore } from '../stores/fundStore'
import Layout from '../components/Layout'
import apiClient from '../lib/api'

export default function TransactionsPage() {
  const { transactions, fetchTransactions } = useFundStore()
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)
  const [currentPage, setCurrentPage] = useState(1)
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc')
  const itemsPerPage = 15

  const [formData, setFormData] = useState({
    fund_code: '',
    fund_name: '',
    transaction_date: new Date().toISOString().split('T')[0],
    amount: '',
    transaction_type: '\u4e70\u5165',
    note: ''
  })
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchTransactions()
  }, [fetchTransactions])

  const sortedTransactions = [...transactions].sort((a, b) => {
    const dateA = new Date(a.transaction_date).getTime()
    const dateB = new Date(b.transaction_date).getTime()
    return sortDirection === 'desc' ? dateB - dateA : dateA - dateB
  })

  const totalPages = Math.ceil(sortedTransactions.length / itemsPerPage)
  const paginatedTransactions = sortedTransactions.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  )

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await apiClient.post('/funds/transactions', {
        fund_code: formData.fund_code,
        fund_name: formData.fund_name,
        transaction_date: formData.transaction_date,
        amount: parseFloat(formData.amount),
        transaction_type: formData.transaction_type,
        note: formData.note
      })
      await fetchTransactions()
      setFormData({
        fund_code: '',
        fund_name: '',
        transaction_date: new Date().toISOString().split('T')[0],
        amount: '',
        transaction_type: '买入',
        note: ''
      })
      setIsAddModalOpen(false)
    } catch (error) {
      console.error('Failed to add transaction:', error)
      alert('添加交易失败')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (confirm('确认删除此交易记录？')) {
      try {
        await apiClient.delete(`/funds/transactions/${id}`)
        await fetchTransactions()
      } catch (error) {
        console.error('Failed to delete transaction:', error)
        alert('删除失败')
      }
    }
  }

  return (
    <Layout>
      <div className="space-y-10">
        {/* Page Header */}
        <div className="flex items-end justify-between border-b border-gray-200 pb-6">
          <div>
            <h1 className="text-5xl font-black text-gray-900 tracking-tight mb-3">交易</h1>
            <p className="text-gray-500 text-lg">记录和管理您的交易历史</p>
          </div>
          <button
            onClick={() => setIsAddModalOpen(true)}
            className="px-6 py-3.5 bg-gray-900 text-white rounded-2xl font-bold text-sm flex items-center gap-2.5 hover:bg-gray-800 transition-all shadow-lg hover:shadow-xl hover:scale-105 duration-300"
          >
            <Plus className="w-5 h-5" />
            添加交易
          </button>
        </div>

        {/* Transactions Table */}
        <div className="bg-white/80 backdrop-blur-sm rounded-3xl border border-gray-200/60 shadow-lg overflow-hidden">
          {/* Table Header */}
          <div className="bg-gray-50 px-8 py-5 border-b border-gray-200">
            <div className="grid grid-cols-7 gap-6 text-sm font-bold text-gray-700 uppercase tracking-wide">
              <div
                className="flex items-center gap-2 cursor-pointer hover:text-gray-900 transition-colors"
                onClick={() => setSortDirection(sortDirection === 'desc' ? 'asc' : 'desc')}
              >
                <Calendar className="w-4 h-4" />
                日期
                <ArrowUpDown className="w-4 h-4" />
              </div>
              <div>基金代码</div>
              <div>基金名称</div>
              <div>类型</div>
              <div className="text-right">份额</div>
              <div className="text-right">净值</div>
              <div className="text-right">金额</div>
            </div>
          </div>

          {/* Table Body */}
          <div className="divide-y divide-gray-100">
            <AnimatePresence mode="popLayout">
              {paginatedTransactions.map((transaction, index) => (
                <motion.div
                  key={transaction.transaction_id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, x: -30 }}
                  transition={{
                    duration: 0.4,
                    delay: index * 0.03,
                    ease: [0.16, 1, 0.3, 1],
                  }}
                  className="grid grid-cols-7 gap-6 px-8 py-5 hover:bg-gray-50/70 transition-colors group"
                >
                  <div className="text-sm font-medium text-gray-900">
                    {new Date(transaction.transaction_date).toLocaleDateString('zh-CN')}
                  </div>
                  <div className="text-sm font-mono text-gray-700 font-semibold">
                    {transaction.fund_code}
                  </div>
                  <div className="text-sm text-gray-900 font-medium truncate">
                    {transaction.fund_name}
                  </div>
                  <div>
                    <span
                      className={`
                        inline-flex px-3 py-1.5 rounded-full text-xs font-bold uppercase tracking-wide
                        ${transaction.transaction_type === 'buy'
                          ? 'bg-blue-100 text-blue-700'
                          : 'bg-orange-100 text-orange-700'
                        }
                      `}
                    >
                      {transaction.transaction_type === 'buy' ? '买入' : '卖出'}
                    </span>
                  </div>
                  <div className="text-sm text-right font-bold text-gray-900">
                    {transaction.shares?.toFixed(2) || '-'}
                  </div>
                  <div className="text-sm text-right text-gray-700 font-medium">
                    ¥{transaction.unit_nav?.toFixed(4) || '-'}
                  </div>
                  <div className="text-sm text-right font-bold text-gray-900 flex items-center justify-end gap-3">
                    ¥{transaction.amount.toFixed(2)}
                    <button
                      onClick={() => handleDelete(transaction.transaction_id)}
                      className="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 hover:bg-red-50 rounded-lg"
                    >
                      <X className="w-4 h-4 text-red-600" />
                    </button>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="px-8 py-5 border-t border-gray-200 flex items-center justify-between bg-gray-50/50">
              <p className="text-sm text-gray-600 font-medium">
                共 {sortedTransactions.length} 条记录，第 {currentPage} / {totalPages} 页
              </p>
              <div className="flex items-center gap-3">
                <button
                  onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="px-4 py-2 bg-white border border-gray-300 rounded-xl font-semibold text-sm text-gray-700 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <span className="text-sm font-bold text-gray-900 min-w-[60px] text-center">
                  {currentPage} / {totalPages}
                </span>
                <button
                  onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className="px-4 py-2 bg-white border border-gray-300 rounded-xl font-semibold text-sm text-gray-700 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            </div>
          )}

          {/* Empty State */}
          {transactions.length === 0 && (
            <div className="text-center py-20">
              <p className="text-gray-500 text-lg">暂无交易记录</p>
            </div>
          )}
        </div>
      </div>

      {/* Add Transaction Modal */}
      <AnimatePresence>
        {isAddModalOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsAddModalOpen(false)}
              className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40"
            />

            {/* Modal */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
              className="fixed inset-0 z-50 flex items-center justify-center p-4"
            >
              <div 
                className="bg-white/95 backdrop-blur-2xl rounded-3xl w-full max-w-lg p-10 shadow-2xl border border-gray-200" 
                onClick={(e) => e.stopPropagation()}
              >
                <div className="flex items-center justify-between mb-8">
                  <h2 className="text-3xl font-black text-gray-900 tracking-tight">添加交易</h2>
                  <button
                    onClick={() => setIsAddModalOpen(false)}
                    className="p-2 hover:bg-gray-100 rounded-xl transition-colors"
                  >
                    <X className="w-6 h-6 text-gray-500" />
                  </button>
                </div>

                <form onSubmit={handleSubmit} className="space-y-5">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-bold text-gray-700 mb-2.5">基金代码</label>
                      <input
                        type="text"
                        required
                        value={formData.fund_code}
                        onChange={(e) => setFormData({ ...formData, fund_code: e.target.value })}
                        className="w-full px-4 py-3.5 bg-gray-50 border border-gray-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition-all text-gray-900 font-medium"
                        placeholder="例如: 021000"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-bold text-gray-700 mb-2.5">基金名称</label>
                      <input
                        type="text"
                        value={formData.fund_name}
                        onChange={(e) => setFormData({ ...formData, fund_name: e.target.value })}
                        className="w-full px-4 py-3.5 bg-gray-50 border border-gray-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition-all text-gray-900 font-medium"
                        placeholder="可选"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-bold text-gray-700 mb-2.5">交易日期</label>
                      <input
                        type="date"
                        required
                        value={formData.transaction_date}
                        onChange={(e) => setFormData({ ...formData, transaction_date: e.target.value })}
                        className="w-full px-4 py-3.5 bg-gray-50 border border-gray-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition-all text-gray-900 font-medium"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-bold text-gray-700 mb-2.5">交易类型</label>
                      <select
                        value={formData.transaction_type}
                        onChange={(e) => setFormData({ ...formData, transaction_type: e.target.value })}
                        className="w-full px-4 py-3.5 bg-gray-50 border border-gray-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition-all text-gray-900 font-medium"
                      >
                        <option value="买入">买入</option>
                        <option value="卖出">卖出</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-bold text-gray-700 mb-2.5">金额 (元)</label>
                    <input
                      type="number"
                      step="0.01"
                      required
                      value={formData.amount}
                      onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                      className="w-full px-4 py-3.5 bg-gray-50 border border-gray-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition-all text-gray-900 font-medium"
                      placeholder="0.00"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-bold text-gray-700 mb-2.5">备注</label>
                    <textarea
                      value={formData.note}
                      onChange={(e) => setFormData({ ...formData, note: e.target.value })}
                      className="w-full px-4 py-3.5 bg-gray-50 border border-gray-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition-all text-gray-900 font-medium"
                      rows={3}
                      placeholder="可选备注信息"
                    />
                  </div>

                  <div className="flex gap-4 pt-6">
                    <button
                      type="button"
                      onClick={() => setIsAddModalOpen(false)}
                      className="flex-1 px-6 py-4 bg-gray-100 text-gray-700 rounded-2xl font-bold hover:bg-gray-200 transition-all"
                    >
                      取消
                    </button>
                    <button 
                      type="submit" 
                      disabled={loading}
                      className="flex-1 px-6 py-4 bg-gray-900 text-white rounded-2xl font-bold hover:bg-gray-800 transition-all shadow-lg hover:shadow-xl disabled:opacity-50"
                    >
                      {loading ? '提交中...' : '提交'}
                    </button>
                  </div>
                </form>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </Layout>
  )
}
