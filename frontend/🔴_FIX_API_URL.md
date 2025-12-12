# 🔴 تحديث API URL - مهم جداً!

**المشكلة:** Backend لا يجد الـ API endpoint

---

## 🔍 المشكلة:

`django-tenants` يتطلب **domain محدد** مثل `farm1.localhost:8000` وليس `localhost:8000` مباشرة.

---

## ✅ الحل:

### الخطوة 1: إضافة Domain إلى hosts file

**في Windows:**

1. افتح Notepad كـ Administrator
2. افتح الملف: `C:\Windows\System32\drivers\etc\hosts`
3. أضف هذا السطر في النهاية:
   ```
   127.0.0.1    farm1.localhost
   ```
4. احفظ الملف

### الخطوة 2: تحديث Frontend

في `frontend/src/utils/constants.ts`، غيّر:

```typescript
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://farm1.localhost:8000'
```

### الخطوة 3: إعادة تشغيل Frontend

```bash
# أوقف Frontend (Ctrl+C)
# ثم شغله مرة أخرى
npm run dev
```

---

## 📋 التحقق:

بعد التغييرات، يجب أن يعمل:
- ✅ `http://farm1.localhost:8000/api/auth/login`
- ❌ `http://localhost:8000/api/auth/login` (لن يعمل)

---

**الحالة:** 🔴 يحتاج إلى تحديث

