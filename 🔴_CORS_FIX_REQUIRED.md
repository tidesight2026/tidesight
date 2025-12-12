# 🔴 حل مشكلة CORS - مهم جداً!

**المشكلة:** Backend لا يجد الـ API endpoint (`/api/auth/login`)

---

## 🔍 المشكلة الحقيقية:

في السجلات يظهر:
```
WARNING Not Found: /api/auth/login
WARNING "OPTIONS /api/auth/login HTTP/1.1" 404
```

**السبب:** `django-tenants` يتطلب **domain محدد** للوصول إلى tenant!

---

## ✅ الحل:

### الحل 1: استخدام Domain محدد (موصى به)

**الخطوة 1:** إضافة Domain إلى hosts file

في Windows، افتح الملف:
```
C:\Windows\System32\drivers\etc\hosts
```

أضف هذا السطر:
```
127.0.0.1    farm1.localhost
```

**الخطوة 2:** تحديث Frontend

في `frontend/src/utils/constants.ts`، غيّر:
```typescript
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://farm1.localhost:8000'
```

**الخطوة 3:** تحديث CORS settings

في `tenants/aqua_core/settings.py`، أضف:
```python
CORS_ALLOWED_ORIGINS = [
    # ... القائمة الحالية ...
    "http://farm1.localhost:8000",  # جديد
]
```

---

### الحل 2: إضافة Public Schema (أكثر تعقيداً)

يمكن إضافة schema عام للـ API بدون tenant، لكن هذا يتطلب تعديلات أكثر.

---

## 🚀 الخطوات السريعة:

1. ✅ إضافة `127.0.0.1 farm1.localhost` إلى hosts file
2. ✅ تحديث `frontend/src/utils/constants.ts`
3. ✅ إعادة تشغيل Frontend
4. ✅ جرب تسجيل الدخول

---

## 📋 التحقق:

بعد التغييرات، يجب أن يعمل:
- `http://farm1.localhost:8000/api/auth/login` ✅
- بدلاً من `http://localhost:8000/api/auth/login` ❌

---

**الحالة:** 🔴 يحتاج إلى تعديل hosts file و Frontend

