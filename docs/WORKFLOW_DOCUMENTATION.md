# توثيق نموذج العمل الحالي في AquaERP

> هذا الملف يوثق تدفق العمل الكامل في AquaERP من إنشاء دفعة أسماك حتى البيع والمحاسبة.

---

## نظرة عامة على تدفق العمل

```
إنشاء دفعة (Batch) 
    ↓
تسجيل عمليات التغذية (Feeding)
    ↓
تسجيل النفوق (Mortality)
    ↓
الحصاد (Harvest)
    ↓
الربط مع المبيعات (Sales)
    ↓
التأثير على المحاسبة (Accounting)
```

---

## 1. إنشاء دفعة أسماك جديدة (Batch)

### الوصف
إنشاء دفعة جديدة من الأسماك في حوض معين.

### النموذج المستخدم
- **`biological.models.Batch`**

### الحقول الأساسية
- `batch_number` - رقم الدفعة (فريد)
- `pond` - الحوض (ForeignKey إلى `Pond`)
- `species` - النوع السمكي (ForeignKey إلى `Species`)
- `start_date` - تاريخ البدء
- `initial_count` - العدد الأولي
- `initial_weight` - الوزن الأولي (كجم)
- `initial_cost` - التكلفة الأولية
- `status` - الحالة (active/harvested/terminated)
- `lifecycle_stage` - مرحلة النمو الحالية

### الحقول المحسوبة تلقائياً
- `current_count` - العدد الحالي (يُحدّث عند النفوق والحصاد)
- `current_weight` - الوزن الحالي (يُحدّث عند النفوق والحصاد)

### التأثير على المحاسبة
- عند إنشاء دفعة جديدة، يتم إنشاء قيد محاسبي:
  - **مدين:** ح/ الأصول البيولوجية (Active Batches)
  - **دائن:** ح/ النقدية/الموردين (حسب طريقة الدفع)

### API Endpoints
- `GET /api/batches/` - قائمة الدفعات
- `POST /api/batches/` - إنشاء دفعة جديدة
- `GET /api/batches/{id}/` - تفاصيل دفعة
- `PUT /api/batches/{id}/` - تحديث دفعة
- `DELETE /api/batches/{id}/` - حذف دفعة

---

## 2. تسجيل عمليات التغذية (Feeding)

### الوصف
تسجيل كل عملية تغذية للدفعة مع نوع العلف والكمية والتكلفة.

### النموذج المستخدم
- **`daily_operations.models.FeedingLog`**

### الحقول الأساسية
- `batch` - الدفعة (ForeignKey إلى `Batch`)
- `feed_type` - نوع العلف (ForeignKey إلى `FeedType`)
- `feeding_date` - تاريخ التغذية
- `quantity` - الكمية (كجم)
- `unit_price` - سعر الوحدة
- `total_cost` - التكلفة الإجمالية (محسوبة تلقائياً: quantity × unit_price)
- `created_by` - المستخدم المسجل
- `is_posted` - هل تم إنشاء قيد محاسبي؟

### التأثير على المحاسبة
- عند تسجيل تغذية:
  - **مدين:** ح/ تكلفة العلف (Feed Cost)
  - **دائن:** ح/ مخزون العلف (Feed Inventory)
- يتم تحديث التكلفة التراكمية للدفعة

### API Endpoints
- `GET /api/operations/feeding-logs/` - قائمة سجلات التغذية
- `POST /api/operations/feeding-logs/` - إنشاء سجل تغذية
- `GET /api/operations/feeding-logs/{id}/` - تفاصيل سجل
- `PUT /api/operations/feeding-logs/{id}/` - تحديث سجل
- `DELETE /api/operations/feeding-logs/{id}/` - حذف سجل

---

## 3. تسجيل النفوق (Mortality)

### الوصف
تسجيل حالات النفوق في الدفعة مع السبب والعدد.

### النموذج المستخدم
- **`daily_operations.models.MortalityLog`**

### الحقول الأساسية
- `batch` - الدفعة (ForeignKey إلى `Batch`)
- `mortality_date` - تاريخ النفوق
- `count` - عدد النفوق
- `average_weight` - متوسط الوزن (كجم) - اختياري
- `cause` - سبب النفوق - اختياري
- `notes` - ملاحظات
- `created_by` - المستخدم المسجل

### التأثير على الدفعة
- عند تسجيل نفوق:
  - يتم تحديث `current_count` في الدفعة (يُطرح العدد)
  - يتم تحديث `current_weight` في الدفعة (يُطرح الوزن)

### التأثير على المحاسبة
- عند تسجيل نفوق:
  - **مدين:** ح/ خسائر النفوق (Mortality Loss)
  - **دائن:** ح/ الأصول البيولوجية (Active Batches)

