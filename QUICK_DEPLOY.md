# 🚀 نشر سريع - TideSight

## معلومات الخادم

- **Server:** srv1029413.hstgr.cloud (72.60.187.58)
- **User:** root
- **Domain:** tidesight.cloud
- **OS:** Ubuntu 24.04

---

## خطوات سريعة

### 1. الاتصال بالخادم

```bash
ssh root@72.60.187.58
```

### 2. تثبيت المتطلبات

```bash
apt-get update
apt-get install -y docker.io docker-compose git
```

### 3. نسخ المشروع

```bash
cd /opt
git clone <your-repo-url> tidesight
cd tidesight
```

### 4. إنشاء .env.prod

```bash
cat > .env.prod << EOF
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DEBUG=False
ALLOWED_HOSTS=tidesight.cloud,www.tidesight.cloud,*.tidesight.cloud
POSTGRES_DB=tidesight_db
POSTGRES_USER=tidesight_admin
POSTGRES_PASSWORD=$(openssl rand -base64 32)
REDIS_PASSWORD=$(openssl rand -base64 32)
CELERY_BROKER_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
CELERY_RESULT_BACKEND=redis://:${REDIS_PASSWORD}@redis:6379/0
ENVIRONMENT=production
EOF
```

### 5. تشغيل التطبيق

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

### 6. Migrations

```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate_schemas --shared
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

### 7. SSL Certificate

```bash
certbot --nginx -d tidesight.cloud -d www.tidesight.cloud --non-interactive --agree-tos --email admin@tidesight.cloud
```

---

## ✅ جاهز!

افتح: `https://tidesight.cloud`
