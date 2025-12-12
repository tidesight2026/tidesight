# 🚀 TideSight - النشر باستخدام Git

## 📋 نظرة عامة

هذا الدليل يشرح كيفية نشر TideSight على الخادم باستخدام Git.

---

## ⚡ الخطوات السريعة

### 1. إعداد Git Repository

```bash
# على جهازك المحلي
cd d:\AquaERP
git init
git remote add origin https://github.com/yourusername/tidesight.git
git add .
git commit -m "Initial commit - TideSight"
git push -u origin main
```

### 2. على الخادم - Clone

```bash
ssh root@72.60.187.58
cd /opt
git clone https://github.com/yourusername/tidesight.git tidesight
cd tidesight
```

### 3. إعداد البيئة

```bash
# إنشاء .env.prod
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

### 4. تثبيت Docker

```bash
apt-get update
apt-get install -y docker.io docker-compose
systemctl start docker
systemctl enable docker
```

### 5. تشغيل التطبيق

```bash
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate_schemas --shared
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

### 6. SSL

```bash
apt-get install -y certbot python3-certbot-nginx
certbot --nginx -d tidesight.cloud -d www.tidesight.cloud --non-interactive --agree-tos --email admin@tidesight.cloud
```

---

## 🔄 تحديث الكود

### الطريقة 1: يدوياً

```bash
cd /opt/tidesight
git pull origin main
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate_schemas --shared
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

### الطريقة 2: استخدام Script

```bash
cd /opt/tidesight
chmod +x update.sh
./update.sh
```

---

## 📚 الملفات المرجعية

- **`DEPLOY_WITH_GIT.md`** - دليل شامل ومفصل
- **`GIT_DEPLOY_QUICK.md`** - دليل سريع
- **`GIT_SETUP_GUIDE.md`** - إعداد Git محلياً
- **`GIT_COMMANDS.md`** - أوامر Git المفيدة
- **`update.sh`** - Script التحديث التلقائي

---

## ✅ المزايا

- ✅ **سهولة التحديث:** `git pull` فقط
- ✅ **تتبع التغييرات:** جميع التعديلات مسجلة
- ✅ **Rollback:** يمكن العودة لأي نسخة سابقة
- ✅ **Collaboration:** يمكن للفريق العمل معاً
- ✅ **Backup:** الكود محفوظ في Repository

---

**جاهز للنشر! 🎉**