### API Endpoints
- `GET /api/operations/mortality-logs/` - قائمة سجلات النفوق
- `POST /api/operations/mortality-logs/` - إنشاء سجل نفوق
- `GET /api/operations/mortality-logs/{id}/` - تفاصيل سجل
- `PUT /api/operations/mortality-logs/{id}/` - تحديث سجل
- `DELETE /api/operations/mortality-logs/{id}/` - حذف سجل

---

## 4. الحصاد (Harvest)

### الوصف
تحويل الأصل البيولوجي (الدفعة) إلى منتج تام جاهز للبيع.

### النموذج المستخدم
- **`sales.models.Harvest`**

### الحقول الأساسية
- `batch` - الدفعة (ForeignKey إلى `Batch`)
- `harvest_date` - تاريخ الحصاد
- `quantity_kg` - الكمية المحصودة (كجم)
- `count` - عدد الأسماك المحصودة
- `average_weight` - متوسط الوزن (محسوب تلقائياً)
- `fair_value` - القيمة العادلة
- `cost_per_kg` - التكلفة لكل كيلوجرام
- `status` - الحالة (pending/in_progress/completed/cancelled)

### التأثير على الدفعة
- عند إكمال الحصاد (`status='completed'`):
  - يتم تحديث `current_count` و `current_weight` في الدفعة
  - إذا تم حصاد كل الدفعة، يتم تغيير `status` إلى `'harvested'`

### التأثير على المحاسبة
- عند إكمال الحصاد:
  - **مدين:** ح/ مخزون منتج تام (Finished Goods)
  - **دائن:** ح/ الأصول البيولوجية (Active Batches)
- القيمة المستخدمة: `fair_value` أو `cost_per_kg × quantity_kg`

### API Endpoints
- `GET /api/sales/harvests/` - قائمة الحصاد
- `POST /api/sales/harvests/` - إنشاء حصاد
- `GET /api/sales/harvests/{id}/` - تفاصيل حصاد
- `PUT /api/sales/harvests/{id}/` - تحديث حصاد
- `DELETE /api/sales/harvests/{id}/` - حذف حصاد

---

## 5. الربط مع المبيعات (Sales)

### الوصف
ربط الحصاد بطلبات البيع والفواتير.

### النماذج المستخدمة
- **`sales.models.SalesOrder`** - طلب البيع
- **`sales.models.SalesOrderLine`** - بند طلب البيع (يربط `Harvest` بـ `SalesOrder`)
- **`sales.models.Invoice`** - الفاتورة

### تدفق المبيعات
1. **إنشاء طلب بيع (SalesOrder)**
   - `order_number` - رقم الطلب
   - `customer_name` - اسم العميل
   - `order_date` - تاريخ الطلب
   - `status` - الحالة (draft/confirmed/invoiced/delivered/cancelled)

2. **إضافة بنود الطلب (SalesOrderLine)**
   - كل بند مرتبط بـ `Harvest` محدد
   - `quantity_kg` - الكمية المباعة (كجم)
   - `unit_price` - سعر الكيلوجرام
   - `line_total` - المجموع (محسوب تلقائياً)

3. **إنشاء فاتورة (Invoice)**
   - `invoice_number` - رقم الفاتورة
   - مرتبط بـ `SalesOrder` (OneToOne)
   - `subtotal`, `vat_amount`, `total_amount`
   - دعم ZATCA (QR Code, UUID, signed XML)

### التأثير على المحاسبة
- عند إنشاء فاتورة:
  - **مدين:** ح/ العملاء (Accounts Receivable)
  - **دائن:** ح/ الإيرادات (Revenue)
  - **دائن:** ح/ ضريبة القيمة المضافة (VAT Payable)
- عند البيع من المخزون:
  - **مدين:** ح/ تكلفة البضاعة المباعة (COGS)
  - **دائن:** ح/ مخزون منتج تام (Finished Goods)

### API Endpoints
- `GET /api/sales/orders/` - قائمة طلبات البيع
- `POST /api/sales/orders/` - إنشاء طلب بيع
- `GET /api/sales/invoices/` - قائمة الفواتير
- `POST /api/sales/invoices/` - إنشاء فاتورة

---

## 6. التأثير على المحاسبة (Accounting)

### الوصف
كل عملية في النظام تؤثر على المحاسبة عبر قيود تلقائية.

### النموذج المستخدم
- **`accounting.models.JournalEntry`** - القيد المحاسبي
- **`accounting.models.JournalEntryLine`** - بند القيد

### القيود التلقائية

#### 1. عند إنشاء دفعة
```
مدين: ح/ الأصول البيولوجية (Active Batches) - initial_cost
دائن: ح/ النقدية/الموردين - initial_cost
```

