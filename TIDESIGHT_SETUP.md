# TideSight - إعداد التطبيق للنشر

## 📋 معلومات المشروع

- **اسم التطبيق:** TideSight
- **الدومين:** tidesight.cloud
- **الخادم:** srv1029413.hstgr.cloud (72.60.187.58)
- **نظام التشغيل:** Ubuntu 24.04
- **SSH User:** root

---

## 🔧 التغييرات المطلوبة

### 1. تحديث ALLOWED_HOSTS

في `tenants/aqua_core/settings.py`:

```python
ALLOWED_HOSTS = [
    'tidesight.cloud',
    'www.tidesight.cloud',
    '*.tidesight.cloud',
    'localhost',  # للتطوير المحلي
]
```

### 2. تحديث Frontend API URL

في `frontend/src/utils/constants.ts`:

```typescript
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://tidesight.cloud'
```

### 3. تحديث Nginx Configuration

تم إنشاء `nginx/conf.d/tidesight.conf` مع إعدادات الدومين الجديد.

### 4. تحديث Docker Compose

تم تحديث `docker-compose.prod.yml` مع:
- Network name: `tidesight_network`
- Frontend build args للـ API URL

---

## 📝 ملفات تم إنشاؤها

1. ✅ `deploy.sh` - Script النشر التلقائي
2. ✅ `docker-compose.prod.yml` - إعدادات Docker للإنتاج
3. ✅ `nginx/conf.d/tidesight.conf` - إعدادات Nginx
4. ✅ `DEPLOYMENT_GUIDE.md` - دليل النشر الكامل
5. ✅ `QUICK_DEPLOY.md` - دليل النشر السريع

---

## 🚀 الخطوات التالية

1. **مراجعة الإعدادات:**
   - تحقق من `ALLOWED_HOSTS`
   - تحقق من `API_BASE_URL` في Frontend
   - تحقق من إعدادات Database و Redis

2. **إعداد DNS:**
   - A Record: `tidesight.cloud -> 72.60.187.58`
   - A Record: `www.tidesight.cloud -> 72.60.187.58`
   - CNAME: `*.tidesight.cloud -> tidesight.cloud`

3. **النشر:**
   - اتبع `DEPLOYMENT_GUIDE.md` أو `QUICK_DEPLOY.md`

---

**ملاحظة:** قد تحتاج إلى تحديث بعض الملفات الأخرى التي تحتوي على "AquaERP" إلى "TideSight" حسب الحاجة.
