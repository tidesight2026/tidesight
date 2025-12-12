# 🧪 تعليمات اختبار الميزات - AquaERP

**التاريخ:** ديسمبر 2025

---

## ✅ الإصلاحات المطبقة

1. ✅ إصلاح `Optional` import في `api/batches.py`
2. ✅ تثبيت `reportlab` في Docker container
3. ✅ جميع الخدمات تعمل

---

## 🚀 خطوات الاختبار السريع

### 1. التحقق من الخدمات

```bash
docker-compose ps
```

يجب أن تكون جميع الخدمات **Up**:
- ✅ web (Backend)
- ✅ db (PostgreSQL)
- ✅ redis (Cache)
- ✅ celery (Async tasks)
- ✅ celery-beat (Scheduled tasks)

---

### 2. اختبار Health Check

**في PowerShell:**
```powershell
Invoke-WebRequest -UseBasicParsing -Uri "http://localhost:8000/api/dashboard/health"
```

**النتيجة المتوقعة:**
```json
{
  "status": "healthy",
  "service": "AquaERP API",
  "version": "1.0.0"
}
```

---

### 3. اختبار تسجيل الدخول

#### الطريقة 1: عبر المتصفح
1. افتح: `http://farm1.localhost:5175`
2. أدخل:
   - Username: `admin`
   - Password: `Admin123!`
3. يجب الانتقال إلى Dashboard

#### الطريقة 2: عبر API
```powershell
$loginResponse = Invoke-WebRequest -Method POST `
  -Uri "http://localhost:8000/api/auth/login" `
  -ContentType "application/json" `
  -Body '{"username":"admin","password":"Admin123!"}'

$token = ($loginResponse.Content | ConvertFrom-Json).access
Write-Host "Token: $token"
```

---

### 4. اختبار Dashboard Stats

```powershell
$statsResponse = Invoke-WebRequest `
  -Uri "http://localhost:8000/api/dashboard/stats" `
  -Headers @{Authorization = "Bearer $token"}

$statsResponse.Content | ConvertFrom-Json
```

**النتيجة المتوقعة:**
```json
{
  "total_ponds": 0,
  "active_batches": 0,
  "total_biomass": 0.0,
  "mortality_rate": 0.0,
  "total_feed_value": 0.0,
  "total_medicine_value": 0.0
}
```

---

### 5. اختبار الميزات الرئيسية

#### A. الأنواع السمكية (Species)
1. افتح: `http://farm1.localhost:5175/farm`
2. اضغط "إضافة نوع"
3. أدخل بيانات النوع
4. احفظ

#### B. الأحواض (Ponds)
1. افتح: `http://farm1.localhost:5175/ponds`
2. اضغط "إضافة حوض"
3. أدخل بيانات الحوض
4. احفظ

#### C. الدفعات (Batches)
1. افتح: `http://farm1.localhost:5175/batches`
2. اضغط "إضافة دفعة"
3. اختر حوض ونوع
4. أدخل بيانات الدفعة
5. احفظ

#### D. المخزون (Inventory)
1. افتح: `http://farm1.localhost:5175/inventory`
2. أضف نوع علف
3. أضف مخزون علف
4. تحقق من خصم المخزون عند التغذية

#### E. العمليات اليومية (Operations)
1. افتح: `http://farm1.localhost:5175/operations`
2. Tab "التغذية"
3. أضف سجل تغذية
4. Tab "النفوق"
5. أضف سجل نفوق
6. تحقق من تحديث العدد الحي

#### F. المحاسبة (Accounting)
1. افتح: `http://farm1.localhost:5175/accounting`
2. Tab "الحسابات" - عرض الحسابات
3. Tab "القيود" - عرض القيود التلقائية
4. Tab "ميزان المراجعة" - عرض الميزان
5. Tab "الميزانية العمومية" - عرض الميزانية

#### G. المبيعات (Sales)
1. افتح: `http://farm1.localhost:5175/harvests`
2. أضف حصاد من دفعة
3. افتح: `http://farm1.localhost:5175/sales-orders`
4. أنشئ طلب بيع
5. افتح: `http://farm1.localhost:5175/invoices`
6. أنشئ فاتورة من الطلب
7. تحقق من:
   - QR Code موجود
   - يمكن تحميل PDF
   - قيد محاسبي تم إنشاؤه

#### H. التقارير (Reports)
1. افتح: `http://farm1.localhost:5175/reports`
2. اختر نوع التقرير:
   - Cost per Kg
   - Batch Profitability
   - Feed Efficiency
   - Mortality Analysis
3. تحقق من عرض البيانات والرسوم البيانية

#### I. Audit Logs
1. افتح: `http://farm1.localhost:5175/audit-logs`
2. تحقق من ظهور السجلات
3. جرب Filters:
   - نوع العملية
   - نوع الكيان
   - التاريخ

#### J. IAS 41 Revaluation
1. افتح: `http://farm1.localhost:5175/biological-asset-revaluations`
2. في Docker:
   ```bash
   docker-compose exec web python manage.py revalue_biological_assets \
     --market-price 25.00 \
     --date 2025-01-31
   ```
3. تحقق من ظهور Revaluation في الصفحة

---

## 🔍 اختبارات متقدمة

### Performance Testing

#### Cache Test:
```powershell
# أول طلب (slow - no cache)
Measure-Command {
  Invoke-WebRequest -Uri "http://localhost:8000/api/dashboard/stats" `
    -Headers @{Authorization = "Bearer $token"}
}

# ثاني طلب (fast - cached)
Measure-Command {
  Invoke-WebRequest -Uri "http://localhost:8000/api/dashboard/stats" `
    -Headers @{Authorization = "Bearer $token"}
}
```

#### Pagination Test:
```powershell
# صفحة 1
Invoke-WebRequest -Uri "http://localhost:8000/api/batches/?page=1&page_size=10" `
  -Headers @{Authorization = "Bearer $token"}

# صفحة 2
Invoke-WebRequest -Uri "http://localhost:8000/api/batches/?page=2&page_size=10" `
  -Headers @{Authorization = "Bearer $token"}
```

---

## ✅ قائمة التحقق النهائية

### Backend:
- [ ] Django check passes
- [ ] Health endpoint works
- [ ] Login works
- [ ] All API endpoints accessible
- [ ] Permissions work
- [ ] Cache works
- [ ] Indexes exist

### Frontend:
- [ ] Login page works
- [ ] Dashboard displays
- [ ] All pages load
- [ ] Forms work
- [ ] Charts display
- [ ] i18n works
- [ ] RTL/LTR switching

### Integration:
- [ ] Feeding Log creates journal entry
- [ ] Mortality Log creates journal entry
- [ ] Harvest creates journal entry
- [ ] Invoice creates journal entry
- [ ] ZATCA QR Code generated
- [ ] PDF generated
- [ ] Audit logging works

---

## 🐛 المشاكل المحتملة وحلولها

### Problem: Health check fails
**Solution:** تأكد من أن `web` service يعمل:
```bash
docker-compose restart web
```

### Problem: Login fails
**Solution:** 
- تحقق من بيانات المستخدم
- تحقق من Tenant domain (farm1.localhost)

### Problem: Permission denied
**Solution:**
- تأكد من أن المستخدم لديه الصلاحيات المطلوبة
- تحقق من role في database

### Problem: Cache not working
**Solution:**
- تحقق من أن Redis يعمل
- تحقق من `CACHES` configuration

---

**✨ ابدأ الاختبار الآن!** ✨

