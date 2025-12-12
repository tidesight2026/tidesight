# 🔧 حل مشكلة Restarting Containers

## ⚠️ المشكلة

```
State: Restarting
Error: Container is restarting, wait until the container is running
```

**السبب:** الحاويات تفشل في التشغيل بسبب خطأ ما (خطأ في الكود، قاعدة البيانات، إلخ).

---

## ✅ الحل: فحص Logs

### 1. فحص Logs للحاويات

```bash
cd /opt/tidesight

# Logs لـ web
docker-compose -f docker-compose.prod.yml logs web

# Logs لـ nginx
docker-compose -f docker-compose.prod.yml logs nginx

# Logs لـ celery
docker-compose -f docker-compose.prod.yml logs celery

# Logs لـ celery-beat
docker-compose -f docker-compose.prod.yml logs celery-beat

# Logs لجميع الخدمات
docker-compose -f docker-compose.prod.yml logs --tail=100
```

### 2. التحقق من الأخطاء الشائعة

- **خطأ في الاتصال بقاعدة البيانات:** تحقق من `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- **خطأ في الاتصال بـ Redis:** تحقق من `REDIS_PASSWORD`
- **خطأ في الكود:** تحقق من syntax errors أو missing dependencies
- **خطأ في Nginx config:** تحقق من ملفات nginx configuration

---

## 🚀 الخطوات السريعة

```bash
cd /opt/tidesight

# 1. فحص Logs
docker-compose -f docker-compose.prod.yml logs web --tail=50

# 2. التحقق من .env
cat .env | grep -E "POSTGRES|REDIS|SECRET"

# 3. إيقاف وإعادة التشغيل
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d

# 4. مراقبة Logs
docker-compose -f docker-compose.prod.yml logs -f
```

---

## ✅ بعد إصلاح المشكلة

```bash
# التحقق من الحالة
docker-compose -f docker-compose.prod.yml ps

# يجب أن تكون جميع الحاويات في حالة "Up" أو "healthy"
```

---

**ملاحظة:** أرسل الـ logs ليتمكن من تحديد المشكلة بدقة.

---

**جاهز! 🎉**
