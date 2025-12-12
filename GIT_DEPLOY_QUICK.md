# ⚡ نشر سريع باستخدام Git - TideSight

## 🚀 خطوات سريعة

### 1. على الخادم - Clone Repository

```bash
ssh root@72.60.187.58
cd /opt
git clone https://github.com/yourusername/tidesight.git tidesight
cd tidesight
```

### 2. إنشاء .env.prod

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

### 3. تثبيت Docker

```bash
apt-get update
apt-get install -y docker.io docker-compose
systemctl start docker
systemctl enable docker
```

### 4. تشغيل التطبيق

```bash
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate_schemas --shared
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

### 5. SSL

```bash
apt-get install -y certbot python3-certbot-nginx
certbot --nginx -d tidesight.cloud -d www.tidesight.cloud --non-interactive --agree-tos --email admin@tidesight.cloud
```

---

## 🔄 تحديث الكود لاحقاً

```bash
cd /opt/tidesight
git pull origin main
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

---

**جاهز! 🎉**
