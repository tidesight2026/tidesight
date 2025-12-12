# 🚀 نشر TideSight على الخادم - الآن

## ✅ تم Push الكود إلى GitHub بنجاح!

الكود موجود الآن على: `https://github.com/tidesight2026/tidesight`

---

## 🖥️ الخطوات التالية: النشر على الخادم

### الخطوة 1: الاتصال بالخادم

```bash
ssh root@72.60.187.58
```

### الخطوة 2: تثبيت Git و Docker

```bash
# تحديث النظام
apt-get update

# تثبيت Git
apt-get install -y git

# تثبيت Docker
apt-get install -y docker.io docker-compose

# تشغيل Docker
systemctl start docker
systemctl enable docker
```

### الخطوة 3: Clone Repository

```bash
# إنشاء مجلد المشروع
mkdir -p /opt/tidesight
cd /opt/tidesight

# Clone Repository
git clone https://github.com/tidesight2026/tidesight.git .

# التحقق
ls -la
```

### الخطوة 4: إنشاء ملف .env.prod

```bash
cd /opt/tidesight

# إنشاء SECRET_KEY بدون Django
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
```

### الخطوة 5: بناء وتشغيل التطبيق

```bash
cd /opt/tidesight

# بناء الصور
docker-compose -f docker-compose.prod.yml build

# تشغيل الخدمات
docker-compose -f docker-compose.prod.yml up -d

# الانتظار قليلاً
sleep 10
```

### الخطوة 6: Migrations

```bash
# Shared Schema
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate_schemas --shared

# Tenant Schemas
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate_schemas --tenant

# Static Files
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

### الخطوة 7: إعداد SSL

```bash
# تثبيت Certbot
apt-get install -y certbot python3-certbot-nginx

# الحصول على SSL Certificate
certbot --nginx -d tidesight.cloud -d www.tidesight.cloud --non-interactive --agree-tos --email admin@tidesight.cloud
```

### الخطوة 8: إنشاء Superuser

```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

أدخل:
- Username: `admin`
- Email: `admin@tidesight.cloud`
- Password: `[كلمة مرور قوية]`

---

## ✅ التحقق من النشر

```bash
# حالة الخدمات
docker-compose -f docker-compose.prod.yml ps

# Logs
docker-compose -f docker-compose.prod.yml logs -f
```

---

## 🌐 الوصول

بعد النشر، افتح:
- `https://tidesight.cloud`
- `https://tidesight.cloud/admin/`

---

## 🔄 تحديث الكود لاحقاً

```bash
cd /opt/tidesight
git pull origin main
./update.sh
```

---

**جاهز للنشر! 🎉**
