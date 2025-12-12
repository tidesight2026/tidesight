# 🚀 TideSight - دليل النشر الكامل

## 📋 معلومات المشروع

- **اسم التطبيق:** TideSight
- **الدومين:** tidesight.cloud
- **الخادم:** srv1029413.hstgr.cloud
- **IP:** 72.60.187.58
- **نظام التشغيل:** Ubuntu 24.04
- **SSH User:** root

---

## ✅ ما تم إنجازه

1. ✅ تحديث `docker-compose.prod.yml` للدومين الجديد
2. ✅ إنشاء `nginx/conf.d/tidesight.conf` مع إعدادات SSL
3. ✅ تحديث `frontend/Dockerfile` لدعم build args
4. ✅ تحديث `ALLOWED_HOSTS` في settings.py
5. ✅ تحديث `API_BASE_URL` في Frontend
6. ✅ إنشاء `deploy.sh` script للنشر التلقائي
7. ✅ إنشاء دليل النشر الكامل

---

## 🚀 خطوات النشر

### الطريقة 1: استخدام Script النشر (موصى به)

```bash
# 1. نسخ الملفات إلى الخادم
scp -r . root@72.60.187.58:/opt/tidesight/

# 2. الاتصال بالخادم
ssh root@72.60.187.58

# 3. الانتقال إلى مجلد المشروع
cd /opt/tidesight

# 4. جعل script قابل للتنفيذ
chmod +x deploy.sh

# 5. تشغيل script النشر
./deploy.sh
```

### الطريقة 2: النشر اليدوي

راجع `DEPLOYMENT_GUIDE.md` للخطوات التفصيلية.

---

## 📝 إعدادات مهمة

### 1. DNS Records

يجب إعداد DNS records التالية:

```
A Record:     tidesight.cloud        -> 72.60.187.58
A Record:     www.tidesight.cloud    -> 72.60.187.58
CNAME Record: *.tidesight.cloud      -> tidesight.cloud
```

### 2. ملف .env.prod

سيتم إنشاؤه تلقائياً بواسطة `deploy.sh`، أو يمكنك إنشاؤه يدوياً:

```env
SECRET_KEY=<strong-secret-key>
DEBUG=False
ALLOWED_HOSTS=tidesight.cloud,www.tidesight.cloud,*.tidesight.cloud
POSTGRES_DB=tidesight_db
POSTGRES_USER=tidesight_admin
POSTGRES_PASSWORD=<strong-password>
REDIS_PASSWORD=<strong-password>
CELERY_BROKER_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
CELERY_RESULT_BACKEND=redis://:${REDIS_PASSWORD}@redis:6379/0
ENVIRONMENT=production
```

### 3. Frontend API URL

في `frontend/.env.prod`:

```env
VITE_API_BASE_URL=https://tidesight.cloud
```

---

## 🔧 الأوامر المفيدة

### عرض Logs

```bash
docker-compose -f docker-compose.prod.yml logs -f
```

### إعادة تشغيل الخدمات

```bash
docker-compose -f docker-compose.prod.yml restart
```

### تحديث الكود

```bash
git pull
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

### Migrations

```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate_schemas --shared
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate_schemas --tenant
```

---

## ✅ التحقق من النشر

بعد النشر، تحقق من:

1. ✅ `https://tidesight.cloud` - Frontend يعمل
2. ✅ `https://tidesight.cloud/api/` - API يعمل
3. ✅ `https://tidesight.cloud/admin/` - Django Admin يعمل
4. ✅ SSL Certificate صالح (Let's Encrypt)

---

## 📚 الملفات المرجعية

- `DEPLOYMENT_GUIDE.md` - دليل النشر التفصيلي
- `QUICK_DEPLOY.md` - دليل النشر السريع
- `TIDESIGHT_SETUP.md` - ملخص التغييرات

---

**جاهز للنشر! 🎉**
