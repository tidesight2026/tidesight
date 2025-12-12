import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import type { FeedingLog, Batch, FeedType } from '../../types'
import { feedingLogSchema, type FeedingLogFormData } from '../../utils/validation'
import FormField from '../common/FormField'

interface FeedingLogFormProps {
  feedingLog?: FeedingLog | null
  batches: Batch[]
  feedTypes: FeedType[]
  onSubmit: (data: Partial<FeedingLog>) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
}

export default function FeedingLogForm({
  feedingLog,
  batches,
  feedTypes,
  onSubmit,
  onCancel,
  isLoading = false,
}: FeedingLogFormProps) {
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
    reset,
  } = useForm<FeedingLogFormData>({
    resolver: zodResolver(feedingLogSchema),
    defaultValues: {
      batch_id: feedingLog?.batch_id || undefined,
      feed_type_id: feedingLog?.feed_type_id || undefined,
      feeding_date: feedingLog?.feeding_date ? feedingLog.feeding_date.split('T')[0] : new Date().toISOString().split('T')[0],
      quantity: feedingLog?.quantity || 0,
      unit_price: feedingLog?.unit_price || 0,
      notes: feedingLog?.notes || '',
    },
  })

  useEffect(() => {
    if (feedingLog) {
      reset({
        batch_id: feedingLog.batch_id,
        feed_type_id: feedingLog.feed_type_id,
        feeding_date: feedingLog.feeding_date.split('T')[0],
        quantity: feedingLog.quantity,
        unit_price: feedingLog.unit_price,
        notes: feedingLog.notes || '',
      })
    }
  }, [feedingLog, reset])

  const onSubmitForm = async (data: FeedingLogFormData) => {
    try {
      await onSubmit({
        ...data,
        batch_id: Number(data.batch_id),
        feed_type_id: Number(data.feed_type_id),
        feeding_date: typeof data.feeding_date === 'string' ? data.feeding_date : data.feeding_date.toISOString(),
      })
    } catch (err) {
      console.error('Error submitting form:', err)
    }
  }

  const quantity = watch('quantity')
  const unitPrice = watch('unit_price')
  const totalCost = (quantity || 0) * (unitPrice || 0)

  return (
    <form onSubmit={handleSubmit(onSubmitForm)} className="space-y-4">
      <FormField label="الدفعة" error={errors.batch_id?.message} required>
        <select
          {...register('batch_id', { valueAsNumber: true })}
          className={`input-field ${errors.batch_id ? 'border-red-500' : ''}`}
          disabled={isLoading}
        >
          <option value="">-- اختر الدفعة --</option>
          {batches
            .filter((b) => b.status === 'active')
            .map((batch) => (
              <option key={batch.id} value={batch.id}>
                {batch.batch_number} - {batch.species?.arabic_name} ({batch.pond?.name})
              </option>
            ))}
        </select>
      </FormField>

      <FormField label="نوع العلف" error={errors.feed_type_id?.message} required>
        <select
          {...register('feed_type_id', { valueAsNumber: true })}
          className={`input-field ${errors.feed_type_id ? 'border-red-500' : ''}`}
          disabled={isLoading}
        >
          <option value="">-- اختر نوع العلف --</option>
          {feedTypes
            .filter((f) => f.is_active !== false)
            .map((feed) => (
              <option key={feed.id} value={feed.id}>
                {feed.arabic_name} ({feed.unit})
              </option>
            ))}
        </select>
        {feedTypes.filter((f) => (f.is_active ?? true) !== false).length === 0 && (
          <p className="text-xs text-gray-500 mt-1">لا توجد أنواع أعلاف متاحة. يرجى إضافة أنواع أعلاف من صفحة المخزون.</p>
        )}
      </FormField>

      <FormField label="تاريخ التغذية" error={errors.feeding_date?.message} required>
        <input
          type="date"
          {...register('feeding_date')}
          className={`input-field ${errors.feeding_date ? 'border-red-500' : ''}`}
          disabled={isLoading}
        />
      </FormField>

      <div className="grid grid-cols-2 gap-4">
        <FormField label="الكمية (كجم)" error={errors.quantity?.message} required>
          <input
            type="number"
            step="0.01"
            min="0.01"
            {...register('quantity', { valueAsNumber: true })}
            className={`input-field ${errors.quantity ? 'border-red-500' : ''}`}
            disabled={isLoading}
          />
        </FormField>

        <FormField label="سعر الكيلوجرام (ريال)" error={errors.unit_price?.message}>
          <input
            type="number"
            step="0.01"
            min="0"
            {...register('unit_price', { valueAsNumber: true })}
            className={`input-field ${errors.unit_price ? 'border-red-500' : ''}`}
            disabled={isLoading}
          />
        </FormField>
      </div>

      {totalCost > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <p className="text-sm text-blue-900">
            <span className="font-medium">التكلفة الإجمالية:</span>{' '}
            <span className="font-bold">{totalCost.toFixed(2)} ريال</span>
          </p>
        </div>
      )}

      <FormField label="ملاحظات" error={errors.notes?.message}>
        <textarea
          {...register('notes')}
          rows={3}
          className="input-field"
          disabled={isLoading}
        />
      </FormField>

      <div className="flex gap-3 pt-4">
        <button type="submit" className="btn-primary flex-1" disabled={isLoading}>
          {isLoading ? 'جاري الحفظ...' : feedingLog ? 'تحديث' : 'إضافة'}
        </button>
        <button type="button" onClick={onCancel} className="btn-secondary flex-1" disabled={isLoading}>
          إلغاء
        </button>
      </div>
    </form>
  )
}

