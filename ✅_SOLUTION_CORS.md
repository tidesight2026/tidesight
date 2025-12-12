# ✅ حل مشكلة CORS - الحل النهائي

**المشكلة:** CORS policy + API endpoint not found

---

## 🔍 المشكلة الحقيقية:

1. **CORS Policy:** Backend لا يسمح بالطلبات من Frontend
2. **API Not Found:** `django-tenants` يتطلب domain محدد (`farm1.localhost`) وليس `localhost` مباشرة

---

## ✅ الحل الكامل:

### الخطوة 1: إضافة Domain إلى hosts file

**في Windows:**

1. افتح **Notepad** كـ **Administrator** (مهم!)
2. افتح الملف: `C:\Windows\System32\drivers\etc\hosts`
3. أضف هذا السطر في النهاية:
   ```
   127.0.0.1    farm1.localhost
   ```
4. احفظ الملف

### الخطوة 2: تحديث Frontend

✅ **تم تحديث `frontend/src/utils/constants.ts`** ليستخدم `http://farm1.localhost:8000`

### الخطوة 3: تحديث CORS Settings

✅ **تم تحديث `tenants/aqua_core/settings.py`** لإضافة `farm1.localhost:5175`

### الخطوة 4: إعادة تشغيل الخدمات

```bash
# إعادة تشغيل Backend
docker-compose restart web

# إعادة تشغيل Frontend (في terminal منفصل)
# Ctrl+C لإيقافه
# ثم: npm run dev
```

---

## 📋 التحقق:

بعد كل التغييرات:
1. ✅ `http://farm1.localhost:8000/api/auth/login` - يجب أن يعمل
2. ✅ `http://localhost:5175` - Frontend
3. ✅ تسجيل الدخول يجب أن يعمل

---

## 🚀 البيانات:

```
👤 Username: admin
🔑 Password: Admin123!
```

---

**الحالة:** ✅ تم إصلاح جميع الإعدادات - جاهز للاختبار!

