/**
 * Global Loader Component - عرض حالة التحميل العامة
 */
import { useUIStore } from '../../store/uiStore'
import LoadingSpinner from './LoadingSpinner'

export default function GlobalLoader() {
  const { isLoading, loadingMessage } = useUIStore()

  if (!isLoading) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-sm">
      <div className="bg-white rounded-lg shadow-xl p-6 flex flex-col items-center gap-4 min-w-[200px]">
        <LoadingSpinner size="lg" />
        {loadingMessage && (
          <p className="text-gray-700 font-medium text-center">{loadingMessage}</p>
        )}
      </div>
    </div>
  )
}