#### 2. عند تسجيل تغذية
```
مدين: ح/ تكلفة العلف (Feed Cost) - total_cost
دائن: ح/ مخزون العلف (Feed Inventory) - total_cost
```

#### 3. عند تسجيل نفوق
```
مدين: ح/ خسائر النفوق (Mortality Loss) - قيمة النفوق
دائن: ح/ الأصول البيولوجية (Active Batches) - قيمة النفوق
```

#### 4. عند الحصاد
```
مدين: ح/ مخزون منتج تام (Finished Goods) - fair_value
دائن: ح/ الأصول البيولوجية (Active Batches) - fair_value
```

#### 5. عند إنشاء فاتورة
```
مدين: ح/ العملاء (Accounts Receivable) - total_amount
دائن: ح/ الإيرادات (Revenue) - subtotal
دائن: ح/ ضريبة القيمة المضافة (VAT Payable) - vat_amount
```

#### 6. عند البيع من المخزون
```
مدين: ح/ تكلفة البضاعة المباعة (COGS) - cost_per_kg × quantity_kg
دائن: ح/ مخزون منتج تام (Finished Goods) - cost_per_kg × quantity_kg
```

### API Endpoints
- `GET /api/accounting/journal-entries/` - قائمة القيود
- `GET /api/accounting/accounts/` - قائمة الحسابات

---

## 7. العلاقات بين النماذج

### مخطط العلاقات

```
Pond (حوض)
  └── Batch (دفعة)
      ├── FeedingLog (سجلات التغذية)
      ├── MortalityLog (سجلات النفوق)
      └── Harvest (حصاد)
          └── SalesOrderLine (بند طلب بيع)
              └── SalesOrder (طلب بيع)
                  └── Invoice (فاتورة)
```

### العلاقات الرئيسية
- `Batch.pond` → `Pond` (Many-to-One)
- `Batch.species` → `Species` (Many-to-One)
- `FeedingLog.batch` → `Batch` (Many-to-One)
- `MortalityLog.batch` → `Batch` (Many-to-One)
- `Harvest.batch` → `Batch` (Many-to-One)
- `SalesOrderLine.harvest` → `Harvest` (Many-to-One)
- `SalesOrderLine.sales_order` → `SalesOrder` (Many-to-One)
- `Invoice.sales_order` → `SalesOrder` (One-to-One)

---

## 8. الحسابات والمؤشرات

### الحسابات المتاحة في Batch
- `average_weight` - متوسط وزن السمكة الواحدة
- `estimated_biomass` - تقدير الكتلة الحيوية
- `mortality_count` - عدد النفوق
- `mortality_rate` - معدل النفوق (%)

### الحسابات المطلوبة (قيد التطوير)
- معدل النمو (Weight Gain)
- معامل تحويل العلف (FCR - Feed Conversion Ratio)
- نسبة النفوق (Mortality Rate) - موجود بالفعل

---

## 9. حالات الدفعة (Batch Status)

- **`active`** - نشط: الدفعة قيد التربية
- **`harvested`** - محصود: تم حصاد الدفعة بالكامل
- **`terminated`** - منتهي: الدفعة انتهت (نفوق كامل أو إلغاء)

---

## 10. ملاحظات مهمة

1. **Soft Delete**: جميع النماذج تستخدم `is_active` للحذف المنطقي
2. **Audit Logging**: جميع العمليات تُسجل في `audit.models.AuditLog`
3. **Permissions**: كل عملية تتطلب صلاحيات محددة
4. **Signals**: يتم استخدام Django Signals لإنشاء القيود المحاسبية تلقائياً
5. **Multi-tenancy**: النظام يدعم Multi-tenancy عبر `tenants` app

---

## 11. الملفات ذات الصلة

### Backend
- `biological/models.py` - نماذج Batch, Pond, Species
- `daily_operations/models.py` - نماذج FeedingLog, MortalityLog
- `sales/models.py` - نماذج Harvest, SalesOrder, Invoice
- `accounting/models.py` - نماذج JournalEntry, Account
- `sales/signals.py` - إشارات لإنشاء القيود المحاسبية
- `api/operations.py` - APIs للعمليات اليومية
- `api/sales.py` - APIs للمبيعات
- `api/batches.py` - APIs للدفعات

### Frontend
- `frontend/src/pages/Batches.tsx` - صفحة إدارة الدفعات
- `frontend/src/pages/FeedingLogs.tsx` - صفحة سجلات التغذية
- `frontend/src/pages/MortalityLogs.tsx` - صفحة سجلات النفوق
- `frontend/src/pages/Harvests.tsx` - صفحة الحصاد
- `frontend/src/pages/SalesOrders.tsx` - صفحة طلبات البيع
- `frontend/src/pages/Invoices.tsx` - صفحة الفواتير

---

**تاريخ الإنشاء:** 2024  
**آخر تحديث:** 2024
