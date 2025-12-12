import { useState, useEffect } from 'react'
import { apiService } from '../../services/api'
import type { FeedInventory, FeedType } from '../../types'

interface FeedInventoryFormProps {
  item?: FeedInventory | null
  onSubmit: (data: {
    feed_type_id: number
    quantity: number
    unit_price: number
    expiry_date?: string
    location?: string
    notes?: string
  }) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
}

interface FormData {
  feed_type_id: number | ''
  quantity: string
  unit_price: string
  expiry_date: string
  location: string
  notes: string
}

export default function FeedInventoryForm({
  item,
  onSubmit,
  onCancel,
  isLoading = false,
}: FeedInventoryFormProps) {
  const [formData, setFormData] = useState<FormData>({
    feed_type_id: '',
    quantity: '',
    unit_price: '0',
    expiry_date: '',
    location: '',
    notes: '',
  })
  const [feedTypes, setFeedTypes] = useState<FeedType[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchFeedTypes = async () => {
      try {
        const data = await apiService.getFeedTypes()
        setFeedTypes(data)
      } catch (error) {
        console.error('Error fetching feed types:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchFeedTypes()
  }, [])

  useEffect(() => {
    if (item) {
      setFormData({
        feed_type_id: item.feed_type.id,
        quantity: item.quantity.toString(),
        unit_price: item.unit_price.toString(),
        expiry_date: item.expiry_date || '',
        location: item.location || '',
        notes: '',
      })
    }
  }, [item])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.feed_type_id) return

    await onSubmit({
      feed_type_id: formData.feed_type_id as number,
      quantity: parseFloat(formData.quantity),
      unit_price: parseFloat(formData.unit_price || '0'),
      expiry_date: formData.expiry_date || undefined,
      location: formData.location || undefined,
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
          نوع العلف <span className="text-red-500">*</span>
        </label>
        <select
          required
          value={formData.feed_type_id}
          onChange={(e) => setFormData({ ...formData, feed_type_id: parseInt(e.target.value) || '' })}
          className="input-field"
          disabled={!!item}
        >
          <option value="">اختر نوع العلف</option>
          {feedTypes.map((type) => (
            <option key={type.id} value={type.id}>
              {type.arabic_name} ({type.unit})
            </option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            الكمية <span className="text-red-500">*</span>
          </label>
          <input
            type="number"
            required
            min="0.01"
            step="0.01"
            value={formData.quantity}
            onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
            className="input-field"
            placeholder="الكمية"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            سعر الوحدة (ريال)
          </label>
          <input
            type="number"
            min="0"
            step="0.01"
            value={formData.unit_price}
            onChange={(e) => setFormData({ ...formData, unit_price: e.target.value })}
            className="input-field"
            placeholder="0.00"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">تاريخ انتهاء الصلاحية</label>
        <input
          type="date"
          value={formData.expiry_date}
          onChange={(e) => setFormData({ ...formData, expiry_date: e.target.value })}
          className="input-field"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">الموقع</label>
        <input
          type="text"
          value={formData.location}
          onChange={(e) => setFormData({ ...formData, location: e.target.value })}
          className="input-field"
          placeholder="موقع التخزين (اختياري)"
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
        <button type="button" onClick={onCancel} className="flex-1 btn-secondary" disabled={isLoading}>
          إلغاء
        </button>
        <button type="submit" className="flex-1 btn-primary" disabled={isLoading}>
          {isLoading ? 'جاري الحفظ...' : item ? 'حفظ التغييرات' : 'إضافة'}
        </button>
      </div>
    </form>
  )
}

