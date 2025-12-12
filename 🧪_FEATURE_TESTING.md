# 🧪 اختبار الميزات - AquaERP

**التاريخ:** ديسمبر 2025  
**الحالة:** 🔄 قيد الاختبار

---

## ✅ قائمة الاختبارات

### 1. البنية التحتية

#### Docker Services

- [ ] جميع الخدمات تعمل
- [ ] Database متصل
- [ ] Redis متصل
- [ ] Web server يعمل

#### Health Check

- [ ] API Health endpoint يعمل
- [ ] Frontend يعمل

---

### 2. المصادقة (Authentication)

#### Login

- [ ] تسجيل دخول ناجح
- [ ] فشل تسجيل دخول (كلمة مرور خاطئة)
- [ ] JWT Token يتم إرجاعه
- [ ] Refresh Token يعمل

#### API Authentication

- [ ] Endpoints محمية بـ Token
- [ ] Invalid Token يرفض
- [ ] Expired Token يرفض

---

### 3. Permissions System

#### Role-Based Access

- [ ] Owner يمكنه الوصول لكل شيء
- [ ] Manager يمكنه الوصول لمعظم الميزات
- [ ] Accountant يمكنه الوصول للمحاسبة والمبيعات
- [ ] Worker يمكنه الوصول للعمليات فقط
- [ ] Viewer يمكنه العرض فقط

#### Feature-Based Access

- [ ] Protected routes في Frontend
- [ ] Protected API endpoints
- [ ] Sidebar items تظهر حسب الصلاحيات

---

### 4. البيانات البيولوجية

#### Species

- [ ] إنشاء نوع جديد
- [ ] قائمة الأنواع (مع Cache)
- [ ] تعديل نوع
- [ ] حذف نوع (soft delete)

#### Ponds

- [ ] إنشاء حوض
- [ ] قائمة الأحواض
- [ ] تعديل حوض
- [ ] حذف حوض

#### Batches

- [ ] إنشاء دفعة
- [ ] قائمة الدفعات (مع Pagination)
- [ ] عرض تفاصيل دفعة
- [ ] تعديل دفعة
- [ ] حساب FCR
- [ ] حساب Biomass

---

### 5. المخزون

#### Feed Inventory

- [ ] إنشاء نوع علف
- [ ] إضافة مخزون علف
- [ ] خصم من المخزون
- [ ] قائمة المخزون

#### Medicine Inventory

- [ ] إنشاء دواء
- [ ] إضافة مخزون دواء
- [ ] قائمة الأدوية

---

### 6. العمليات اليومية

#### Feeding Log

- [ ] تسجيل تغذية
- [ ] خصم تلقائي من المخزون
- [ ] قيد محاسبي تلقائي
- [ ] قائمة سجلات التغذية

#### Mortality Log

- [ ] تسجيل نفوق
- [ ] تحديث تلقائي للعدد الحي
- [ ] قيد محاسبي تلقائي
- [ ] قائمة سجلات النفوق

---

### 7. المحاسبة

#### Chart of Accounts

- [ ] عرض الحسابات
- [ ] إنشاء حساب جديد
- [ ] حساب رصيد الحساب

#### Journal Entries

- [ ] إنشاء قيد محاسبي
- [ ] التحقق من التوازن (Debit = Credit)
- [ ] قائمة القيود
- [ ] ربط القيود بالعمليات (Tự động)

#### Reports

- [ ] Trial Balance
- [ ] Balance Sheet
- [ ] حساب الرصيد

---

### 8. المبيعات

#### Harvest

- [ ] إنشاء حصاد
- [ ] قيد محاسبي تلقائي
- [ ] تحديث حالة الدفعة

#### Sales Order

- [ ] إنشاء طلب بيع
- [ ] إضافة بنود من الحصاد
- [ ] حساب الضريبة
- [ ] حساب الإجمالي

#### Invoice

- [ ] إنشاء فاتورة من طلب بيع
- [ ] QR Code generation
- [ ] XML generation
- [ ] PDF Export
- [ ] قيد محاسبي تلقائي

---

### 9. ZATCA Integration

#### QR Code

- [ ] QR Code موجود في Invoice
- [ ] QR Code صحيح (TLV format)
- [ ] QR Code قابل للقراءة

#### XML

- [ ] XML موجود
- [ ] XML صحيح (UBL 2.1)
- [ ] XML يحتوي على جميع البيانات المطلوبة

#### PDF

- [ ] PDF يمكن تحميله
- [ ] PDF يحتوي على QR Code
- [ ] PDF يحتوي على جميع البيانات

---

### 10. IAS 41 Revaluation

#### Revaluation Command

- [ ] Command يعمل
- [ ] حساب القيمة الدفترية
- [ ] حساب القيمة العادلة
- [ ] إنشاء قيد محاسبي
- [ ] حفظ Revaluation record

#### API

- [ ] قائمة Revaluations
- [ ] Filters تعمل
- [ ] Frontend page يعمل

---

### 11. Audit Logging

#### Automatic Logging

- [ ] تسجيل Login
- [ ] تسجيل Logout
- [ ] تسجيل JournalEntry create/update
- [ ] تسجيل Invoice create/update
- [ ] تسجيل Harvest create/update

#### API

- [ ] قائمة Audit Logs
- [ ] Filters تعمل (action_type, entity_type, date)
- [ ] Frontend page يعمل
- [ ] Permissions (owner/manager only)

---

### 12. Performance

#### Caching

- [ ] Dashboard stats cached
- [ ] Species list cached
- [ ] Cache invalidation

#### Query Optimization

- [ ] select_related يعمل
- [ ] prefetch_related يعمل
- [ ] Indexes موجودة

#### Pagination

- [ ] Batches pagination يعمل
- [ ] Page size محدود

---

### 13. Frontend Features

#### i18n

- [ ] Language switcher يعمل
- [ ] RTL/LTR switching
- [ ] Translations موجودة

#### Forms

- [ ] Validation يعمل
- [ ] Error messages بالعربية
- [ ] react-hook-form integration

#### Charts

- [ ] Dashboard charts تعمل
- [ ] Reports charts تعمل
- [ ] Data visualization صحيح

---

## 🔧 سكريبت الاختبار السريع

```bash
# 1. التحقق من الخدمات
docker-compose ps

# 2. Health check
curl http://farm1.localhost:8000/api/dashboard/health

# 3. Login test
curl -X POST http://farm1.localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "Admin123!"}'

# 4. Test authenticated endpoint
curl http://farm1.localhost:8000/api/dashboard/stats \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📝 ملاحظات الاختبار

- سجل أي أخطاء تواجهها
- سجل أي تحسينات مطلوبة
- وثّق أي مشاكل في الأداء

---

**✨ ابدأ الاختبار!** ✨
