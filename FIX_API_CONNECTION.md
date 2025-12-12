# 🔧 حل مشكلة ERR_CONNECTION_REFUSED

## ⚠️ المشكلة

```
ERR_CONNECTION_REFUSED
Failed to load resource: /api/auth/login
```

**السبب:** Frontend مبني بـ `VITE_API_BASE_URL=https://tidesight.cloud` لكن:
1. الوصول عبر `http://tidesight.doud` (HTTP وليس HTTPS)
2. النطاق مختلف (`tidesight.doud` vs `tidesight.cloud`)

---

## ✅ الحل: إعادة بناء Frontend

### 1. Commit و Push التغييرات:

```bash
git add .
git commit -m "Fix API URL to use tidesight.doud and dynamic protocol"
git push origin main
```

### 2. على الخادم - إعادة بناء Frontend:

```bash
cd /opt/tidesight

# Pull التغييرات
git pull origin main

# إعادة بناء Frontend فقط
docker-compose -f docker-compose.prod.yml build frontend

# إعادة تشغيل Frontend
docker-compose -f docker-compose.prod.yml up -d frontend

# التحقق
docker-compose -f docker-compose.prod.yml ps
```

---

## 🔄 الحل البديل (أسرع):

إذا كنت تريد حل سريع بدون إعادة بناء:

### تعديل Frontend لاستخدام النطاق الحالي تلقائياً:

تم تحديث `constants.ts` لاستخدام النطاق الحالي تلقائياً:
```typescript
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 
  (typeof window !== 'undefined' ? `${window.location.protocol}//${window.location.host}` : 'http://tidesight.doud')
```

هذا يعني أن Frontend سيستخدم نفس النطاق والبروتوكول تلقائياً.

---

## ✅ بعد الإصلاح:

- ✅ Frontend سيستخدم `http://tidesight.doud/api` تلقائياً
- ✅ لا حاجة لإعادة بناء إذا استخدمت الحل البديل
- ✅ يعمل مع أي نطاق (tidesight.doud أو tidesight.cloud)

---

**جاهز! 🎉**
