# 🧪 اختبار API بعد الإصلاحات

**التاريخ:** ديسمبر 2025

---

## ✅ التعديلات المطبقة

1. ✅ تحديث `ALLOWED_HOSTS` لتشمل `farm1.localhost` و `*.localhost`
2. ✅ إضافة `PUBLIC_SCHEMA_URLCONF` في settings
3. ✅ URL routing يعمل داخل tenant context (تم التحقق)

---

## 🧪 الاختبار المطلوب

### الخطوة 1: تأكد من ملف Hosts

**Windows:** `C:\Windows\System32\drivers\etc\hosts`

أضف:
```
127.0.0.1    farm1.localhost
```

**ملاحظة:** قد تحتاج إلى فتح Notepad كـ Administrator.

### الخطوة 2: اختبار API

#### 1. Swagger UI:
```
http://farm1.localhost:8000/api/docs
```

**النتيجة المتوقعة:**
- ✅ يجب أن ترى Swagger UI
- ❌ إذا رأيت 404: تحقق من ملف hosts

#### 2. Login Endpoint:
```
POST http://farm1.localhost:8000/api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "Admin123!"
}
```

**النتيجة المتوقعة:**
- ✅ يجب أن تحصل على access_token و refresh_token
- ❌ إذا رأيت 404: المشكلة ما زالت موجودة

---

## 🔍 إذا استمرت المشكلة

إذا ما زالت تعطي 404:

1. **تحقق من السجلات:**
   ```powershell
   docker-compose logs web --tail 20
   ```

2. **تحقق من tenant:**
   ```powershell
   docker-compose exec web python manage.py shell -c "from tenants.models import Domain; print(Domain.objects.all())"
   ```

3. **تحقق من Host header:**
   - تأكد أن المتصفح يرسل `Host: farm1.localhost:8000`
   - جرب Postman مع Header: `Host: farm1.localhost:8000`

---

**أخبرني بالنتيجة!** 🚀

