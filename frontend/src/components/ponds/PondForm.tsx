import { useState, useEffect } from 'react'
import type { Pond } from '../../types'

interface PondFormProps {
  pond?: Pond | null
  onSubmit: (data: Partial<Pond>) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
}

export default function PondForm({ pond, onSubmit, onCancel, isLoading = false }: PondFormProps) {
  const [formData, setFormData] = useState({
    name: '',
    pond_type: 'concrete' as const,
    capacity: '',
    location: '',
    status: 'empty' as const,
  })

  useEffect(() => {
    if (pond) {
      setFormData({
        name: pond.name,
        pond_type: pond.pond_type as any,
        capacity: pond.capacity.toString(),
        location: pond.location || '',
        status: pond.status as any,
      })
    }
  }, [pond])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    await onSubmit({
      name: formData.name,
      pond_type: formData.pond_type,
      capacity: parseFloat(formData.capacity),
      location: formData.location || undefined,
      status: formData.status,
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          اسم الحوض <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          required
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          className="input-field"
          placeholder="أدخل اسم الحوض"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          نوع الحوض <span className="text-red-500">*</span>
        </label>
        <select
          required
          value={formData.pond_type}
          onChange={(e) => setFormData({ ...formData, pond_type: e.target.value as any })}
          className="input-field"
        >
          <option value="concrete">خرسانة</option>
          <option value="earth">ترابي</option>
          <option value="fiberglass">فيبرجلاس</option>
          <option value="cage">قفص</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          السعة (م³) <span className="text-red-500">*</span>
        </label>
        <input
          type="number"
          required
          min="0.01"
          step="0.01"
          value={formData.capacity}
          onChange={(e) => setFormData({ ...formData, capacity: e.target.value })}
          className="input-field"
          placeholder="أدخل السعة"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">الموقع</label>
        <input
          type="text"
          value={formData.location}
          onChange={(e) => setFormData({ ...formData, location: e.target.value })}
          className="input-field"
          placeholder="أدخل الموقع (اختياري)"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          الحالة <span className="text-red-500">*</span>
        </label>
        <select
          required
          value={formData.status}
          onChange={(e) => setFormData({ ...formData, status: e.target.value as any })}
          className="input-field"
        >
          <option value="empty">فارغ</option>
          <option value="active">نشط</option>
          <option value="maintenance">صيانة</option>
          <option value="inactive">غير نشط</option>
        </select>
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
          {isLoading ? 'جاري الحفظ...' : pond ? 'حفظ التغييرات' : 'إضافة'}
        </button>
      </div>
    </form>
  )
}

