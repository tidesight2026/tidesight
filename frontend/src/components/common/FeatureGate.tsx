import React from 'react'

interface FeatureGateProps {
  feature: string
  features?: Record<string, boolean>
  fallback?: React.ReactNode
  children: React.ReactNode
}

/**
 * إخفاء أو تقييد الميزة بناءً على خطة الاشتراك الحالية.
 * يقرأ features (قاموس من الميزة -> boolean). إذا لم تكن الميزة مفعلة، يعرض fallback.
 */
export function FeatureGate({ feature, features, fallback, children }: FeatureGateProps) {
  const isEnabled = features ? features[feature] === true : true

  if (!isEnabled) {
    return (
      fallback || (
        <div className="p-4 border border-yellow-200 bg-yellow-50 rounded text-yellow-800">
          هذه الميزة غير متاحة في باقتك الحالية. يرجى الترقية للاستفادة منها.
        </div>
      )
    )
  }

  return <>{children}</>
}

