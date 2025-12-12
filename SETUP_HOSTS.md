# إعداد hosts للوصول إلى Tenant

## المشكلة
Windows لا يعرف `farm1.localhost` كاسم نطاق صالح.

## الحل

### الطريقة 1: إضافة إلى ملف hosts (موصى به)

1. افتح Notepad **كمسؤول (Run as Administrator)**
2. افتح الملف: `C:\Windows\System32\drivers\etc\hosts`
3. أضف السطر التالي في نهاية الملف:
```
127.0.0.1    farm1.localhost
```
4. احفظ الملف

### الطريقة 2: استخدام localhost مباشرة

يمكنك الوصول للتطبيق عبر:
- http://localhost:8000 (لكن قد لا يعمل مع Multi-tenant بشكل صحيح)

### الطريقة 3: استخدام IP مباشرة

- http://127.0.0.1:8000

## بعد إضافة hosts

افتح المتصفح وانتقل إلى:
- **Admin Panel:** http://farm1.localhost:8000/admin/
- **API Docs:** http://farm1.localhost:8000/api/docs

## معلومات تسجيل الدخول

- **Username:** SmartFarm
- **Email:** admin@farm1.com
- **Password:** (تم إنشاؤه تلقائياً - استخدم الأمر أدناه لإنشاء كلمة مرور جديدة)

## إنشاء كلمة مرور جديدة

```bash
docker-compose exec web python manage.py create_tenant_superuser --schema_name farm1 --username SmartFarm --email admin@farm1.com --password YourNewPassword
```
