# 🚀 دليل النشر باستخدام WinSCP - TideSight

## 📋 المتطلبات

- **WinSCP** مثبت على Windows
- **PuTTY** (للاتصال بالخادم عبر SSH)
- **معلومات الخادم:**
  - Hostname: `srv1029413.hstgr.cloud`
  - IP: `72.60.187.58`
  - User: `root`
  - Domain: `tidesight.cloud`

---

## 🔧 الخطوة 1: إعداد الاتصال في WinSCP

### 1.1 فتح WinSCP

1. شغّل برنامج **WinSCP**
2. انقر على **New Site** (موقع جديد)

### 1.2 إعدادات الاتصال

املأ البيانات التالية:

```
File protocol: SFTP
Host name: 72.60.187.58
Port number: 22
User name: root
Password: [كلمة مرور الخادم]
```

**أو يمكنك استخدام:**
```
Host name: srv1029413.hstgr.cloud
```

### 1.3 حفظ الاتصال

1. انقر على **Save** لحفظ الإعدادات
2. أدخل اسم للاتصال (مثل: `TideSight Server`)
3. انقر على **OK**

### 1.4 الاتصال

1. اختر الاتصال المحفوظ
2. انقر على **Login**
3. إذا ظهرت رسالة عن SSH key، انقر على **Yes**

---

## 📁 الخطوة 2: إنشاء مجلد المشروع

### 2.1 الاتصال بالخادم

بعد الاتصال بنجاح، ستظهر نافذتان:
- **اليسار:** جهازك المحلي
- **اليمين:** الخادم

### 2.2 إنشاء مجلد المشروع

في نافذة الخادم (اليمين):

1. انتقل إلى `/opt`
2. انقر بالزر الأيمن → **New** → **Directory**
3. أدخل الاسم: `tidesight`
4. انقر على **OK**

---

## 📤 الخطوة 3: نسخ الملفات

### 3.1 تحضير الملفات المحلية

في نافذة جهازك (اليسار):

1. انتقل إلى مجلد المشروع `d:\AquaERP`
2. تأكد من وجود جميع الملفات

### 3.2 استثناء الملفات غير الضرورية

**ملفات يجب استثناؤها (لا تنسخها):**

- `.git/` (إذا كان موجوداً)
- `node_modules/` (في `frontend/`)
- `__pycache__/`
- `*.pyc`
- `.env` (سيتم إنشاؤه على الخادم)
- `venv/` أو `.venv/`
- `.idea/` (إذا كنت تستخدم PyCharm)
- `.vscode/`

### 3.3 نسخ الملفات

**الطريقة 1: نسخ كامل (موصى به للمرة الأولى)**

1. في نافذة جهازك (اليسار)، حدد جميع الملفات والمجلدات
2. اسحب وأفلت إلى نافذة الخادم (اليمين) في `/opt/tidesight`
3. انتظر حتى يكتمل النسخ (قد يستغرق وقتاً)

**الطريقة 2: نسخ مجلدات محددة**

انسخ هذه المجلدات والملفات:

```
✅ tenants/
✅ frontend/
✅ api/
✅ accounts/
✅ accounting/
✅ audit/
✅ biological/
✅ daily_operations/
✅ inventory/
✅ sales/
✅ nginx/
✅ docker-compose.prod.yml
✅ Dockerfile
✅ deploy.sh
✅ manage.py
✅ requirements.txt
✅ env.prod.template
```

---

## 🔐 الخطوة 4: إعداد ملف .env.prod

### 4.1 فتح Terminal في WinSCP

1. في WinSCP، انقر على **Commands** → **Open Terminal**
2. أو استخدم **PuTTY** للاتصال بالخادم

### 4.2 إنشاء ملف .env.prod

في Terminal، نفّذ:

```bash
cd /opt/tidesight
cat > .env.prod << 'EOF'
SECRET_KEY=your-super-secret-key-minimum-50-characters-long-change-this-in-production
DEBUG=False
ALLOWED_HOSTS=tidesight.cloud,www.tidesight.cloud,*.tidesight.cloud
POSTGRES_DB=tidesight_db
POSTGRES_USER=tidesight_admin
POSTGRES_PASSWORD=your-strong-database-password-here
REDIS_PASSWORD=your-strong-redis-password-here
CELERY_BROKER_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
CELERY_RESULT_BACKEND=redis://:${REDIS_PASSWORD}@redis:6379/0
ENVIRONMENT=production
EOF
```

