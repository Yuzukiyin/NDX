import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Plus, Edit2, Trash2, Power, X } from 'lucide-react'
import Layout from '../components/Layout'

interface AutoInvestPlan {
  plan_id: number
  plan_name: string
  fund_code: string
  fund_name: string
  amount: number
  frequency: 'daily' | 'weekly' | 'monthly'
  start_date: string
  end_date: string
  enabled: boolean
  created_at: string
}

const frequencyMap = {
  daily: '每日',
  weekly: '每周',
  monthly: '每月'
}

export default function AutoInvestPage() {
  const [plans, setPlans] = useState<AutoInvestPlan[]>([])
  const [loading, setLoading] = useState(false)
  const [showModal, setShowModal] = useState(false)
  const [editingPlan, setEditingPlan] = useState<AutoInvestPlan | null>(null)
  const [formData, setFormData] = useState({
    plan_name: '',
    fund_code: '',
    fund_name: '',
    amount: '',
    frequency: 'daily' as 'daily' | 'weekly' | 'monthly',
    start_date: new Date().toISOString().split('T')[0],
    end_date: '2099-12-31'
  })

  const fetchPlans = async () => {
    try {
      const apiUrl = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000'
      const token = localStorage.getItem('access_token')
      const response = await fetch(`${apiUrl}/auto-invest/plans`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (response.ok) {
        const data = await response.json()
        setPlans(data)
      }
    } catch (error) {
      console.error('Failed to fetch plans:', error)
    }
  }

  useEffect(() => {
    fetchPlans()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const apiUrl = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000'
      const token = localStorage.getItem('access_token')
      const url = editingPlan
        ? `${apiUrl}/auto-invest/plans/${editingPlan.plan_id}`
        : `${apiUrl}/auto-invest/plans`
      
      const response = await fetch(url, {
        method: editingPlan ? 'PATCH' : 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...formData,
          amount: parseFloat(formData.amount)
        })
      })

      if (response.ok) {
        await fetchPlans()
        setShowModal(false)
        setEditingPlan(null)
        setFormData({
          plan_name: '',
          fund_code: '',
          fund_name: '',
          amount: '',
          frequency: 'daily',
          start_date: new Date().toISOString().split('T')[0],
          end_date: '2099-12-31'
        })
      }
    } catch (error) {
      console.error('Failed to save plan:', error)
      alert('保存失败')
    } finally {
      setLoading(false)
    }
  }

  const handleEdit = (plan: AutoInvestPlan) => {
    setEditingPlan(plan)
    setFormData({
      plan_name: plan.plan_name,
      fund_code: plan.fund_code,
      fund_name: plan.fund_name,
      amount: plan.amount.toString(),
      frequency: plan.frequency,
      start_date: plan.start_date,
      end_date: plan.end_date
    })
    setShowModal(true)
  }

  const handleDelete = async (planId: number) => {
    if (!confirm('确认删除此定投计划?')) return

    try {
      const apiUrl = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000'
      const token = localStorage.getItem('access_token')
      await fetch(`${apiUrl}/auto-invest/plans/${planId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      })
      await fetchPlans()
    } catch (error) {
      console.error('Failed to delete plan:', error)
    }
  }

  const handleToggle = async (planId: number) => {
    try {
      const apiUrl = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000'
      const token = localStorage.getItem('access_token')
      await fetch(`${apiUrl}/auto-invest/plans/${planId}/toggle`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      })
      await fetchPlans()
    } catch (error) {
      console.error('Failed to toggle plan:', error)
    }
  }

  return (
    <Layout>
      <div className="space-y-10">
        {/* Header */}
        <div className="flex items-end justify-between border-b border-gray-200 pb-6">
          <div>
            <h1 className="text-5xl font-black text-gray-900 tracking-tight mb-3">定投管理</h1>
            <p className="text-gray-500 text-lg">配置和管理您的定投计划</p>
          </div>
          <button
            onClick={() => {
              setEditingPlan(null)
              setFormData({
                plan_name: '',
                fund_code: '',
                fund_name: '',
                amount: '',
                frequency: 'daily',
                start_date: new Date().toISOString().split('T')[0],
                end_date: '2099-12-31'
              })
              setShowModal(true)
            }}
            className="px-6 py-3.5 bg-gray-900 text-white rounded-2xl font-bold text-sm flex items-center gap-2.5 hover:bg-gray-800 transition-all shadow-lg hover:shadow-xl"
          >
            <Plus className="w-5 h-5" />
            新增计划
          </button>
        </div>

        {/* Plans Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {plans.map((plan, index) => (
            <motion.div
              key={plan.plan_id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className={`
                bg-white rounded-3xl p-6 border-2 shadow-lg hover:shadow-xl transition-all
                ${plan.enabled ? 'border-green-200' : 'border-gray-200 opacity-60'}
              `}
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-gray-900 mb-1">{plan.plan_name}</h3>
                  <p className="text-sm text-gray-500">{plan.fund_code} - {plan.fund_name}</p>
                </div>
                <div className={`
                  px-3 py-1 rounded-full text-xs font-bold
                  ${plan.enabled ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'}
                `}>
                  {plan.enabled ? '运行中' : '已暂停'}
                </div>
              </div>

              {/* Details */}
              <div className="space-y-3 mb-5">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">金额</span>
                  <span className="text-sm font-bold text-gray-900">¥{plan.amount}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">频率</span>
                  <span className="text-sm font-bold text-gray-900">{frequencyMap[plan.frequency]}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">起止日期</span>
                  <span className="text-sm font-bold text-gray-900">
                    {plan.start_date} ~ {plan.end_date === '2099-12-31' ? '永久' : plan.end_date}
                  </span>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-2 pt-4 border-t border-gray-200">
                <button
                  onClick={() => handleToggle(plan.plan_id)}
                  className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-xl font-semibold text-sm hover:bg-gray-200 transition-colors flex items-center justify-center gap-2"
                >
                  <Power className="w-4 h-4" />
                  {plan.enabled ? '暂停' : '启用'}
                </button>
                <button
                  onClick={() => handleEdit(plan)}
                  className="px-4 py-2 bg-blue-100 text-blue-700 rounded-xl font-semibold text-sm hover:bg-blue-200 transition-colors"
                >
                  <Edit2 className="w-4 h-4" />
                </button>
                <button
                  onClick={() => handleDelete(plan.plan_id)}
                  className="px-4 py-2 bg-red-100 text-red-700 rounded-xl font-semibold text-sm hover:bg-red-200 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Empty State */}
        {plans.length === 0 && (
          <div className="text-center py-20">
            <p className="text-gray-500 text-lg">暂无定投计划</p>
            <p className="text-gray-400 mt-2">点击右上角按钮创建您的第一个定投计划</p>
          </div>
        )}

        {/* Modal */}
        <AnimatePresence>
          {showModal && (
            <>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={() => setShowModal(false)}
                className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40"
              />

              <motion.div
                initial={{ opacity: 0, scale: 0.95, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95, y: 20 }}
                className="fixed inset-0 z-50 flex items-center justify-center p-4"
              >
                <div className="bg-white rounded-3xl w-full max-w-lg p-8 shadow-2xl" onClick={(e) => e.stopPropagation()}>
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-3xl font-black text-gray-900">
                      {editingPlan ? '编辑计划' : '新增计划'}
                    </h2>
                    <button onClick={() => setShowModal(false)} className="p-2 hover:bg-gray-100 rounded-xl">
                      <X className="w-6 h-6" />
                    </button>
                  </div>

                  <form onSubmit={handleSubmit} className="space-y-5">
                    <div>
                      <label className="block text-sm font-bold text-gray-700 mb-2">计划名称</label>
                      <input
                        type="text"
                        required
                        value={formData.plan_name}
                        onChange={(e) => setFormData({ ...formData, plan_name: e.target.value })}
                        className="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-gray-900"
                        placeholder="例如: 广发定投"
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-bold text-gray-700 mb-2">基金代码</label>
                        <input
                          type="text"
                          required
                          value={formData.fund_code}
                          onChange={(e) => setFormData({ ...formData, fund_code: e.target.value })}
                          className="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-gray-900"
                          placeholder="270042"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-bold text-gray-700 mb-2">基金名称</label>
                        <input
                          type="text"
                          required
                          value={formData.fund_name}
                          onChange={(e) => setFormData({ ...formData, fund_name: e.target.value })}
                          className="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-gray-900"
                          placeholder="基金名称"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-bold text-gray-700 mb-2">金额(元)</label>
                        <input
                          type="number"
                          step="0.01"
                          required
                          value={formData.amount}
                          onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                          className="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-gray-900"
                          placeholder="10.00"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-bold text-gray-700 mb-2">频率</label>
                        <select
                          value={formData.frequency}
                          onChange={(e) => setFormData({ ...formData, frequency: e.target.value as any })}
                          className="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-gray-900"
                        >
                          <option value="daily">每日</option>
                          <option value="weekly">每周</option>
                          <option value="monthly">每月</option>
                        </select>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-bold text-gray-700 mb-2">开始日期</label>
                        <input
                          type="date"
                          required
                          value={formData.start_date}
                          onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                          className="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-gray-900"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-bold text-gray-700 mb-2">结束日期</label>
                        <input
                          type="date"
                          required
                          value={formData.end_date}
                          onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                          className="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-gray-900"
                        />
                      </div>
                    </div>

                    <div className="flex gap-4 pt-4">
                      <button
                        type="button"
                        onClick={() => setShowModal(false)}
                        className="flex-1 px-6 py-3 bg-gray-100 text-gray-700 rounded-2xl font-bold hover:bg-gray-200"
                      >
                        取消
                      </button>
                      <button
                        type="submit"
                        disabled={loading}
                        className="flex-1 px-6 py-3 bg-gray-900 text-white rounded-2xl font-bold hover:bg-gray-800 disabled:opacity-50"
                      >
                        {loading ? '保存中...' : '保存'}
                      </button>
                    </div>
                  </form>
                </div>
              </motion.div>
            </>
          )}
        </AnimatePresence>
      </div>
    </Layout>
  )
}
