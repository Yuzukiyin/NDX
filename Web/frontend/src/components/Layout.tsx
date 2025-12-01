import { ReactNode } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useAuthStore } from '../stores/authStore'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const navigate = useNavigate()
  const { logout, user } = useAuthStore()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50">
      {/* Sticky Navigation Bar */}
      <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-xl border-b border-gray-200/60 shadow-sm">
        <div className="max-w-7xl mx-auto px-8">
          <div className="flex items-center justify-between h-20">
            {/* Logo */}
            <Link 
              to="/dashboard" 
              className="text-3xl font-black text-gray-900 tracking-[-0.02em] hover:opacity-80 transition-opacity duration-300"
            >
              NDX
            </Link>

            {/* Center Navigation */}
            <div className="flex items-center gap-3">
              <Link
                to="/dashboard"
                className={`
                  px-6 py-3 rounded-2xl font-semibold text-sm transition-all duration-300
                  ${location.pathname === '/dashboard'
                    ? 'bg-gray-900 text-white shadow-lg'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }
                `}
              >
                概览
              </Link>
              <Link
                to="/funds"
                className={`
                  px-6 py-3 rounded-2xl font-semibold text-sm transition-all duration-300
                  ${location.pathname === '/funds'
                    ? 'bg-gray-900 text-white shadow-lg'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }
                `}
              >
                基金
              </Link>
              <Link
                to="/transactions"
                className={`
                  px-6 py-3 rounded-2xl font-semibold text-sm transition-all duration-300
                  ${location.pathname === '/transactions'
                    ? 'bg-gray-900 text-white shadow-lg'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }
                `}
              >
                交易
              </Link>
              <Link
                to="/auto-invest"
                className={`
                  px-6 py-3 rounded-2xl font-semibold text-sm transition-all duration-300
                  ${location.pathname === '/auto-invest'
                    ? 'bg-gray-900 text-white shadow-lg'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }
                `}
              >
                定投
              </Link>
              <Link
                to="/tools"
                className={`
                  px-6 py-3 rounded-2xl font-semibold text-sm transition-all duration-300
                  ${location.pathname === '/tools'
                    ? 'bg-gray-900 text-white shadow-lg'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }
                `}
              >
                工具
              </Link>
            </div>

            {/* User Menu */}
            <div className="flex items-center gap-5 pl-8 border-l border-gray-300">
              <div className="text-right">
                <p className="text-sm font-bold text-gray-900">{user?.username}</p>
                <p className="text-xs text-gray-500">{user?.email}</p>
              </div>
              <button
                onClick={handleLogout}
                className="text-sm text-gray-600 hover:text-gray-900 font-semibold transition-colors px-4 py-2 hover:bg-gray-100 rounded-xl"
              >
                退出
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="max-w-7xl mx-auto px-8 py-12">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        >
          {children}
        </motion.div>
      </main>
    </div>
  )
}
