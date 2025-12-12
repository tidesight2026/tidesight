import { useState, useEffect } from 'react'
import { apiService } from '../../services/api'
import type { MedicineInventory, Medicine } from '../../types'

interface MedicineInventoryFormProps {
  item?: MedicineInventory | null
  onSubmit: (data: {
    medicine_id: number
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
  medicine_id: number | ''
  quantity: string
  unit_price: string
  expiry_date: string
  location: string
  notes: string
}

export default function MedicineInventoryForm({
  item,
  onSubmit,
  onCancel,
  isLoading = false,
}: MedicineInventoryFormProps) {
  const [formData, setFormData] = useState<FormData>({
    medicine_id: '',
    quantity: '',
    unit_price: '0',
    expiry_date: '',
    location: '',
    notes: '',
  })
  const [medicines, setMedicines] = useState<Medicine[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchMedicines = async () => {
      try {
        const data = await apiService.getMedicineTypes()
        setMedicines(data)
      } catch (error) {
        console.error('Error fetching medicines:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchMedicines()
  }, [])

  useEffect(() => {
    if (item) {
      setFormData({
        medicine_id: item.medicine.id,
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
    if (!formData.medicine_id) return

    await onSubmit({
      medicine_id: formData.medicine_id as number,
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
          الدواء <span className="text-red-500">*</span>
        </label>
        <select
          required
          value={formData.medicine_id}
          onChange={(e) => setFormData({ ...formData, medicine_id: parseInt(e.target.value) || '' })}
          className="input-field"
          disabled={!!item}
        >
          <option value="">اختر الدواء</option>
          {medicines.map((medicine) => (
            <option key={medicine.id} value={medicine.id}>
              {medicine.arabic_name} ({medicine.unit})
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

