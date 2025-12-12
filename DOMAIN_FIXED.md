# ✅ تم إصلاح Domain - AquaERP

## ✅ ما تم إنجازه

تم إصلاح Domain من `http://localhost:8000/tmco` إلى `tmco.localhost` ✅

---

## 📋 الخطوات التالية

### 1. إضافة Domain إلى hosts file

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

### 2. تشغيل Migrations للـ Tenant

```bash
docker-compose exec web python manage.py migrate_schemas --tenant --schema_name tilapia_marine_company
```

### 3. إنشاء مستخدم Admin في Tenant

عدّل `create_admin_user.py`:
- `SCHEMA_NAME = 'tilapia_marine_company'`
- `USERNAME = 'admin'`
- `PASSWORD = 'admin123'`

ثم شغّل:
```bash
docker-compose exec web python create_admin_user.py
```

### 4. الوصول إلى Tenant

افتح:
```
http://tmco.localhost:8000/admin/
```

**بيانات تسجيل الدخول:**
- Username: `admin`
- Password: `admin123`

---

## ✅ الحالة الحالية

- ✅ Domain تم إصلاحه: `tmco.localhost`
- ✅ Tenant موجود: `Tilapia Marine Company`
- ✅ Schema موجود: `tilapia_marine_company`
- ⏳ يحتاج إلى migrations
- ⏳ يحتاج إلى مستخدم admin

---

## 📝 ملاحظات

- **Domain الصحيح:** `tmco.localhost` ✅
- **Domain الخاطئ:** `http://localhost:8000/tmco` ❌
- **في django-tenants:** Domain يجب أن يكون hostname فقط

---

**تاريخ الإصلاح:** 2025-12-11
