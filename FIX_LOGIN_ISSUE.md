# 🔧 حل مشكلة تسجيل الدخول - AquaERP

**المشكلة:** فشل تسجيل الدخول مع رسالة خطأ

---

## ✅ ما تم التحقق منه

1. ✅ **المستخدم موجود في قاعدة البيانات**
   - Username: `admin`
   - Email: `admin@example.com`
   - Password: `Admin123!`
   - Is Active: `True`

2. ✅ **المصادقة تعمل بشكل صحيح**
   - تم التحقق من أن المصادقة تعمل

---

## 🔍 المشكلة المحتملة

### المشكلة 1: Frontend لا يتصل بالـ Backend

**السبب:**
- Frontend يرسل الطلبات إلى `http://localhost:8000/api/auth/login`
- لكن Backend قد لا يكون على نفس العنوان
- أو هناك مشكلة في Tenant routing

### المشكلة 2: Tenant Domain

**السبب:**
- الـ API يحتاج للـ Tenant Domain للوصول إلى Schema الصحيح
- `farm1.localhost` قد لا يكون مضافاً إلى hosts

---

## 🔧 الحلول

### الحل 1: التحقق من Backend

```powershell
# تحقق من أن Backend يعمل
docker-compose ps

# تحقق من السجلات
docker-compose logs web --tail 50
```

### الحل 2: إضافة Domain إلى hosts

**Windows:**
1. افتح Notepad **كمسؤول**
2. افتح: `C:\Windows\System32\drivers\etc\hosts`
3. أضف: `127.0.0.1    farm1.localhost`
4. احفظ الملف

### الحل 3: استخدام Backend مباشرة

جرب تسجيل الدخول مباشرة من API:

```bash
curl -X POST http://farm1.localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "Admin123!"}'
```

---

## 📋 البيانات الصحيحة

```
Username: admin
Email: admin@example.com
Password: Admin123!
```

**استخدم Username (`admin`) وليس Email للتسجيل!**

---

## 🚀 خطوات التحقق

### 1. تحقق من Backend

```powershell
docker-compose ps
```

يجب أن ترى جميع الخدمات تعمل.

### 2. تحقق من Frontend

افتح Console (`F12`) وابحث عن:
- أخطاء في Network tab
- أخطاء في Console

### 3. جرب API مباشرة

افتح: `http://farm1.localhost:8000/api/docs`

جرب Endpoint `/auth/login` من Swagger UI

---

## 💡 ملاحظات مهمة

1. **استخدم Username وليس Email:**
   - Username: `admin`
   - Password: `Admin123!`

2. **أضف Domain إلى hosts:**
   - `127.0.0.1    farm1.localhost`

3. **تحقق من Console:**
   - افتح `F12`
   - ابحث عن أخطاء

---

**حاول مرة أخرى باستخدام Username: `admin` وكلمة المرور: `Admin123!`**

