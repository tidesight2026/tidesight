import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useTranslation } from 'react-i18next'
import { useAuthStore } from '../store/authStore'
import { loginSchema, type LoginFormData } from '../utils/validation'
import FormField from '../components/common/FormField'
import LanguageSwitcher from '../components/common/LanguageSwitcher'

export default function Login() {
  const { t } = useTranslation()
  const [apiError, setApiError] = useState('')
  const [loading, setLoading] = useState(false)
  
  const login = useAuthStore((state) => state.login)
  const navigate = useNavigate()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  })

  const onSubmit = async (data: LoginFormData) => {
    setApiError('')
    setLoading(true)

    try {
      await login(data.username, data.password)
      navigate('/dashboard')
    } catch (err: any) {
      setApiError(err.response?.data?.detail || 'فشل تسجيل الدخول. يرجى التحقق من البيانات.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="card w-full max-w-md">
        <div className="flex justify-end mb-4">
          <LanguageSwitcher />
        </div>
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">AquaERP</h1>
          <p className="text-gray-600">نظام إدارة المزارع السمكية</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {apiError && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg" role="alert">
              {apiError}
            </div>
          )}

          <FormField
            label={t('auth.username')}
            error={errors.username?.message}
            required
          >
            <input
              type="text"
              {...register('username')}
              className="input-field"
              disabled={loading}
              autoComplete="username"
            />
          </FormField>

          <FormField
            label={t('auth.password')}
            error={errors.password?.message}
            required
          >
            <input
              type="password"
              {...register('password')}
              className="input-field"
              disabled={loading}
              autoComplete="current-password"
            />
          </FormField>

          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? t('common.loading') : t('auth.login')}
          </button>
        </form>
      </div>
    </div>
  )
}

