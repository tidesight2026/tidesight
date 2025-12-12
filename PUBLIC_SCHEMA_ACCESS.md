# الوصول إلى Public Schema - AquaERP

## ⚠️ المشكلة

عند محاولة الوصول إلى `http://localhost:8000/admin/`، يظهر الخطأ:
```
No tenant for hostname 'localhost'
```

## ✅ الحل المطبق

تم إضافة إعداد في `settings.py`:

```python
SHOW_PUBLIC_IF_NO_TENANT_FOUND = True
```

هذا الإعداد يسمح لـ `django-tenants` بالوصول إلى public schema عندما لا يتم العثور على tenant للـ hostname.

## 🚀 كيفية الوصول

### 1. الوصول إلى Public Schema Admin

افتح المتصفح وانتقل إلى:
```
http://localhost:8000/admin/
```

أو

```
http://127.0.0.1:8000/admin/
```

### 2. تسجيل الدخول

إذا لم يكن لديك مستخدم في public schema، أنشئه:

```bash
docker-compose exec web python manage.py createsuperuser
```

**ملاحظة:** بدون `--schema_name`، سيتم إنشاء المستخدم في public schema.

### 3. إنشاء Tenants

بعد تسجيل الدخول، يمكنك:
1. الانتقال إلى **"إدارة العملاء"** → **"العملاء"**
2. إضافة عميل جديد
3. إضافة Domain للعميل الجديد

## 📝 ملاحظات

- **Public Schema:** يستخدم لإدارة Tenants والـ Plans والـ Subscriptions
- **Tenant Schema:** يستخدم لإدارة بيانات كل tenant (مثل `farm1.localhost:8000`)
- **SHOW_PUBLIC_IF_NO_TENANT_FOUND:** يسمح بالوصول إلى public schema عندما لا يوجد tenant للـ hostname

## 🔗 روابط مفيدة

- **Public Schema Admin:** http://localhost:8000/admin/
- **Tenant Admin (farm1):** http://farm1.localhost:8000/admin/
- **API Docs:** http://farm1.localhost:8000/api/docs

---

**تاريخ الإنشاء:** 2025-12-11
