import { useEffect } from 'react'
import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown, Calendar, Hash, DollarSign } from 'lucide-react'
import { useFundStore } from '../stores/fundStore'
import Layout from '../components/Layout'

export default function FundsPage() {
  const { funds, fetchFunds } = useFundStore()

  useEffect(() => {
    fetchFunds()
  }, [fetchFunds])

  return (
    <Layout>
      <div className="space-y-6 sm:space-y-8 lg:space-y-10">
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between border-b border-gray-200 pb-4 sm:pb-6 gap-3">
          <div>
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black text-gray-900 tracking-tight mb-2 sm:mb-3">基金</h1>
            <p className="text-gray-500 text-base sm:text-lg">管理您的基金持仓</p>
          </div>
        </div>

        {/* Funds Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4 sm:gap-5 lg:gap-6">
          {funds.map((fund, index) => {
            const isProfit = fund.profit >= 0

            return (
              <motion.div
                key={fund.fund_code}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{
                  duration: 0.6,
                  delay: index * 0.08,
                  ease: [0.16, 1, 0.3, 1],
                }}
                whileHover={{ y: -8, scale: 1.02, transition: { duration: 0.3 } }}
                className="bg-white/80 backdrop-blur-sm rounded-2xl sm:rounded-3xl p-5 sm:p-6 lg:p-8 border border-gray-200/60 shadow-lg hover:shadow-2xl transition-all duration-300 group"
              >
                {/* Fund Header */}
                <div className="mb-5 sm:mb-6">
                  <div className="flex items-start justify-between gap-3 sm:gap-4 mb-4">
                    <div className="flex-1 min-w-0">
                      <h3 className="font-bold text-gray-900 text-lg sm:text-xl mb-2 truncate tracking-tight">
                        {fund.fund_name}
                      </h3>
                      <div className="flex items-center gap-2 text-xs sm:text-sm text-gray-500">
                        <Hash className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                        <span className="font-mono">{fund.fund_code}</span>
                      </div>
                    </div>
                    <div className={`
                      px-3 sm:px-4 py-1.5 sm:py-2 rounded-full text-xs sm:text-sm font-bold whitespace-nowrap
                      flex items-center gap-1.5 flex-shrink-0
                      group-hover:scale-110 transition-transform duration-300
                      ${isProfit
                        ? 'bg-green-100 text-green-700'
                        : 'bg-red-100 text-red-700'
                      }
                    `}>
                      {isProfit ? (
                        <TrendingUp className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                      ) : (
                        <TrendingDown className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                      )}
                      {fund.profit_rate.toFixed(2)}%
                    </div>
                  </div>
                </div>

                {/* Main Stats */}
                <div className="grid grid-cols-2 gap-3 sm:gap-4 mb-5 sm:mb-6">
                  <div className="bg-gradient-to-br from-blue-50 to-blue-100/50 rounded-xl sm:rounded-2xl p-4 sm:p-5 border border-blue-200/50">
                    <div className="flex items-center gap-2 mb-2">
                      <DollarSign className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-blue-600" />
                      <p className="text-xs font-bold uppercase tracking-wide text-blue-700">
                        当前市值
                      </p>
                    </div>
                    <p className="text-2xl font-black text-blue-900">
                      ¥{fund.current_value.toFixed(2)}
                    </p>
                  </div>
                  <div className={`rounded-2xl p-5 border ${
                    isProfit 
                      ? 'bg-gradient-to-br from-green-50 to-green-100/50 border-green-200/50' 
                      : 'bg-gradient-to-br from-red-50 to-red-100/50 border-red-200/50'
                  }`}>
                    <div className="flex items-center gap-2 mb-2">
                      {isProfit ? (
                        <TrendingUp className="w-4 h-4 text-green-600" />
                      ) : (
                        <TrendingDown className="w-4 h-4 text-red-600" />
                      )}
                      <p className={`text-xs font-bold uppercase tracking-wide ${
                        isProfit ? 'text-green-700' : 'text-red-700'
                      }`}>
                        累计收益
                      </p>
                    </div>
                    <p className={`text-2xl font-black ${
                      isProfit ? 'text-green-900' : 'text-red-900'
                    }`}>
                      {isProfit ? '+' : ''}¥{fund.profit.toFixed(2)}
                    </p>
                  </div>
                </div>

                {/* Divider */}
                <div className="my-6 border-t border-gray-200" />

                {/* Additional Stats */}
                <div className="space-y-3.5">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-500 font-medium">持有份额</span>
                    <span className="text-sm font-bold text-gray-900">
                      {fund.total_shares.toFixed(2)}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-500 font-medium">当前净值</span>
                    <span className="text-sm font-bold text-gray-900">
                      ¥{fund.current_nav.toFixed(4)}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-500 font-medium">平均买入净值</span>
                    <span className="text-sm font-bold text-gray-900">
                      ¥{fund.average_buy_nav.toFixed(4)}
                    </span>
                  </div>
                  {fund.last_nav_date && (
                    <div className="flex justify-between items-center pt-2">
                      <span className="text-xs text-gray-400 flex items-center gap-1.5">
                        <Calendar className="w-3.5 h-3.5" />
                        净值日期
                      </span>
                      <span className="text-xs text-gray-500 font-medium">
                        {new Date(fund.last_nav_date).toLocaleDateString('zh-CN')}
                      </span>
                    </div>
                  )}
                </div>
              </motion.div>
            )
          })}
        </div>

        {/* Empty State */}
        {funds.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="text-center py-24 bg-white/50 rounded-3xl border border-gray-200/60"
          >
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gray-100 mb-6">
              <TrendingUp className="w-10 h-10 text-gray-400" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-3">暂无持仓基金</h3>
            <p className="text-gray-500 text-lg">开始添加交易记录来追踪您的基金投资</p>
          </motion.div>
        )}
      </div>
    </Layout>
  )
}
