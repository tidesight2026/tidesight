# توثيق الجداول/الموديلات في AquaERP

> هذا الملف يوثق جميع الجداول (Django Models) المستخدمة في AquaERP مع وصف مفصل لكل جدول.

---

## 1. تطبيق Biological (البيولوجي)

### 1.1 Species (الأنواع السمكية)
**الجدول:** `biological_species`

**الحقول:**
- `id` - Primary Key
- `name` - الاسم العلمي
- `arabic_name` - الاسم العربي
- `scientific_name` - الاسم اللاتيني
- `description` - الوصف
- `is_active` - نشط
- `created_at` - تاريخ الإنشاء
- `updated_at` - آخر تحديث

**العلاقات:**
- Many-to-Many مع `LifecycleStage`

---

### 1.2 LifecycleStage (مراحل النمو)
**الجدول:** `biological_lifecyclestage`

**الحقول:**
- `id` - Primary Key
- `name` - اسم المرحلة
- `arabic_name` - الاسم العربي
- `description` - الوصف
- `min_days` - الحد الأدنى للأيام
- `max_days` - الحد الأقصى للأيام
- `order` - ترتيب المرحلة
- `is_active` - نشط
- `created_at` - تاريخ الإنشاء
- `updated_at` - آخر تحديث

---

### 1.3 FarmLocation (موقع المزرعة)
**الجدول:** `biological_farmlocation`

**الحقول:**
- `id` - Primary Key
- `name` - اسم الموقع
- `arabic_name` - الاسم العربي
- `description` - الوصف
- `parent_id` - الموقع الأب (ForeignKey إلى نفس الجدول)
- `is_active` - نشط
- `created_at` - تاريخ الإنشاء
- `updated_at` - آخر تحديث

---

### 1.4 Pond (الحوض)
**الجدول:** `biological_pond`

**الحقول:**
- `id` - Primary Key
- `name` - اسم الحوض
- `pond_type` - نوع الحوض (concrete/earth/fiberglass/cage)
- `capacity` - السعة (م³)
- `location` - الموقع (نص)
- `farm_location_id` - موقع المزرعة (ForeignKey إلى `FarmLocation`)
- `coordinates_x` - إحداثي X
- `coordinates_y` - إحداثي Y
- `status` - الحالة (active/maintenance/empty/inactive)
- `is_active` - نشط
- `created_at` - تاريخ الإنشاء
- `updated_at` - آخر تحديث

**الفهارس:**
- Index على `name`

---

### 1.5 Batch (الدفعة)
**الجدول:** `biological_batch`

**الحقول:**
- `id` - Primary Key
- `pond_id` - الحوض (ForeignKey إلى `Pond`)
- `species_id` - النوع السمكي (ForeignKey إلى `Species`)
- `batch_number` - رقم الدفعة (فريد)
- `start_date` - تاريخ البدء
- `initial_count` - العدد الأولي
- `initial_weight` - الوزن الأولي (كجم)
- `initial_cost` - التكلفة الأولية
- `current_count` - العدد الحالي
- `current_weight` - الوزن الحالي (كجم)
- `lifecycle_stage_id` - مرحلة النمو (ForeignKey إلى `LifecycleStage`)
- `status` - الحالة (active/harvested/terminated)
- `notes` - ملاحظات
- `is_active` - نشط
- `created_at` - تاريخ الإنشاء
- `updated_at` - آخر تحديث

**الفهارس:**
- Index على `batch_number`
- Index على `status`
- Index على `pond_id`

**الخصائص المحسوبة (Properties):**
- `average_weight` - متوسط وزن السمكة
- `estimated_biomass` - تقدير الكتلة الحيوية
- `mortality_count` - عدد النفوق
- `mortality_rate` - معدل النفوق (%)

---

## 2. تطبيق Daily Operations (العمليات اليومية)

### 2.1 FeedingLog (سجل التغذية)
**الجدول:** `daily_operations_feedinglog`

**الحقول:**
- `id` - Primary Key
- `batch_id` - الدفعة (ForeignKey إلى `Batch`)
- `feed_type_id` - نوع العلف (ForeignKey إلى `FeedType`)
- `feeding_date` - تاريخ التغذية
- `quantity` - الكمية (كجم)
- `unit_price` - سعر الوحدة
- `total_cost` - التكلفة الإجمالية (محسوبة تلقائياً)
- `notes` - ملاحظات
- `is_posted` - مُسجل محاسبياً
- `created_by_id` - المسجل (ForeignKey إلى `User`)
- `created_at` - تاريخ الإنشاء
- `updated_at` - آخر تحديث

