import { useState, useEffect } from 'react'
import { apiService } from '../../services/api'
import type { Batch, Pond, Species } from '../../types'

interface BatchFormSubmitData {
  pond_id: number
  species_id: number
  batch_number: string
  start_date: string
  initial_count: number
  initial_weight: number
  initial_cost: number
  notes?: string
}

interface BatchFormProps {
  batch?: Batch | null
  onSubmit: (data: BatchFormSubmitData) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
}

interface BatchFormData {
  pond_id: number | ''
  species_id: number | ''
  batch_number: string
  start_date: string
  initial_count: string
  initial_weight: string
  initial_cost: string
  notes: string
}

export default function BatchForm({ batch, onSubmit, onCancel, isLoading = false }: BatchFormProps) {
  const [formData, setFormData] = useState<BatchFormData>({
    pond_id: '',
    species_id: '',
    batch_number: '',
    start_date: '',
    initial_count: '',
    initial_weight: '',
    initial_cost: '0',
    notes: '',
  })
  const [ponds, setPonds] = useState<Pond[]>([])
  const [species, setSpecies] = useState<Species[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [pondsData, speciesData] = await Promise.all([
          apiService.getPonds(),
          apiService.getSpecies(),
        ])
        setPonds(pondsData)
        setSpecies(speciesData)
      } catch (error) {
        console.error('Error fetching data:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  useEffect(() => {
    if (batch) {
      setFormData({
        pond_id: batch.pond.id,
        species_id: batch.species.id,
        batch_number: batch.batch_number,
        start_date: batch.start_date,
        initial_count: batch.initial_count.toString(),
        initial_weight: batch.initial_weight.toString(),
        initial_cost: batch.initial_cost.toString(),
        notes: batch.notes || '',
      })
    }
  }, [batch])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.pond_id || !formData.species_id) {
      return
    }
    await onSubmit({
      pond_id: formData.pond_id as number,
      species_id: formData.species_id as number,
      batch_number: formData.batch_number,
      start_date: formData.start_date,
      initial_count: parseInt(formData.initial_count),
      initial_weight: parseFloat(formData.initial_weight),
      initial_cost: parseFloat(formData.initial_cost || '0'),
      notes: formData.notes || undefined,
    })
  }

  if (loading) {
    return <div className="text-center py-8">جاري التحميل...</div>
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          رقم الدفعة <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          required
          value={formData.batch_number}
          onChange={(e) => setFormData({ ...formData, batch_number: e.target.value })}
          className="input-field"
          placeholder="مثال: BATCH-2024-001"
          disabled={!!batch}
        />
        {batch && <p className="text-xs text-gray-500 mt-1">لا يمكن تغيير رقم الدفعة</p>}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          الحوض <span className="text-red-500">*</span>
        </label>
        <select
          required
          value={formData.pond_id}
          onChange={(e) => setFormData({ ...formData, pond_id: parseInt(e.target.value) || '' })}
          className="input-field"
          disabled={!!batch}
        >
          <option value="">اختر الحوض</option>
          {ponds
            .filter((p) => p.is_active && p.status === 'active')
            .map((pond) => (
              <option key={pond.id} value={pond.id}>
                {pond.name} ({pond.capacity} م³)
              </option>
            ))}
        </select>
        {ponds.filter((p) => p.is_active && p.status === 'active').length === 0 && (
          <p className="text-xs text-gray-500 mt-1">لا توجد أحواض نشطة متاحة. يرجى إضافة أحواض من صفحة الأحواض.</p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          النوع السمكي <span className="text-red-500">*</span>
        </label>
        <select
          required
          value={formData.species_id}
          onChange={(e) => setFormData({ ...formData, species_id: parseInt(e.target.value) || '' })}
          className="input-field"
          disabled={!!batch}
        >
          <option value="">اختر النوع</option>
          {species.map((s) => (
            <option key={s.id} value={s.id}>
              {s.arabic_name}
            </option>
          ))}
        </select>
        {species.length === 0 && (
          <p className="text-xs text-gray-500 mt-1">لا توجد أنواع متاحة. يرجى إضافة أنواع من صفحة الأنواع.</p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          تاريخ البدء <span className="text-red-500">*</span>
        </label>
        <input
          type="date"
          required
          value={formData.start_date}
          onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
          className="input-field"
          disabled={!!batch}
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            العدد الأولي <span className="text-red-500">*</span>
          </label>
          <input
            type="number"
            required
            min="1"
            value={formData.initial_count}
            onChange={(e) => setFormData({ ...formData, initial_count: e.target.value })}
            className="input-field"
            placeholder="عدد الأسماك"
            disabled={!!batch}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            الوزن الأولي (كجم) <span className="text-red-500">*</span>
          </label>
          <input
            type="number"
            required
            min="0.01"
            step="0.01"
            value={formData.initial_weight}
            onChange={(e) => setFormData({ ...formData, initial_weight: e.target.value })}
            className="input-field"
            placeholder="الوزن بالكيلوجرام"
            disabled={!!batch}
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          التكلفة الأولية (ريال)
        </label>
        <input
          type="number"
          min="0"
          step="0.01"
          value={formData.initial_cost}
          onChange={(e) => setFormData({ ...formData, initial_cost: e.target.value })}
          className="input-field"
          placeholder="0.00"
          disabled={!!batch}
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">ملاحظات</label>
        <textarea
          value={formData.notes}
          onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
          className="input-field"
          rows={3}
          placeholder="ملاحظات إضافية (اختياري)"
        />
      </div>

      <div className="flex gap-3 pt-4">
        <button
          type="button"
          onClick={onCancel}
          className="flex-1 btn-secondary"
          disabled={isLoading}
        >
          إلغاء
        </button>
        <button type="submit" className="flex-1 btn-primary" disabled={isLoading}>
          {isLoading ? 'جاري الحفظ...' : batch ? 'حفظ التغييرات' : 'إضافة'}
        </button>
      </div>
    </form>
  )
}

