# 🔧 حل مشكلة Docker Compose Environment Variables

## ⚠️ المشكلة

```
WARNING: The CELERY_BROKER_URL variable is not set. Defaulting to a blank string.
ERROR: Container is unhealthy
```

**السبب:** `docker-compose` يقرأ `.env` تلقائياً للمتغيرات `${VAR}`، لكننا نستخدم `.env.prod`.

---

## ✅ الحل: استخدام --env-file

### الطريقة 1: استخدام --env-file (موصى به)

```bash
cd /opt/tidesight

# استخدام --env-file
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

### الطريقة 2: نسخ .env.prod إلى .env

```bash
cd /opt/tidesight

# نسخ .env.prod إلى .env
cp .env.prod .env

# ثم تشغيل docker-compose عادي
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🚀 الحل السريع (الطريقة 2 - موصى به)

```bash
cd /opt/tidesight
cp .env.prod .env
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

---

## ✅ التحقق

```bash
# التحقق من الحاويات
docker-compose -f docker-compose.prod.yml ps

# التحقق من Logs
docker-compose -f docker-compose.prod.yml logs web
docker-compose -f docker-compose.prod.yml logs db
docker-compose -f docker-compose.prod.yml logs redis
```

---

**ملاحظة:** `.env` موجود في `.gitignore` ولن يتم رفعه إلى Git.

---

**جاهز! 🎉**
