# 🚀 دليل النشر باستخدام Git - TideSight

## 📋 المتطلبات

- **Git Repository** (GitHub, GitLab, Bitbucket, إلخ)
- **SSH Access** إلى الخادم
- **معلومات الخادم:**
  - Hostname: `srv1029413.hstgr.cloud`
  - IP: `72.60.187.58`
  - User: `root`
  - Domain: `tidesight.cloud`

---

## 🔧 الخطوة 1: إعداد Git Repository

### 1.1 إنشاء Repository

إذا لم يكن لديك repository:

1. أنشئ repository جديد على GitHub/GitLab
2. ادفع الكود إلى Repository:

```bash
# في مجلد المشروع المحلي
cd d:\AquaERP

# تهيئة Git (إذا لم يكن موجوداً)
git init

# إضافة Remote
git remote add origin https://github.com/yourusername/tidesight.git
# أو
git remote add origin git@github.com:yourusername/tidesight.git

# إضافة جميع الملفات
git add .

# Commit
git commit -m "Initial commit - TideSight"

# Push إلى Repository
git push -u origin main
```

### 1.2 إنشاء .gitignore

تأكد من وجود `.gitignore`:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
.venv/
env/
.env
.env.local
.env.prod

# Django
*.log
db.sqlite3
db.sqlite3-journal
/staticfiles/
/media/

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnp
.pnp.js

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Docker
.dockerignore

# Secrets
*.pem
*.key
secrets/
```

---

## 🖥️ الخطوة 2: الاتصال بالخادم

### 2.1 الاتصال عبر SSH

```bash
ssh root@72.60.187.58
# أو
ssh root@srv1029413.hstgr.cloud
```

### 2.2 تثبيت Git على الخادم

```bash
# تحديث النظام
apt-get update

# تثبيت Git
apt-get install -y git

# التحقق من التثبيت
git --version
```

---

## 📥 الخطوة 3: Clone Repository

### 3.1 إنشاء مجلد المشروع

```bash
mkdir -p /opt/tidesight
cd /opt/tidesight
```

### 3.2 Clone Repository

**الطريقة 1: HTTPS (أسهل)**

```bash
git clone https://github.com/yourusername/tidesight.git .
```

**الطريقة 2: SSH (أكثر أماناً)**

```bash
# أولاً: إضافة SSH Key إلى الخادم (إذا لم يكن موجوداً)
# انسخ محتوى ~/.ssh/id_rsa.pub من جهازك المحلي
# ثم أضفه إلى GitHub/GitLab SSH Keys

git clone git@github.com:yourusername/tidesight.git .
```

---

## 🔐 الخطوة 4: إعداد ملف .env.prod

### 4.1 إنشاء ملف .env.prod

```bash
cd /opt/tidesight

# إنشاء ملف .env.prod
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

### 4.2 التأكد من أن .env.prod في .gitignore

```bash
# التحقق من أن .env.prod غير موجود في Git
git check-ignore .env.prod
```

---

## 🐳 الخطوة 5: تثبيت Docker

```bash
# تثبيت Docker
apt-get install -y docker.io docker-compose

# تشغيل Docker
systemctl start docker
systemctl enable docker

# التحقق
docker --version
docker-compose --version
```

---

## 🚀 الخطوة 6: النشر الأولي

### 6.1 بناء الصور

```bash
cd /opt/tidesight
docker-compose -f docker-compose.prod.yml build
```

### 6.2 تشغيل الخدمات

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 6.3 Migrations

```bash
# Shared Schema
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate_schemas --shared

# Tenant Schemas
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate_schemas --tenant

# Static Files
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

---

## 🔒 الخطوة 7: إعداد SSL

```bash
# تثبيت Certbot
apt-get install -y certbot python3-certbot-nginx

# الحصول على SSL Certificate
certbot --nginx -d tidesight.cloud -d www.tidesight.cloud --non-interactive --agree-tos --email admin@tidesight.cloud
```

---

## 👤 الخطوة 8: إنشاء Superuser

```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

---

## 🔄 الخطوة 9: تحديث الكود (للمستقبل)

