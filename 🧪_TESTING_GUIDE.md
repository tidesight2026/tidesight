# 🧪 دليل اختبار الميزات - AquaERP

**التاريخ:** ديسمبر 2025

---

## 🚀 البدء السريع

### 1. التحقق من الخدمات

```bash
# فحص حالة Docker services
docker-compose ps

# يجب أن تكون جميع الخدمات في حالة "Up":
# - web (Backend)
# - db (PostgreSQL)
# - redis (Cache)
# - celery (Async tasks)
# - celery-beat (Scheduled tasks)
```

### 2. Health Check

```bash
# باستخدام PowerShell
Invoke-WebRequest -UseBasicParsing -Uri "http://localhost:8000/api/dashboard/health"

# أو باستخدام Python script
python test_features.py
```

### 3. اختبار تسجيل الدخول

افتح المتصفح: `http://farm1.localhost:5175`

أو استخدم API:
```bash
# Login
$response = Invoke-WebRequest -Method POST -Uri "http://localhost:8000/api/auth/login" `
  -ContentType "application/json" `
  -Body '{"username":"admin","password":"Admin123!"}'

$token = ($response.Content | ConvertFrom-Json).access
```

---

## 📋 اختبارات تفصيلية

### 🔐 1. Authentication & Authorization

#### Login Test
- [ ] تسجيل دخول بنجاح
- [ ] فشل تسجيل دخول (كلمة مرور خاطئة)
- [ ] JWT Token يتم إرجاعه
- [ ] Token يمكن استخدامه للوصول المحمي

#### Permissions Test
- [ ] Owner يمكنه الوصول لكل شيء
- [ ] Manager يمكنه الوصول لمعظم الميزات
- [ ] Accountant يمكنه الوصول للمحاسبة فقط
- [ ] Worker يمكنه الوصول للعمليات فقط
- [ ] Protected routes تظهر/تختفي حسب الصلاحيات

---

### 🐟 2. Biological Data

#### Species
- [ ] عرض قائمة الأنواع (مع Cache)
- [ ] إنشاء نوع جديد
- [ ] تعديل نوع موجود
- [ ] Soft delete (is_active=False)

#### Ponds
- [ ] عرض قائمة الأحواض
- [ ] إنشاء حوض جديد
- [ ] تعديل حوض
- [ ] ربط حوض بموقع مزرعة

#### Batches
- [ ] عرض قائمة الدفعات (مع Pagination)
- [ ] إنشاء دفعة جديدة
- [ ] ربط دفعة بحوض ونوع
- [ ] حساب FCR
- [ ] حساب Biomass
- [ ] تحديث العدد الحي

---

### 📦 3. Inventory

#### Feed Inventory
- [ ] إنشاء نوع علف
- [ ] إضافة مخزون علف
- [ ] عرض المخزون
- [ ] خصم من المخزون عند التغذية

#### Medicine Inventory
- [ ] إنشاء دواء
- [ ] إضافة مخزون دواء
- [ ] عرض المخزون

---

### 📝 4. Daily Operations

#### Feeding Log
- [ ] تسجيل تغذية
- [ ] خصم تلقائي من المخزون
- [ ] قيد محاسبي تلقائي
- [ ] عرض سجلات التغذية
- [ ] حساب FCR

#### Mortality Log
- [ ] تسجيل نفوق
- [ ] تحديث تلقائي للعدد الحي
- [ ] قيد محاسبي تلقائي
- [ ] عرض سجلات النفوق
- [ ] حساب معدل النفوق

---

### 💰 5. Accounting

#### Chart of Accounts
- [ ] عرض الحسابات
- [ ] إنشاء حساب جديد
- [ ] حساب رصيد الحساب
- [ ] عرض حسب نوع الحساب

#### Journal Entries
- [ ] إنشاء قيد محاسبي
- [ ] التحقق من التوازن (Debit = Credit)
- [ ] عرض القيود
- [ ] ترحيل القيد
- [ ] ربط القيود بالعمليات (تلقائي)

#### Reports
- [ ] Trial Balance
- [ ] Balance Sheet
- [ ] حساب الأرصدة

---

### 🌾 6. Sales

#### Harvest
- [ ] إنشاء حصاد
- [ ] ربط حصاد ب batch
- [ ] قيد محاسبي تلقائي
- [ ] تحديث حالة الدفعة

