import { z } from 'zod'

// Arabic error messages
const arabicMessages = {
  required: 'هذا الحقل مطلوب',
  min: 'القيمة صغيرة جداً',
  max: 'القيمة كبيرة جداً',
  email: 'البريد الإلكتروني غير صحيح',
  positive: 'يجب أن تكون القيمة أكبر من صفر',
  number: 'يجب أن يكون رقم',
  string: 'يجب أن يكون نص',
}

// Common validation schemas
export const commonSchemas = {
  requiredString: z.string().min(1, arabicMessages.required),
  optionalString: z.string().optional(),
  email: z.string().email(arabicMessages.email),
  positiveNumber: z.number().positive(arabicMessages.positive),
  optionalPositiveNumber: z.number().positive(arabicMessages.positive).optional(),
  date: z.string().or(z.date()),
  optionalDate: z.string().or(z.date()).optional(),
}

// Login validation
export const loginSchema = z.object({
  username: commonSchemas.requiredString.min(3, 'اسم المستخدم يجب أن يكون 3 أحرف على الأقل'),
  password: commonSchemas.requiredString.min(6, 'كلمة المرور يجب أن تكون 6 أحرف على الأقل'),
})

// Pond validation
export const pondSchema = z.object({
  name: commonSchemas.requiredString.min(2, 'اسم الحوض يجب أن يكون حرفين على الأقل'),
  pond_type: commonSchemas.requiredString,
  capacity_cubic_meters: commonSchemas.positiveNumber,
  location: commonSchemas.optionalString,
  notes: commonSchemas.optionalString,
})

// Batch validation
export const batchSchema = z.object({
  batch_number: commonSchemas.requiredString,
  species_id: z.number().positive(arabicMessages.positive),
  pond_id: z.number().positive(arabicMessages.positive),
  initial_count: commonSchemas.positiveNumber,
  initial_weight: commonSchemas.positiveNumber,
  initial_cost: z.number().min(0, 'التكلفة الأولية يجب أن تكون أكبر من أو تساوي صفر'),
  stocking_date: commonSchemas.date,
  expected_harvest_date: commonSchemas.optionalDate,
  notes: commonSchemas.optionalString,
})

// Feeding Log validation
export const feedingLogSchema = z.object({
  batch_id: z.number().positive(arabicMessages.positive),
  feed_type_id: z.number().positive(arabicMessages.positive),
  feeding_date: commonSchemas.date,
  quantity: commonSchemas.positiveNumber,
  unit_price: z.number().min(0, 'السعر يجب أن يكون أكبر من أو يساوي صفر'),
  notes: commonSchemas.optionalString,
})

// Mortality Log validation
export const mortalityLogSchema = z.object({
  batch_id: z.number().positive(arabicMessages.positive),
  mortality_date: commonSchemas.date,
  count: z.number().int().positive(arabicMessages.positive),
  average_weight_g: z.number().positive(arabicMessages.positive),
  cause: commonSchemas.optionalString,
  notes: commonSchemas.optionalString,
})

// Feed Inventory validation
export const feedInventorySchema = z.object({
  feed_type_id: z.number().positive(arabicMessages.positive),
  quantity: commonSchemas.positiveNumber,
  unit_price: z.number().min(0, 'السعر يجب أن يكون أكبر من أو يساوي صفر'),
  expiry_date: commonSchemas.optionalDate,
  notes: commonSchemas.optionalString,
})

// Medicine Inventory validation
export const medicineInventorySchema = z.object({
  medicine_id: z.number().positive(arabicMessages.positive),
  quantity: commonSchemas.positiveNumber,
  unit_price: z.number().min(0, 'السعر يجب أن يكون أكبر من أو يساوي صفر'),
  expiry_date: commonSchemas.optionalDate,
  notes: commonSchemas.optionalString,
})

// Sales Order validation
export const salesOrderSchema = z.object({
  order_date: commonSchemas.date,
  customer_name: commonSchemas.requiredString.min(2, 'اسم العميل يجب أن يكون حرفين على الأقل'),
  customer_phone: commonSchemas.optionalString,
  customer_address: commonSchemas.optionalString,
  vat_rate: z.number().min(0).max(100, 'نسبة الضريبة يجب أن تكون بين 0 و 100'),
  lines: z.array(
    z.object({
      harvest_id: z.number().positive(arabicMessages.positive),
      quantity_kg: commonSchemas.positiveNumber,
      unit_price: commonSchemas.positiveNumber,
    })
  ).min(1, 'يجب إضافة بند واحد على الأقل'),
  notes: commonSchemas.optionalString,
})

// Export types
export type LoginFormData = z.infer<typeof loginSchema>
export type PondFormData = z.infer<typeof pondSchema>
export type BatchFormData = z.infer<typeof batchSchema>
export type FeedingLogFormData = z.infer<typeof feedingLogSchema>
export type MortalityLogFormData = z.infer<typeof mortalityLogSchema>
export type FeedInventoryFormData = z.infer<typeof feedInventorySchema>
export type MedicineInventoryFormData = z.infer<typeof medicineInventorySchema>
export type SalesOrderFormData = z.infer<typeof salesOrderSchema>

