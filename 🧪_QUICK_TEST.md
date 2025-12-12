# 🧪 اختبار سريع - AquaERP

**التاريخ:** ديسمبر 2025

---

## ✅ حالة النظام

### الخدمات:
- ✅ **web** - Backend (Up)
- ✅ **db** - PostgreSQL (Up, Healthy)
- ✅ **redis** - Cache (Up, Healthy)
- ✅ **celery** - Async tasks (Up)
- ✅ **celery-beat** - Scheduled tasks (Up)

### التحقق:
- ✅ Django check passes
- ✅ reportlab مثبت
- ✅ Cache configured

---

## 🚀 اختبارات سريعة

### 1. Health Check ✅

```powershell
Invoke-WebRequest -UseBasicParsing -Uri "http://localhost:8000/api/dashboard/health"
```

**النتيجة المتوقعة:**
```json
{"status": "healthy", "service": "AquaERP API", "version": "1.0.0"}
```

---

### 2. تسجيل الدخول

افتح المتصفح: **http://farm1.localhost:5175**

**بيانات الدخول:**
- Username: `admin`
- Password: `Admin123!`

---

### 3. اختبار الميزات عبر Frontend

#### Dashboard 📊
- URL: `http://farm1.localhost:5175/dashboard`
- تحقق من:
  - عرض الإحصائيات
  - Charts تعمل
  - Cache يعمل (استجابة سريعة)

#### Biological Data 🐟
- **Species:** `http://farm1.localhost:5175/farm`
- **Ponds:** `http://farm1.localhost:5175/ponds`
- **Batches:** `http://farm1.localhost:5175/batches`
- تحقق من:
  - CRUD operations
  - Pagination في Batches
  - Cache في Species list

#### Inventory 📦
- URL: `http://farm1.localhost:5175/inventory`
- تحقق من:
  - إضافة Feed/Medicine
  - عرض المخزون

#### Daily Operations 📝
- URL: `http://farm1.localhost:5175/operations`
- تحقق من:
  - تسجيل Feeding Log
  - خصم من المخزون
  - قيد محاسبي تلقائي
  - تسجيل Mortality Log
  - تحديث العدد الحي

#### Accounting 💰
- URL: `http://farm1.localhost:5175/accounting`
- تحقق من:
  - Chart of Accounts
  - Journal Entries
  - Trial Balance
  - Balance Sheet

#### Sales 🌾
- **Harvests:** `http://farm1.localhost:5175/harvests`
- **Sales Orders:** `http://farm1.localhost:5175/sales-orders`
- **Invoices:** `http://farm1.localhost:5175/invoices`
- تحقق من:
  - إنشاء Harvest
  - إنشاء Sales Order
  - إنشاء Invoice
  - QR Code موجود
  - PDF Export يعمل

#### Reports 📈
- URL: `http://farm1.localhost:5175/reports`
- تحقق من:
  - Cost per Kg Report
  - Batch Profitability
  - Feed Efficiency
  - Mortality Analysis
  - Charts تعمل

#### Audit Logs 📋
- URL: `http://farm1.localhost:5175/audit-logs`
- تحقق من:
  - عرض السجلات
  - Filters تعمل
  - Permissions (owner/manager only)

#### IAS 41 Revaluation 📊
- URL: `http://farm1.localhost:5175/biological-asset-revaluations`
- تحقق من:
  - عرض Revaluations
  - Filters تعمل

---

### 4. اختبار Permissions

#### اختبار مع roles مختلفة:
1. Login كـ **owner** - يجب الوصول لكل شيء
2. Login كـ **manager** - يجب الوصول لمعظم الميزات
3. Login كـ **accountant** - يجب الوصول للمحاسبة والمبيعات فقط
4. Login كـ **worker** - يجب الوصول للعمليات فقط

---

### 5. اختبار Performance

#### Cache Test:
1. افتح Dashboard
2. لاحظ وقت التحميل الأول (قد يكون بطيئاً)
3. حدّث الصفحة (F5)
4. لاحظ وقت التحميل الثاني (يجب أن يكون سريعاً - cached)

#### Pagination Test:
1. افتح Batches page
2. لاحظ عدد العناصر في الصفحة (20 افتراضياً)
3. جرب تغيير `page_size` في URL

---

## 📝 سجل النتائج

### ✅ نجح:
- [ ] Health Check
- [ ] Login
- [ ] Dashboard
- [ ] Species CRUD
- [ ] Ponds CRUD
- [ ] Batches CRUD (مع Pagination)
- [ ] Inventory CRUD
- [ ] Feeding Log
- [ ] Mortality Log
- [ ] Accounting Reports
- [ ] Harvest
- [ ] Sales Order
- [ ] Invoice
- [ ] PDF Export
- [ ] ZATCA QR Code
- [ ] Audit Logs
- [ ] IAS 41 Revaluation
- [ ] Permissions
- [ ] Cache
- [ ] i18n

### ❌ فشل:
- [ ] (سجل أي مشاكل هنا)

### ⚠️ ملاحظات:
- (سجل أي ملاحظات هنا)

---

**✨ ابدأ الاختبار!** ✨

