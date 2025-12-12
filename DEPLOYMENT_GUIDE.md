# دليل النشر - TideSight على Ubuntu 24.04

## 📋 معلومات الخادم

- **اسم التطبيق:** TideSight
- **الدومين:** tidesight.cloud
- **نظام التشغيل:** Ubuntu 24.04
- **الاستضافة:** Hostinger
- **Hostname:** srv1029413.hstgr.cloud
- **SSH User:** root
- **IPv4:** 72.60.187.58

---

## 🚀 خطوات النشر

### 1. الاتصال بالخادم

```bash
ssh root@72.60.187.58
# أو
ssh root@srv1029413.hstgr.cloud
```

### 2. تشغيل Script النشر

```bash
# نسخ الملفات إلى الخادم
scp -r . root@72.60.187.58:/opt/tidesight/

# الاتصال بالخادم
ssh root@72.60.187.58

# الانتقال إلى مجلد المشروع
cd /opt/tidesight

# جعل script النشر قابل للتنفيذ
chmod +x deploy.sh

# تشغيل script النشر
./deploy.sh
```

### 3. إعداد DNS

تأكد من إعداد DNS records للدومين:

```
A Record: tidesight.cloud -> 72.60.187.58
A Record: www.tidesight.cloud -> 72.60.187.58
CNAME Record: *.tidesight.cloud -> tidesight.cloud
```

### 4. إنشاء Superuser

```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

### 5. إنشاء Tenant الأول

1. افتح: `https://tidesight.cloud/admin/`
2. سجّل دخول باستخدام Superuser
3. اذهب إلى: **Client Management > Clients**
4. أنشئ Client جديد
5. أضف Domain: `client1.tidesight.cloud`

---

## 🔧 إعدادات مهمة

### ملف .env.prod

يتم إنشاؤه تلقائياً بواسطة `deploy.sh`، أو يمكنك إنشاؤه يدوياً:

```env
# Django Settings
SECRET_KEY=<generate-strong-secret-key>
DEBUG=False
ALLOWED_HOSTS=tidesight.cloud,www.tidesight.cloud,*.tidesight.cloud

# Database
POSTGRES_DB=tidesight_db
POSTGRES_USER=tidesight_admin
POSTGRES_PASSWORD=<strong-password>

# Redis
REDIS_PASSWORD=<strong-password>
CELERY_BROKER_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
CELERY_RESULT_BACKEND=redis://:${REDIS_PASSWORD}@redis:6379/0

# Environment
ENVIRONMENT=production
```

### تحديث Frontend API URL

في `frontend/.env.prod`:

```env
VITE_API_BASE_URL=https://tidesight.cloud
```

---

## 📝 أوامر مفيدة

### عرض Logs

```bash
# جميع الخدمات
docker-compose -f docker-compose.prod.yml logs -f

# خدمة معينة
docker-compose -f docker-compose.prod.yml logs -f web
docker-compose -f docker-compose.prod.yml logs -f nginx
```

### إعادة تشغيل الخدمات

```bash
docker-compose -f docker-compose.prod.yml restart
```

### تحديث الكود

```bash
# سحب التحديثات
git pull

# إعادة بناء الصور
docker-compose -f docker-compose.prod.yml build

# إعادة تشغيل الخدمات
docker-compose -f docker-compose.prod.yml up -d
```

### تشغيل Migrations

```bash
# Shared Schema
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate_schemas --shared

# Tenant Schemas
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate_schemas --tenant
```

### جمع Static Files

```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

---

## 🔒 الأمان

### Firewall

```bash
# فتح المنافذ المطلوبة
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### SSL Certificate

يتم تثبيت SSL تلقائياً بواسطة Certbot. للتجديد:

```bash
certbot renew --dry-run
```

---

## 🐛 حل المشاكل

### مشكلة: لا يمكن الوصول إلى الموقع

1. تحقق من أن Docker يعمل:
   ```bash
   docker ps
   ```

2. تحقق من Logs:
   ```bash
   docker-compose -f docker-compose.prod.yml logs
   ```

3. تحقق من DNS:
   ```bash
   nslookup tidesight.cloud
   ```

### مشكلة: SSL Certificate

```bash
# إعادة تثبيت SSL
certbot --nginx -d tidesight.cloud -d www.tidesight.cloud --force-renewal
```

### مشكلة: Database Connection

```bash
# التحقق من حالة Database
docker-compose -f docker-compose.prod.yml exec db psql -U tidesight_admin -d tidesight_db -c "SELECT 1;"
```

---

## 📊 المراقبة

### Health Check

```bash
curl https://tidesight.cloud/health/
```

### Resource Usage

```bash
docker stats
```

---

## ✅ التحقق من النشر

1. ✅ الموقع يعمل: `https://tidesight.cloud`
2. ✅ SSL Certificate صالح
3. ✅ Django Admin يعمل: `https://tidesight.cloud/admin/`
4. ✅ API يعمل: `https://tidesight.cloud/api/`
5. ✅ Frontend يعمل: `https://tidesight.cloud/`

---

**تاريخ الإنشاء:** 2025-12-12