### 9.1 سحب التحديثات

```bash
cd /opt/tidesight
git pull origin main
```

### 9.2 إعادة بناء وتشغيل

```bash
# إعادة بناء الصور
docker-compose -f docker-compose.prod.yml build

# إعادة تشغيل الخدمات
docker-compose -f docker-compose.prod.yml up -d

# Migrations (إذا كانت هناك تغييرات)
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate_schemas --shared
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate_schemas --tenant

# جمع Static Files (إذا كانت هناك تغييرات)
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

---

## 🤖 الخطوة 10: أتمتة النشر (اختياري)

### 10.1 إنشاء Script تحديث تلقائي

```bash
cat > /opt/tidesight/update.sh << 'EOF'
#!/bin/bash
set -e

cd /opt/tidesight

echo "🔄 سحب التحديثات من Git..."
git pull origin main

echo "🔨 إعادة بناء الصور..."
docker-compose -f docker-compose.prod.yml build

echo "🚀 إعادة تشغيل الخدمات..."
docker-compose -f docker-compose.prod.yml up -d

echo "📊 تشغيل Migrations..."
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate_schemas --shared
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate_schemas --tenant

echo "📦 جمع Static Files..."
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

echo "✅ تم التحديث بنجاح!"
EOF

chmod +x /opt/tidesight/update.sh
```

### 10.2 استخدام Script التحديث

```bash
/opt/tidesight/update.sh
```

---

## 🔐 الخطوة 11: إعداد SSH Keys (لـ Git SSH)

### 11.1 إنشاء SSH Key على الخادم

```bash
# إنشاء SSH Key
ssh-keygen -t ed25519 -C "tidesight-server" -f ~/.ssh/id_ed25519 -N ""

# عرض المفتاح العام
cat ~/.ssh/id_ed25519.pub
```

### 11.2 إضافة SSH Key إلى GitHub/GitLab

1. انسخ محتوى `~/.ssh/id_ed25519.pub`
2. اذهب إلى GitHub/GitLab → Settings → SSH Keys
3. أضف المفتاح الجديد

### 11.3 اختبار الاتصال

```bash
ssh -T git@github.com
# أو
ssh -T git@gitlab.com
```

---

## 📝 ملخص الأوامر السريعة

### النشر الأولي

```bash
# 1. Clone Repository
cd /opt
git clone https://github.com/yourusername/tidesight.git tidesight
cd tidesight

# 2. إنشاء .env.prod
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

# 3. تثبيت Docker
apt-get update
apt-get install -y docker.io docker-compose
systemctl start docker
systemctl enable docker

# 4. بناء وتشغيل
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# 5. Migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate_schemas --shared
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# 6. SSL
apt-get install -y certbot python3-certbot-nginx
certbot --nginx -d tidesight.cloud -d www.tidesight.cloud --non-interactive --agree-tos --email admin@tidesight.cloud

# 7. Superuser
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

### تحديث الكود

```bash
cd /opt/tidesight
git pull origin main
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate_schemas --shared
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

---

## 🔧 نصائح مهمة

### 1. Branch Strategy

```bash
# استخدام branch منفصل للإنتاج
git checkout -b production
git push origin production

# على الخادم
git clone -b production https://github.com/yourusername/tidesight.git .
```

### 2. Git Hooks (اختياري)

```bash
# إنشاء post-receive hook للتحديث التلقائي
cat > /opt/tidesight/.git/hooks/post-receive << 'EOF'
#!/bin/bash
cd /opt/tidesight
git pull origin main
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
EOF

chmod +x /opt/tidesight/.git/hooks/post-receive
```

### 3. Backup قبل التحديث

```bash
# نسخ احتياطي للقاعدة البيانات
docker-compose -f docker-compose.prod.yml exec db pg_dump -U tidesight_admin tidesight_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

---

## ✅ التحقق من النشر

```bash
# حالة الخدمات
docker-compose -f docker-compose.prod.yml ps

# Logs
docker-compose -f docker-compose.prod.yml logs -f

# اختبار الموقع
curl https://tidesight.cloud
```

---

**جاهز للنشر! 🎉**
