import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Mail, Lock, User } from 'lucide-react'
import { useAuthStore } from '../stores/authStore'

export default function RegisterPage() {
  const navigate = useNavigate()
  const register = useAuthStore((state) => state.register)
  
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: ''
  })
  const [error, setError] = useState('')
  const [validationErrors, setValidationErrors] = useState<{
    email?: string
    password?: string
    confirmPassword?: string
  }>({})
  const [loading, setLoading] = useState(false)

  // 邮箱格式验证
  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }

  // 密码强度验证
  const validatePassword = (password: string): { valid: boolean; message?: string } => {
    if (password.length < 8) {
      return { valid: false, message: '密码至少需要 8 个字符' }
    }
    if (!/[A-Z]/.test(password)) {
      return { valid: false, message: '密码必须包含至少一个大写字母' }
    }
    if (!/[a-z]/.test(password)) {
      return { valid: false, message: '密码必须包含至少一个小写字母' }
    }
    if (!/[0-9]/.test(password)) {
      return { valid: false, message: '密码必须包含至少一个数字' }
    }
    return { valid: true }
  }

  // 实时验证邮箱
  const handleEmailChange = (email: string) => {
    setFormData({ ...formData, email })
    if (email && !validateEmail(email)) {
      setValidationErrors(prev => ({ ...prev, email: '请输入有效的邮箱地址' }))
    } else {
      setValidationErrors(prev => ({ ...prev, email: undefined }))
    }
  }

  // 实时验证密码
  const handlePasswordChange = (password: string) => {
    setFormData({ ...formData, password })
    if (password) {
      const validation = validatePassword(password)
      if (!validation.valid) {
        setValidationErrors(prev => ({ ...prev, password: validation.message }))
      } else {
        setValidationErrors(prev => ({ ...prev, password: undefined }))
      }
    } else {
      setValidationErrors(prev => ({ ...prev, password: undefined }))
    }
    
    // 同时检查确认密码
    if (formData.confirmPassword && password !== formData.confirmPassword) {
      setValidationErrors(prev => ({ ...prev, confirmPassword: '两次输入的密码不一致' }))
    } else {
      setValidationErrors(prev => ({ ...prev, confirmPassword: undefined }))
    }
  }

  // 验证确认密码
  const handleConfirmPasswordChange = (confirmPassword: string) => {
    setFormData({ ...formData, confirmPassword })
    if (confirmPassword && confirmPassword !== formData.password) {
      setValidationErrors(prev => ({ ...prev, confirmPassword: '两次输入的密码不一致' }))
    } else {
      setValidationErrors(prev => ({ ...prev, confirmPassword: undefined }))
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    console.log('表单提交开始')
    setError('')

    // 验证邮箱格式
    console.log('验证邮箱:', formData.email)
    if (!validateEmail(formData.email)) {
      console.error('邮箱格式无效')
      setError('请输入有效的邮箱地址')
      setValidationErrors(prev => ({ ...prev, email: '请输入有效的邮箱地址' }))
      return
    }
    console.log('邮箱格式有效')

    // 验证密码强度
    console.log('验证密码强度')
    const passwordValidation = validatePassword(formData.password)
    console.log('密码验证结果:', passwordValidation)
    if (!passwordValidation.valid) {
      console.error('密码不符合要求:', passwordValidation.message)
      setError(passwordValidation.message || '密码不符合要求')
      setValidationErrors(prev => ({ ...prev, password: passwordValidation.message }))
      return
    }
    console.log('密码强度符合要求')

    // 验证两次密码是否一致
    console.log('验证密码确认')
    if (formData.password !== formData.confirmPassword) {
      console.error('两次密码不一致')
      setError('两次输入的密码不一致')
      setValidationErrors(prev => ({ ...prev, confirmPassword: '两次输入的密码不一致' }))
      return
    }
    console.log('密码确认一致')

    // 检查是否有任何验证错误
    console.log('检查验证错误:', validationErrors)
    if (validationErrors.email || validationErrors.password || validationErrors.confirmPassword) {
      console.error('存在验证错误')
      setError('请修正表单中的错误后再提交')
      return
    }
    console.log('所有验证通过')
    setLoading(true)
    console.log('开始调用注册 API...')
    try {
      await register({
        email: formData.email,
        username: formData.username,
        password: formData.password
      })
      console.log('注册成功')
      navigate('/dashboard')
    } catch (err: any) {
      console.error('注册失败:', err)
      setError(err.response?.data?.detail || '注册失败，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 px-4 sm:px-6 lg:px-8 py-8 sm:py-12 relative overflow-hidden">
      {/* Background Gradient Overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-900/20 via-transparent to-purple-900/20 pointer-events-none" />
      
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        className="w-full max-w-md relative z-10"
      >
        {/* Logo */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2, duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
          className="text-center mb-6 sm:mb-8"
        >
          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-black text-white tracking-[-0.03em] mb-3 sm:mb-4 drop-shadow-2xl">
            NDX
          </h1>
          <p className="text-xs sm:text-sm text-gray-300 tracking-[0.2em] sm:tracking-[0.25em] uppercase font-light">
            Create Account
          </p>
        </motion.div>

        {/* Register Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
          className="bg-white/10 backdrop-blur-2xl border border-white/20 rounded-2xl sm:rounded-3xl p-6 sm:p-8 lg:p-10 shadow-[0_20px_60px_rgba(0,0,0,0.4)]"
        >
          <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-5">
            {error && (
              <motion.div
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="bg-red-500/20 border border-red-500/40 text-red-100 px-3 sm:px-4 py-2.5 sm:py-3 rounded-xl sm:rounded-2xl text-xs sm:text-sm backdrop-blur-sm"
              >
                {error}
              </motion.div>
            )}

            {/* Email Input */}
            <div>
              <label className="block text-xs sm:text-sm font-semibold text-gray-200 mb-2 sm:mb-3">
                邮箱
              </label>
              <div className="relative">
                <div className="absolute left-3 sm:left-4 top-1/2 -translate-y-1/2 text-gray-400">
                  <Mail className="w-4 h-4 sm:w-5 sm:h-5" />
                </div>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleEmailChange(e.target.value)}
                  className={`w-full pl-10 sm:pl-12 pr-4 sm:pr-5 py-3 sm:py-4 bg-white/10 border rounded-xl sm:rounded-2xl text-white placeholder-gray-400 focus:outline-none focus:bg-white/15 transition-all duration-300 text-sm sm:text-base ${
                    validationErrors.email 
                      ? 'border-red-500/60 focus:border-red-500/80' 
                      : 'border-white/20 focus:border-white/40'
                  }`}
                  placeholder="your@email.com"
                  required
                />
              </div>
              {validationErrors.email && (
                <motion.p
                  initial={{ opacity: 0, y: -5 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-2 text-xs text-red-300 flex items-center gap-1"
                >
                  <span className="text-red-400">⚠</span> {validationErrors.email}
                </motion.p>
              )}
            </div>

            {/* Username Input */}
            <div>
              <label className="block text-xs sm:text-sm font-semibold text-gray-200 mb-2 sm:mb-3">
                用户名
              </label>
              <div className="relative">
                <div className="absolute left-3 sm:left-4 top-1/2 -translate-y-1/2 text-gray-400">
                  <User className="w-4 h-4 sm:w-5 sm:h-5" />
                </div>
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  className="w-full pl-10 sm:pl-12 pr-4 sm:pr-5 py-3 sm:py-4 bg-white/10 border border-white/20 rounded-xl sm:rounded-2xl text-white placeholder-gray-400 focus:outline-none focus:border-white/40 focus:bg-white/15 transition-all duration-300 text-sm sm:text-base"
                  placeholder="至少3个字符"
                  required
                  minLength={3}
                />
              </div>
            </div>

            {/* Password Input */}
            <div>
              <label className="block text-xs sm:text-sm font-semibold text-gray-200 mb-2 sm:mb-3">
                密码
              </label>
              <div className="relative">
                <div className="absolute left-3 sm:left-4 top-1/2 -translate-y-1/2 text-gray-400">
                  <Lock className="w-4 h-4 sm:w-5 sm:h-5" />
                </div>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => handlePasswordChange(e.target.value)}
                  className={`w-full pl-10 sm:pl-12 pr-4 sm:pr-5 py-3 sm:py-4 bg-white/10 border rounded-xl sm:rounded-2xl text-white placeholder-gray-400 focus:outline-none focus:bg-white/15 transition-all duration-300 text-sm sm:text-base ${
                    validationErrors.password 
                      ? 'border-red-500/60 focus:border-red-500/80' 
                      : 'border-white/20 focus:border-white/40'
                  }`}
                  placeholder="至少8个字符，含大小写字母和数字"
                  required
                  minLength={8}
                />
              </div>
              {validationErrors.password && (
                <motion.p
                  initial={{ opacity: 0, y: -5 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-2 text-xs text-red-300 flex items-center gap-1"
                >
                  <span className="text-red-400">⚠</span> {validationErrors.password}
                </motion.p>
              )}
              {!validationErrors.password && formData.password && (
                <motion.div
                  initial={{ opacity: 0, y: -5 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-2 text-xs text-gray-300 space-y-1"
                >
                  <p className="flex items-center gap-1.5">
                    <span className={formData.password.length >= 8 ? 'text-green-400' : 'text-gray-500'}>
                      {formData.password.length >= 8 ? '✓' : '○'}
                    </span>
                    至少 8 个字符
                  </p>
                  <p className="flex items-center gap-1.5">
                    <span className={/[A-Z]/.test(formData.password) ? 'text-green-400' : 'text-gray-500'}>
                      {/[A-Z]/.test(formData.password) ? '✓' : '○'}
                    </span>
                    包含大写字母
                  </p>
                  <p className="flex items-center gap-1.5">
                    <span className={/[a-z]/.test(formData.password) ? 'text-green-400' : 'text-gray-500'}>
                      {/[a-z]/.test(formData.password) ? '✓' : '○'}
                    </span>
                    包含小写字母
                  </p>
                  <p className="flex items-center gap-1.5">
                    <span className={/[0-9]/.test(formData.password) ? 'text-green-400' : 'text-gray-500'}>
                      {/[0-9]/.test(formData.password) ? '✓' : '○'}
                    </span>
                    包含数字
                  </p>
                </motion.div>
              )}
            </div>

            {/* Confirm Password Input */}
            <div>
              <label className="block text-xs sm:text-sm font-semibold text-gray-200 mb-2 sm:mb-3">
                确认密码
              </label>
              <div className="relative">
                <div className="absolute left-3 sm:left-4 top-1/2 -translate-y-1/2 text-gray-400">
                  <Lock className="w-4 h-4 sm:w-5 sm:h-5" />
                </div>
                <input
                  type="password"
                  value={formData.confirmPassword}
                  onChange={(e) => handleConfirmPasswordChange(e.target.value)}
                  className={`w-full pl-10 sm:pl-12 pr-4 sm:pr-5 py-3 sm:py-4 bg-white/10 border rounded-xl sm:rounded-2xl text-white placeholder-gray-400 focus:outline-none focus:bg-white/15 transition-all duration-300 text-sm sm:text-base ${
                    validationErrors.confirmPassword 
                      ? 'border-red-500/60 focus:border-red-500/80' 
                      : 'border-white/20 focus:border-white/40'
                  }`}
                  placeholder="再次输入密码"
                  required
                />
              </div>
              {validationErrors.confirmPassword && (
                <motion.p
                  initial={{ opacity: 0, y: -5 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-2 text-xs text-red-300 flex items-center gap-1"
                >
                  <span className="text-red-400">⚠</span> {validationErrors.confirmPassword}
                </motion.p>
              )}
              {!validationErrors.confirmPassword && formData.confirmPassword && formData.password === formData.confirmPassword && (
                <motion.p
                  initial={{ opacity: 0, y: -5 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-2 text-xs text-green-300 flex items-center gap-1"
                >
                  <span className="text-green-400">✓</span> 密码匹配
                </motion.p>
              )}
            </div>

            {/* Submit Button */}
            <motion.button
              whileHover={{ scale: 1.02, transition: { duration: 0.2 } }}
              whileTap={{ scale: 0.98 }}
              type="submit"
              disabled={loading}
              className="w-full bg-white text-gray-900 py-3 sm:py-4 rounded-xl sm:rounded-2xl font-bold text-sm sm:text-base tracking-wide hover:bg-gray-100 transition-all duration-300 shadow-xl hover:shadow-2xl disabled:opacity-50 disabled:cursor-not-allowed mt-5 sm:mt-6"
            >
              {loading ? '注册中...' : '注册'}
            </motion.button>

            {/* Login Link */}
            <div className="text-center pt-3 sm:pt-4">
              <p className="text-xs sm:text-sm text-gray-300">
                已有账户？{' '}
                <Link 
                  to="/login" 
                  className="text-white font-bold hover:underline underline-offset-4 transition-all"
                >
                  立即登录
                </Link>
              </p>
            </div>
          </form>
        </motion.div>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8, duration: 0.4 }}
          className="text-center mt-10"
        >
          <p className="text-xs text-gray-500 tracking-wide">© 2025 NDX Fund Manager</p>
        </motion.div>
      </motion.div>
    </div>
  )
}