**أو استخدم هذا الأمر لتوليد كلمات مرور عشوائية:**

```bash
cd /opt/tidesight
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

---

## 🐳 الخطوة 5: تثبيت Docker و Docker Compose

### 5.1 فتح Terminal

في WinSCP: **Commands** → **Open Terminal**

### 5.2 تثبيت المتطلبات

```bash
# تحديث النظام
apt-get update

# تثبيت Docker
apt-get install -y docker.io

# تثبيت Docker Compose
apt-get install -y docker-compose

# تشغيل Docker
systemctl start docker
systemctl enable docker

# التحقق من التثبيت
docker --version
docker-compose --version
```

---

## 🚀 الخطوة 6: تشغيل التطبيق

### 6.1 الانتقال إلى مجلد المشروع

```bash
cd /opt/tidesight
```

### 6.2 جعل Script النشر قابل للتنفيذ

```bash
chmod +x deploy.sh
```

### 6.3 تشغيل Script النشر

```bash
./deploy.sh
```

**أو النشر اليدوي:**

```bash
# بناء الصور
docker-compose -f docker-compose.prod.yml build

# تشغيل الخدمات
docker-compose -f docker-compose.prod.yml up -d

# Migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate_schemas --shared
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

---

## 🔒 الخطوة 7: إعداد SSL Certificate

### 7.1 تثبيت Certbot

```bash
apt-get install -y certbot python3-certbot-nginx
```

### 7.2 الحصول على SSL Certificate

```bash
certbot --nginx -d tidesight.cloud -d www.tidesight.cloud --non-interactive --agree-tos --email admin@tidesight.cloud
```

---

## 👤 الخطوة 8: إنشاء Superuser

```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

أدخل:
- Username: `admin`
- Email: `admin@tidesight.cloud`
- Password: `[كلمة مرور قوية]`

---

## ✅ الخطوة 9: التحقق من النشر

### 9.1 التحقق من الخدمات

```bash
docker-compose -f docker-compose.prod.yml ps
```

يجب أن ترى جميع الخدمات تعمل:
- web
- frontend
- nginx
- db
- redis
- celery
- celery-beat

### 9.2 التحقق من Logs

```bash
docker-compose -f docker-compose.prod.yml logs -f
```

### 9.3 اختبار الموقع

افتح في المتصفح:
- `https://tidesight.cloud`
- `https://tidesight.cloud/admin/`

---

## 🔧 نصائح WinSCP

### عرض الملفات المخفية

1. **Options** → **Preferences**
2. **Panels** → **Show hidden files**

### تحرير الملفات مباشرة

1. انقر بالزر الأيمن على الملف
2. **Edit** (سيستخدم Notepad++ أو محرر نصي)
3. احفظ التغييرات

### رفع مجلدات كبيرة

- استخدم **Compression** في إعدادات الاتصال
- **Options** → **Preferences** → **Transfer** → **Enable transfer resume**

---

## 🐛 حل المشاكل

### مشكلة: لا يمكن الاتصال

1. تحقق من IP: `72.60.187.58`
2. تحقق من Port: `22`
3. تحقق من Username: `root`
4. تحقق من Firewall على الخادم

### مشكلة: الملفات لا ترفع

1. تحقق من الصلاحيات: `chmod 755 /opt/tidesight`
2. تحقق من المساحة: `df -h`

### مشكلة: Docker لا يعمل

```bash
systemctl status docker
systemctl restart docker
```

---

## 📝 ملخص الخطوات السريعة

1. ✅ **WinSCP:** الاتصال بالخادم
2. ✅ **نسخ الملفات:** إلى `/opt/tidesight`
3. ✅ **Terminal:** إنشاء `.env.prod`
4. ✅ **تثبيت Docker:** `apt-get install docker.io docker-compose`
5. ✅ **تشغيل:** `docker-compose -f docker-compose.prod.yml up -d --build`
6. ✅ **Migrations:** `docker-compose exec web python manage.py migrate_schemas --shared`
7. ✅ **SSL:** `certbot --nginx -d tidesight.cloud -d www.tidesight.cloud`
8. ✅ **Superuser:** `docker-compose exec web python manage.py createsuperuser`

---

**جاهز للنشر! 🎉**
