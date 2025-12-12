# كيفية الوصول إلى Tenant - AquaERP

## 📋 الخطوات الكاملة

### 1. إنشاء Tenant

1. **افتح Public Schema Admin:**
   - http://localhost:8000/admin/

2. **أنشئ Client جديد:**
   - **اسم الشركة:** `Tilapia Marine Company`
   - **Schema Name:** سيتم توليده تلقائياً (مثل: `tilapia_marine_company`)
   - **البريد الإلكتروني:** `info@tilapia.com`
   - **نوع الاشتراك:** اختر من القائمة

3. **احفظ**

### 2. إضافة Domain

1. **افتح صفحة إضافة Domain:**
   - http://localhost:8000/admin/tenants/domain/add/

2. **املأ البيانات:**
   - **Domain:** `tmco.localhost` ⚠️ **hostname فقط!**
   - **Tenant:** اختر `Tilapia Marine Company`
   - **Is primary:** ✓

3. **احفظ**

### 3. إضافة Domain إلى hosts file

**في Windows:**
1. افتح `C:\Windows\System32\drivers\etc\hosts` كمسؤول
2. أضف السطر:
   ```
   127.0.0.1    tmco.localhost
   ```
3. احفظ الملف

**في Linux/Mac:**
1. افتح `/etc/hosts` كمسؤول
2. أضف السطر:
   ```
   127.0.0.1    tmco.localhost
   ```
3. احفظ الملف

### 4. تشغيل Migrations للـ Tenant

```bash
docker-compose exec web python manage.py migrate_schemas --tenant --schema_name tilapia_marine_company
```

(استخدم `schema_name` من Tenant الذي أنشأته)

### 5. إنشاء مستخدم Admin في Tenant

```bash
docker-compose exec web python create_admin_user.py
```

عدّل في `create_admin_user.py`:
- `SCHEMA_NAME = 'tilapia_marine_company'`
- `USERNAME = 'admin'`
- `PASSWORD = 'admin123'`

### 6. الوصول إلى Tenant

افتح:
```
http://tmco.localhost:8000/admin/
```

**بيانات تسجيل الدخول:**
- Username: `admin`
- Password: `admin123`

---

## ⚠️ أخطاء شائعة

### خطأ: "Page not found at /tmco"

**السبب:** Domain غير صحيح أو غير موجود في hosts file

**الحل:**
1. تأكد من أن Domain هو `tmco.localhost` وليس `http://localhost:8000/tmco`
2. أضف `127.0.0.1 tmco.localhost` إلى hosts file
3. أعد تشغيل المتصفح

### خطأ: "No tenant for hostname 'tmco.localhost'"

**السبب:** Domain غير موجود في قاعدة البيانات

**الحل:**
1. تأكد من إنشاء Domain في Admin
2. تأكد من أن Domain هو `tmco.localhost` (hostname فقط)

---

## 📝 ملاحظات

- **Domain = Hostname فقط:** `tmco.localhost` ✅
- **ليس URL كامل:** `http://localhost:8000/tmco` ❌
- **Hosts File:** ضروري للوصول محلياً
- **Schema Name:** يتم توليده تلقائياً من اسم الشركة

---

**تاريخ الإنشاء:** 2025-12-11
