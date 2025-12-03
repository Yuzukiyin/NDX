import { useEffect } from 'react'
import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown, DollarSign, PieChart, ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useFundStore } from '../stores/fundStore'
import Layout from '../components/Layout'

export default function DashboardPage() {
  const { profitSummary, funds, fetchFunds, fetchProfitSummary } = useFundStore()

  useEffect(() => {
    fetchFunds()
    fetchProfitSummary()
  }, [fetchFunds, fetchProfitSummary])

  const stats = [
    {
      label: '总市值',
      value: `¥${profitSummary?.total_value?.toFixed(2) || '0.00'}`,
      icon: DollarSign,
      gradient: 'from-blue-500/20 to-blue-600/20',
      iconBg: 'bg-blue-500/10',
      iconColor: 'text-blue-600',
    },
    {
      label: '总成本',
      value: `¥${profitSummary?.total_cost?.toFixed(2) || '0.00'}`,
      icon: PieChart,
      gradient: 'from-purple-500/20 to-purple-600/20',
      iconBg: 'bg-purple-500/10',
      iconColor: 'text-purple-600',
    },
    {
      label: '总收益',
      value: `¥${profitSummary?.total_profit?.toFixed(2) || '0.00'}`,
      icon: profitSummary && profitSummary.total_profit >= 0 ? TrendingUp : TrendingDown,
      gradient: profitSummary && profitSummary.total_profit >= 0 
        ? 'from-green-500/20 to-green-600/20' 
        : 'from-red-500/20 to-red-600/20',
      iconBg: profitSummary && profitSummary.total_profit >= 0 ? 'bg-green-500/10' : 'bg-red-500/10',
      iconColor: profitSummary && profitSummary.total_profit >= 0 ? 'text-green-600' : 'text-red-600',
    },
    {
      label: '总收益率',
      value: `${profitSummary?.total_return_rate?.toFixed(2) || '0.00'}%`,
      icon: profitSummary && profitSummary.total_return_rate >= 0 ? TrendingUp : TrendingDown,
      gradient: profitSummary && profitSummary.total_return_rate >= 0 
        ? 'from-emerald-500/20 to-emerald-600/20' 
        : 'from-orange-500/20 to-orange-600/20',
      iconBg: profitSummary && profitSummary.total_return_rate >= 0 ? 'bg-emerald-500/10' : 'bg-orange-500/10',
      iconColor: profitSummary && profitSummary.total_return_rate >= 0 ? 'text-emerald-600' : 'text-orange-600',
    },
  ]

  return (
    <Layout>
      <div className="space-y-6 sm:space-y-8 lg:space-y-10">
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between border-b border-gray-200 pb-4 sm:pb-6 gap-3">
          <div>
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black text-gray-900 tracking-tight mb-2 sm:mb-3">概览</h1>
            <p className="text-gray-500 text-base sm:text-lg">您的投资组合表现</p>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-5 lg:gap-6">
          {stats.map((stat, index) => {
            const Icon = stat.icon
            return (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ 
                  duration: 0.6, 
                  delay: index * 0.1,
                  ease: [0.16, 1, 0.3, 1] 
                }}
                whileHover={{ y: -8, transition: { duration: 0.3 } }}
                className={`relative bg-gradient-to-br ${stat.gradient} rounded-2xl sm:rounded-3xl p-5 sm:p-6 lg:p-8 border border-gray-200/60 shadow-lg hover:shadow-2xl transition-all duration-300 overflow-hidden group`}
              >
                {/* Background Pattern */}
                <div className="absolute inset-0 bg-white/50 backdrop-blur-sm" />
                
                <div className="relative z-10">
                  {/* Icon */}
                  <div className={`${stat.iconBg} w-12 h-12 sm:w-14 sm:h-14 rounded-xl sm:rounded-2xl flex items-center justify-center mb-4 sm:mb-5 group-hover:scale-110 transition-transform duration-300`}>
                    <Icon className={`w-6 h-6 sm:w-7 sm:h-7 ${stat.iconColor}`} />
                  </div>

                  {/* Label */}
                  <p className="text-xs sm:text-sm font-semibold text-gray-600 mb-1.5 sm:mb-2 tracking-wide uppercase">
                    {stat.label}
                  </p>

                  {/* Value */}
                  <p className={`text-2xl sm:text-3xl font-black ${stat.iconColor} tracking-tight`}>
                    {stat.value}
                  </p>
                </div>
              </motion.div>
            )
          })}
        </div>

        {/* Holdings Section */}
        <div>
          <div className="flex items-center justify-between mb-4 sm:mb-6">
            <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 tracking-tight">持仓基金</h2>
            <Link 
              to="/funds"
              className="flex items-center gap-2 text-sm sm:text-base text-gray-600 hover:text-gray-900 font-semibold transition-colors group"
            >
              查看全部
              <ArrowRight className="w-4 h-4 sm:w-5 sm:h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
          </div>

          {/* Funds Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-5 lg:gap-6">
            {funds.slice(0, 4).map((fund, index) => (
              <motion.div
                key={fund.fund_code}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ 
                  duration: 0.5, 
                  delay: 0.4 + index * 0.08,
                  ease: [0.16, 1, 0.3, 1] 
                }}
                whileHover={{ y: -6, transition: { duration: 0.2 } }}
                className="bg-white/80 backdrop-blur-sm rounded-2xl sm:rounded-3xl p-5 sm:p-6 lg:p-8 border border-gray-200/60 shadow-lg hover:shadow-2xl transition-all duration-300"
              >
                {/* Fund Header */}
                <div className="flex items-start justify-between mb-5 sm:mb-6 gap-3">
                  <div className="flex-1 min-w-0">
                    <h3 className="font-bold text-gray-900 text-lg sm:text-xl mb-2 tracking-tight truncate">
                      {fund.fund_name}
                    </h3>
                    <p className="text-xs sm:text-sm text-gray-500 font-mono">{fund.fund_code}</p>
                  </div>
                  <div className={`
                    px-3 sm:px-4 py-1.5 sm:py-2 rounded-full text-xs sm:text-sm font-bold whitespace-nowrap flex-shrink-0
                    ${fund.profit >= 0
                      ? 'bg-green-100 text-green-700'
                      : 'bg-red-100 text-red-700'
                    }
                  `}>
                    {fund.profit >= 0 ? '+' : ''}{fund.profit_rate.toFixed(2)}%
                  </div>
                </div>

                {/* Fund Stats Grid */}
                <div className="grid grid-cols-2 gap-4 sm:gap-5">
                  <div className="bg-gray-50 rounded-xl sm:rounded-2xl p-3 sm:p-4">
                    <p className="text-xs text-gray-500 mb-1 sm:mb-1.5 font-semibold uppercase tracking-wide">
                      当前市值
                    </p>
                    <p className="text-lg sm:text-xl font-bold text-gray-900">
                      ¥{fund.current_value.toFixed(2)}
                    </p>
                  </div>
                  <div className={`rounded-xl sm:rounded-2xl p-3 sm:p-4 ${
                    fund.profit >= 0 ? 'bg-green-50' : 'bg-red-50'
                  }`}>
                    <p className="text-xs text-gray-500 mb-1 sm:mb-1.5 font-semibold uppercase tracking-wide">
                      累计收益
                    </p>
                    <p className={`text-lg sm:text-xl font-bold ${
                      fund.profit >= 0 ? 'text-green-700' : 'text-red-700'
                    }`}>
                      {fund.profit >= 0 ? '+' : ''}￥{fund.profit.toFixed(2)}
                    </p>
                  </div>
                </div>

                {/* Divider */}
                <div className="my-4 sm:my-5 border-t border-gray-200" />

                {/* Additional Details */}
                <div className="grid grid-cols-2 gap-3 sm:gap-4 text-xs sm:text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500 font-medium">持有份额</span>
                    <span className="text-gray-900 font-bold">
                      {fund.total_shares.toFixed(2)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500 font-medium">当前净值</span>
                    <span className="text-gray-900 font-bold">
                      ¥{fund.current_nav.toFixed(4)}
                    </span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Empty State */}
          {funds.length === 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
              className="text-center py-20 bg-white/50 rounded-3xl border border-gray-200/60"
            >
              <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gray-100 mb-5">
                <TrendingUp className="w-10 h-10 text-gray-400" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">暂无持仓基金</h3>
              <p className="text-gray-500 mb-6">开始添加交易记录来追踪您的投资</p>
              <Link 
                to="/transactions"
                className="inline-flex items-center gap-2 px-6 py-3 bg-gray-900 text-white rounded-2xl font-semibold hover:bg-gray-800 transition-all shadow-lg hover:shadow-xl"
              >
                添加交易
                <ArrowRight className="w-5 h-5" />
              </Link>
            </motion.div>
          )}
        </div>
      </div>
    </Layout>
  )
}
