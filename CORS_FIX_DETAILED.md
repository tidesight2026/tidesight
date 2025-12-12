# 🔧 حل مشكلة CORS - خطوات مفصلة

**المشكلة:** CORS policy blocking requests from Frontend

---

## ✅ ما تم عمله:

1. ✅ تم تغيير ترتيب middleware - CORS قبل TenantMiddleware
2. ✅ تم إضافة CORS_ALLOW_ALL_ORIGINS = DEBUG
3. ✅ تم إضافة CORS_ALLOW_METHODS و CORS_ALLOW_HEADERS
4. ✅ تم إعادة تشغيل Backend

---

## 🔍 المشكلة المحتملة:

`django-tenants` يتطلب domain محدد (مثل `farm1.localhost:8000`) وليس `localhost:8000` مباشرة.

---

## 🚀 الحلول الممكنة:

### الحل 1: استخدام Domain محدد (موصى به)

استخدام `farm1.localhost:8000` بدلاً من `localhost:8000`

**في Frontend (`frontend/src/utils/constants.ts`):**
```typescript
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://farm1.localhost:8000'
```

**إضافة إلى `/etc/hosts` (أو `C:\Windows\System32\drivers\etc\hosts`):**
```
127.0.0.1 farm1.localhost
```

### الحل 2: إضافة Public Schema

يمكن إضافة schema عام للـ API بدون tenant.

---

## 📋 الخطوة التالية:

1. تحقق من أن Tenant موجود
2. استخدم domain محدد للـ API
3. أو أضف public schema للـ API

---

**الحالة:** 🔧 يحتاج إلى مزيد من التعديل