#### Sales Order
- [ ] إنشاء طلب بيع
- [ ] إضافة بنود من الحصاد
- [ ] حساب الضريبة (15%)
- [ ] حساب الإجمالي
- [ ] تحديث حالة الطلب

#### Invoice
- [ ] إنشاء فاتورة من طلب بيع
- [ ] QR Code generation (ZATCA)
- [ ] XML generation (UBL 2.1)
- [ ] PDF Export
- [ ] قيد محاسبي تلقائي
- [ ] عرض الفاتورة

---

### 🏛️ 7. ZATCA Integration

#### QR Code
- [ ] QR Code موجود في Invoice
- [ ] QR Code صحيح (TLV format)
- [ ] QR Code قابل للقراءة
- [ ] QR Code يحتوي على البيانات المطلوبة

#### XML
- [ ] XML موجود
- [ ] XML صحيح (UBL 2.1 format)
- [ ] XML يحتوي على جميع البيانات
- [ ] XML قابل للتحميل

#### PDF
- [ ] PDF يمكن تحميله
- [ ] PDF يحتوي على QR Code
- [ ] PDF يحتوي على جميع البيانات
- [ ] PDF مطابق للتصميم السعودي

---

### 📊 8. IAS 41 Revaluation

#### Revaluation Command
```bash
# داخل Docker container
docker-compose exec web python manage.py revalue_biological_assets \
  --market-price 25.00 \
  --date 2025-01-31
```

- [ ] Command يعمل
- [ ] حساب القيمة الدفترية
- [ ] حساب القيمة العادلة
- [ ] إنشاء قيد محاسبي
- [ ] حفظ Revaluation record

#### API & Frontend
- [ ] قائمة Revaluations
- [ ] Filters تعمل
- [ ] Frontend page يعمل
- [ ] Charts تعرض البيانات

---

### 📋 9. Audit Logging

#### Automatic Logging
- [ ] تسجيل Login
- [ ] تسجيل Logout
- [ ] تسجيل JournalEntry create/update
- [ ] تسجيل Invoice create/update
- [ ] تسجيل Harvest create/update
- [ ] IP tracking
- [ ] User Agent tracking

#### API & Frontend
- [ ] قائمة Audit Logs
- [ ] Filters (action_type, entity_type, date)
- [ ] Frontend page يعمل
- [ ] Permissions (owner/manager only)

---

### ⚡ 10. Performance

#### Caching
- [ ] Dashboard stats cached (60 seconds)
- [ ] Species list cached (600 seconds)
- [ ] Cache invalidation عند التحديث

#### Query Optimization
- [ ] select_related يعمل
- [ ] prefetch_related يعمل
- [ ] Indexes موجودة في قاعدة البيانات

#### Pagination
- [ ] Batches pagination يعمل
- [ ] Page size محدود (max 100)
- [ ] Pagination parameters تعمل

---

### 🎨 11. Frontend

#### i18n
- [ ] Language switcher يعمل
- [ ] RTL/LTR switching
- [ ] Translations موجودة (ar/en)
- [ ] dir attribute يتغير

#### Forms
- [ ] Validation يعمل
- [ ] Error messages بالعربية
- [ ] react-hook-form integration
- [ ] zod validation

#### Charts
- [ ] Dashboard charts تعمل
- [ ] Reports charts تعمل
- [ ] Data visualization صحيح

---

## 🔧 سكريبتات الاختبار

### Python Script
```bash
python test_features.py
```

### Manual API Testing
```bash
# 1. Login
$login = Invoke-WebRequest -Method POST -Uri "http://localhost:8000/api/auth/login" `
  -ContentType "application/json" `
  -Body '{"username":"admin","password":"Admin123!"}'

$token = ($login.Content | ConvertFrom-Json).access

# 2. Dashboard Stats
Invoke-WebRequest -Uri "http://localhost:8000/api/dashboard/stats" `
  -Headers @{Authorization = "Bearer $token"}

# 3. Species List
Invoke-WebRequest -Uri "http://localhost:8000/api/species/" `
  -Headers @{Authorization = "Bearer $token"}
```

---

## 📝 ملاحظات

- سجل أي أخطاء تواجهها
- سجل أي تحسينات مطلوبة
- وثّق أي مشاكل في الأداء

---

**✨ ابدأ الاختبار!** ✨

