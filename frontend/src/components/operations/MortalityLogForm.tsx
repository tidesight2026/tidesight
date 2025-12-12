import { useState, useEffect } from 'react'
import type { MortalityLog, Batch } from '../../types'

interface MortalityLogFormProps {
  mortalityLog?: MortalityLog | null
  batches: Batch[]
  onSubmit: (data: Partial<MortalityLog>) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
}

export default function MortalityLogForm({
  mortalityLog,
  batches,
  onSubmit,
  onCancel,
  isLoading = false,
}: MortalityLogFormProps) {
  const [formData, setFormData] = useState({
    batch_id: mortalityLog?.batch_id || '',
    mortality_date: mortalityLog?.mortality_date || new Date().toISOString().split('T')[0],
    count: mortalityLog?.count || 0,
    average_weight: mortalityLog?.average_weight || 0,
    cause: mortalityLog?.cause || '',
    notes: mortalityLog?.notes || '',
  })

  const [errors, setErrors] = useState<Record<string, string>>({})

  useEffect(() => {
    if (mortalityLog) {
      setFormData({
        batch_id: mortalityLog.batch_id,
        mortality_date: mortalityLog.mortality_date.split('T')[0],
        count: mortalityLog.count,
        average_weight: mortalityLog.average_weight || 0,
        cause: mortalityLog.cause || '',
        notes: mortalityLog.notes || '',
      })
    }
  }, [mortalityLog])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]:
        name === 'batch_id'
          ? Number(value)
          : name === 'count' || name === 'average_weight'
            ? Number(value)
            : value,
    }))
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }))
    }
  }

  const validate = () => {
    const newErrors: Record<string, string> = {}
    if (!formData.batch_id) newErrors.batch_id = 'يجب اختيار الدفعة'
    if (!formData.mortality_date) newErrors.mortality_date = 'يجب تحديد تاريخ النفوق'
    if (!formData.count || formData.count <= 0) newErrors.count = 'يجب إدخال عدد صحيح أكبر من صفر'
    if (formData.average_weight < 0) newErrors.average_weight = 'الوزن يجب أن يكون أكبر من أو يساوي صفر'

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validate()) return

    try {
      await onSubmit({
        ...formData,
        batch_id: Number(formData.batch_id),
        average_weight: formData.average_weight > 0 ? formData.average_weight : undefined,
      })
    } catch (err) {
      console.error('Error submitting form:', err)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="batch_id" className="block text-sm font-medium text-gray-700 mb-1">
          الدفعة <span className="text-red-500">*</span>
        </label>
        <select
          id="batch_id"
          name="batch_id"
          value={formData.batch_id}
          onChange={handleChange}
          className={`input-field ${errors.batch_id ? 'border-red-500' : ''}`}
          disabled={isLoading}
        >
          <option value="">-- اختر الدفعة --</option>
          {batches
            .filter((b) => b.status === 'active')
            .map((batch) => (
              <option key={batch.id} value={batch.id}>
                {batch.batch_number} - {batch.species.arabic_name} ({batch.pond.name})
              </option>
            ))}
        </select>
        {errors.batch_id && <p className="text-red-500 text-sm mt-1">{errors.batch_id}</p>}
      </div>

      <div>
        <label htmlFor="mortality_date" className="block text-sm font-medium text-gray-700 mb-1">
          تاريخ النفوق <span className="text-red-500">*</span>
        </label>
        <input
          type="date"
          id="mortality_date"
          name="mortality_date"
          value={formData.mortality_date}
          onChange={handleChange}
          className={`input-field ${errors.mortality_date ? 'border-red-500' : ''}`}
          disabled={isLoading}
        />
        {errors.mortality_date && <p className="text-red-500 text-sm mt-1">{errors.mortality_date}</p>}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="count" className="block text-sm font-medium text-gray-700 mb-1">
            عدد النفوق <span className="text-red-500">*</span>
          </label>
          <input
            type="number"
            id="count"
            name="count"
            value={formData.count}
            onChange={handleChange}
            min="1"
            className={`input-field ${errors.count ? 'border-red-500' : ''}`}
            disabled={isLoading}
          />
          {errors.count && <p className="text-red-500 text-sm mt-1">{errors.count}</p>}
        </div>

        <div>
          <label htmlFor="average_weight" className="block text-sm font-medium text-gray-700 mb-1">
            متوسط الوزن (كجم)
          </label>
          <input
            type="number"
            id="average_weight"
            name="average_weight"
            value={formData.average_weight}
            onChange={handleChange}
            step="0.001"
            min="0"
            className={`input-field ${errors.average_weight ? 'border-red-500' : ''}`}
            disabled={isLoading}
          />
          {errors.average_weight && <p className="text-red-500 text-sm mt-1">{errors.average_weight}</p>}
        </div>
      </div>

      <div>
        <label htmlFor="cause" className="block text-sm font-medium text-gray-700 mb-1">
          سبب النفوق
        </label>
        <input
          type="text"
          id="cause"
          name="cause"
          value={formData.cause}
          onChange={handleChange}
          placeholder="مثال: مرض، نقص أكسجين..."
          className="input-field"
          disabled={isLoading}
        />
      </div>

      <div>
        <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-1">
          ملاحظات
        </label>
        <textarea
          id="notes"
          name="notes"
          value={formData.notes}
          onChange={handleChange}
          rows={3}
          className="input-field"
          disabled={isLoading}
        />
      </div>

      <div className="flex gap-3 pt-4">
        <button type="submit" className="btn-primary flex-1" disabled={isLoading}>
          {isLoading ? 'جاري الحفظ...' : mortalityLog ? 'تحديث' : 'إضافة'}
        </button>
        <button type="button" onClick={onCancel} className="btn-secondary flex-1" disabled={isLoading}>
          إلغاء
        </button>
      </div>
    </form>
  )
}

