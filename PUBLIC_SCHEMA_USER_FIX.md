# إصلاح مشكلة User في Public Schema

## المشكلة

عند محاولة تسجيل الدخول في public schema (`localhost:8000/admin/`)، يظهر الخطأ:
```
relation "accounts_user" does not exist
```

## السبب

- `AUTH_USER_MODEL = 'accounts.User'` في settings
- `accounts` كان موجود فقط في `TENANT_APPS`
- Django Admin في public schema يحاول استخدام `accounts.User` الذي غير موجود

## الحل المطبق

تم إضافة `accounts` إلى `SHARED_APPS` أيضاً:

```python
SHARED_APPS = (
    ...
    'accounts',  # تطبيق المستخدمين - موجود في public schema أيضاً
    ...
)
```

## الخطوات التالية

1. **تشغيل migrations للـ public schema:**
   ```bash
   docker-compose exec web python manage.py migrate_schemas --shared
   ```

2. **إنشاء مستخدم admin في public schema:**
   ```bash
   docker-compose exec web python create_public_admin.py
   ```

   أو يدوياً:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

3. **الوصول إلى Admin:**
   - Public Schema: http://localhost:8000/admin/
   - Tenant Schema: http://farm1.localhost:8000/admin/

## ملاحظات

- **Public Schema:** يستخدم `accounts.User` أيضاً (نفس النموذج)
- **Tenant Schemas:** تستخدم `accounts.User` (معزول لكل tenant)
- **الفرق:** البيانات معزولة - كل schema له جدول `accounts_user` منفصل

---

**تاريخ الإنشاء:** 2025-12-11