**الفهارس:**
- Index على `(batch_id, feeding_date)`
- Index على `feeding_date`

---

### 2.2 MortalityLog (سجل النفوق)
**الجدول:** `daily_operations_mortalitylog`

**الحقول:**
- `id` - Primary Key
- `batch_id` - الدفعة (ForeignKey إلى `Batch`)
- `mortality_date` - تاريخ النفوق
- `count` - عدد النفوق
- `average_weight` - متوسط الوزن (كجم)
- `cause` - سبب النفوق
- `notes` - ملاحظات
- `created_by_id` - المسجل (ForeignKey إلى `User`)
- `created_at` - تاريخ الإنشاء
- `updated_at` - آخر تحديث

**الفهارس:**
- Index على `(batch_id, mortality_date)`
- Index على `mortality_date`

---

## 3. تطبيق Sales (المبيعات)

### 3.1 Harvest (الحصاد)
**الجدول:** `sales_harvest`

**الحقول:**
- `id` - Primary Key
- `batch_id` - الدفعة (ForeignKey إلى `Batch`)
- `harvest_date` - تاريخ الحصاد
- `quantity_kg` - الكمية (كجم)
- `count` - العدد
- `average_weight` - متوسط الوزن (كجم)
- `fair_value` - القيمة العادلة
- `cost_per_kg` - التكلفة لكل كيلوجرام
- `status` - الحالة (pending/in_progress/completed/cancelled)
- `notes` - ملاحظات
- `created_by_id` - المسجل (ForeignKey إلى `User`)
- `created_at` - تاريخ الإنشاء
- `updated_at` - آخر تحديث

**الفهارس:**
- Index على `(batch_id, harvest_date)`
- Index على `status`

---

### 3.2 SalesOrder (طلب البيع)
**الجدول:** `sales_salesorder`

**الحقول:**
- `id` - Primary Key
- `order_number` - رقم الطلب (فريد)
- `order_date` - تاريخ الطلب
- `customer_name` - اسم العميل
- `customer_phone` - هاتف العميل
- `customer_address` - عنوان العميل
- `subtotal` - المجموع الفرعي
- `vat_rate` - معدل الضريبة (%)
- `vat_amount` - مبلغ الضريبة
- `total_amount` - المبلغ الإجمالي
- `status` - الحالة (draft/confirmed/invoiced/delivered/cancelled)
- `notes` - ملاحظات
- `created_by_id` - المسجل (ForeignKey إلى `User`)
- `created_at` - تاريخ الإنشاء
- `updated_at` - آخر تحديث

**الفهارس:**
- Index على `order_number`
- Index على `status`

---

### 3.3 SalesOrderLine (بند طلب البيع)
**الجدول:** `sales_salesorderline`

**الحقول:**
- `id` - Primary Key
- `sales_order_id` - طلب البيع (ForeignKey إلى `SalesOrder`)
- `harvest_id` - الحصاد (ForeignKey إلى `Harvest`)
- `quantity_kg` - الكمية (كجم)
- `unit_price` - سعر الكيلوجرام
- `line_total` - المجموع (محسوب تلقائياً)

---

### 3.4 Invoice (الفاتورة)
**الجدول:** `sales_invoice`

**الحقول:**
- `id` - Primary Key
- `invoice_number` - رقم الفاتورة (فريد)
- `sales_order_id` - طلب البيع (OneToOne إلى `SalesOrder`)
- `invoice_date` - تاريخ الفاتورة
- `subtotal` - المجموع الفرعي
- `vat_amount` - مبلغ الضريبة
- `total_amount` - المبلغ الإجمالي
- `status` - الحالة (draft/issued/paid/cancelled)
- `qr_code` - QR Code (ZATCA)
- `uuid` - UUID (ZATCA)
- `signed_xml` - XML الموقع (ZATCA)
- `zatca_status` - حالة ZATCA
- `created_by_id` - المسجل (ForeignKey إلى `User`)
- `created_at` - تاريخ الإنشاء
- `updated_at` - آخر تحديث

**الفهارس:**
- Index على `invoice_number`
- Index على `status`

---

## 4. تطبيق Inventory (المخزون)

### 4.1 FeedType (نوع العلف)
**الجدول:** `inventory_feedtype`

**الحقول:**
- `id` - Primary Key
- `name` - اسم نوع العلف
- `arabic_name` - الاسم العربي
- `description` - الوصف
- `unit` - الوحدة
- `is_active` - نشط
- `created_at` - تاريخ الإنشاء
- `updated_at` - آخر تحديث

