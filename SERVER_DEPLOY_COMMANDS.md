# 📋 أوامر النشر على الخادم - TideSight

## 🚀 الأوامر الكاملة (انسخ والصق)

```bash
# 1. الاتصال بالخادم
ssh root@72.60.187.58

# 2. تثبيت المتطلبات
apt-get update
apt-get install -y git docker.io docker-compose
systemctl start docker
systemctl enable docker

# 3. Clone Repository
mkdir -p /opt/tidesight
cd /opt/tidesight
git clone https://github.com/tidesight2026/tidesight.git .

# 4. إنشاء .env.prod
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')
POSTGRES_PASS=$(openssl rand -base64 32)
REDIS_PASS=$(openssl rand -base64 32)
cat > .env.prod << EOF
SECRET_KEY=${SECRET_KEY}
DEBUG=False
ALLOWED_HOSTS=tidesight.cloud,www.tidesight.cloud,*.tidesight.cloud
POSTGRES_DB=tidesight_db
POSTGRES_USER=tidesight_admin
POSTGRES_PASSWORD=${POSTGRES_PASS}
REDIS_PASSWORD=${REDIS_PASS}
CELERY_BROKER_URL=redis://:${REDIS_PASS}@redis:6379/0
CELERY_RESULT_BACKEND=redis://:${REDIS_PASS}@redis:6379/0
ENVIRONMENT=production
EOF

# 5. بناء وتشغيل
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
sleep 10

# 6. Migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate_schemas --shared
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate_schemas --tenant
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# 7. SSL
apt-get install -y certbot python3-certbot-nginx
certbot --nginx -d tidesight.cloud -d www.tidesight.cloud --non-interactive --agree-tos --email admin@tidesight.cloud

# 8. Superuser
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

---

## ✅ بعد النشر

افتح: `https://tidesight.cloud`

---

**جاهز! 🎉**