---

## 5. تطبيق Accounting (المحاسبة)

### 5.1 Account (الحساب)
**الجدول:** `accounting_account`

**الحقول:**
- `id` - Primary Key
- `code` - رقم الحساب
- `name` - اسم الحساب
- `arabic_name` - الاسم العربي
- `account_type` - نوع الحساب (asset/liability/equity/revenue/expense/biological_asset)
- `parent_id` - الحساب الأب (ForeignKey إلى نفس الجدول)
- `is_active` - نشط
- `created_at` - تاريخ الإنشاء
- `updated_at` - آخر تحديث

---

### 5.2 JournalEntry (القيد المحاسبي)
**الجدول:** `accounting_journalentry`

**الحقول:**
- `id` - Primary Key
- `entry_number` - رقم القيد
- `entry_date` - تاريخ القيد
- `description` - الوصف
- `reference_type` - نوع المرجع (batch/feeding/mortality/harvest/sales)
- `reference_id` - معرف المرجع
- `created_by_id` - المسجل (ForeignKey إلى `User`)
- `created_at` - تاريخ الإنشاء
- `updated_at` - آخر تحديث

---

### 5.3 JournalEntryLine (بند القيد)
**الجدول:** `accounting_journalentryline`

**الحقول:**
- `id` - Primary Key
- `journal_entry_id` - القيد (ForeignKey إلى `JournalEntry`)
- `account_id` - الحساب (ForeignKey إلى `Account`)
- `type` - النوع (debit/credit)
- `amount` - المبلغ
- `description` - الوصف

---

### 5.4 BiologicalAssetRevaluation (إعادة تقييم الأصول البيولوجية)
**الجدول:** `accounting_biologicalassetrevaluation`

**الحقول:**
- `id` - Primary Key
- `batch_id` - الدفعة (ForeignKey إلى `Batch`)
- `revaluation_date` - تاريخ إعادة التقييم
- `previous_fair_value` - القيمة العادلة السابقة
- `new_fair_value` - القيمة العادلة الجديدة
- `change_amount` - مقدار التغيير
- `notes` - ملاحظات
- `created_by_id` - المسجل (ForeignKey إلى `User`)
- `created_at` - تاريخ الإنشاء
- `updated_at` - آخر تحديث

---

## 6. تطبيق Accounts (المستخدمون)

### 6.1 User (المستخدم)
**الجدول:** `accounts_user`

**الحقول:**
- `id` - Primary Key
- `username` - اسم المستخدم
- `email` - البريد الإلكتروني
- `first_name` - الاسم الأول
- `last_name` - اسم العائلة
- `role` - الدور (admin/farm_manager/operator/accountant/sales_manager)
- `is_active` - نشط
- `is_staff` - موظف
- `is_superuser` - مدير عام
- `created_at` - تاريخ الإنشاء
- `updated_at` - آخر تحديث

---

## 7. تطبيق Audit (التدقيق)

### 7.1 AuditLog (سجل التدقيق)
**الجدول:** `audit_auditlog`

**الحقول:**
- `id` - Primary Key
- `user_id` - المستخدم (ForeignKey إلى `User`)
- `action` - الإجراء (create/update/delete)
- `model_name` - اسم النموذج
- `object_id` - معرف الكائن
- `changes` - التغييرات (JSON)
- `ip_address` - عنوان IP
- `user_agent` - User Agent
- `created_at` - تاريخ الإنشاء

**الفهارس:**
- Index على `created_at`
- Index على `(model_name, object_id)`
- Index على `user_id`

---

## 8. ملاحظات مهمة

### 8.1 Soft Delete
جميع النماذج الرئيسية تستخدم `is_active` للحذف المنطقي بدلاً من الحذف الفعلي.

### 8.2 Timestamps
جميع النماذج تحتوي على `created_at` و `updated_at` لتتبع التغييرات.

### 8.3 Foreign Keys
- جميع Foreign Keys تستخدم `on_delete=models.PROTECT` أو `SET_NULL` للحفاظ على سلامة البيانات
- `created_by` يستخدم `on_delete=models.SET_NULL` لتجنب حذف السجلات عند حذف المستخدم

### 8.4 Indexes
- الفهارس موجودة على الحقول المستخدمة في الاستعلامات المتكررة
- الفهارس المركبة موجودة على مجموعات الحقول المستخدمة معاً

---

**تاريخ الإنشاء:** 2024  
**آخر تحديث:** 2024
