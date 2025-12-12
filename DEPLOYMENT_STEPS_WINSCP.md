# 📋 خطوات النشر خطوة بخطوة - WinSCP

## 🎯 نظرة عامة

هذا دليل تفصيلي خطوة بخطوة لنشر TideSight باستخدام WinSCP.

---

## 📝 الخطوة 1: إعداد WinSCP

### 1.1 فتح WinSCP

1. شغّل برنامج **WinSCP**
2. إذا ظهرت نافذة Login، انقر على **New Site**

### 1.2 إعدادات الاتصال

املأ البيانات التالية:

| الحقل | القيمة |
|-------|--------|
| **File protocol** | `SFTP` |
| **Host name** | `72.60.187.58` |
| **Port number** | `22` |
| **User name** | `root` |
| **Password** | `[كلمة مرور الخادم]` |

### 1.3 حفظ الاتصال

1. انقر على **Save** (أو `Ctrl+S`)
2. أدخل اسم: `TideSight Server`
3. انقر على **OK**

### 1.4 الاتصال

1. اختر الاتصال المحفوظ من القائمة
2. انقر على **Login**
3. إذا ظهرت رسالة عن SSH key، انقر على **Yes** أو **Accept**

---

## 📁 الخطوة 2: إنشاء مجلد المشروع على الخادم

### 2.1 الانتقال إلى /opt

في نافذة الخادم (اليمين):

1. انقر على شريط العنوان
2. اكتب: `/opt`
3. اضغط `Enter`

### 2.2 إنشاء مجلد tidesight

1. انقر بالزر الأيمن في منطقة فارغة
2. **New** → **Directory**
3. أدخل الاسم: `tidesight`
4. انقر على **OK**

### 2.3 فتح المجلد

انقر نقراً مزدوجاً على مجلد `tidesight` للدخول إليه.

---

## 📤 الخطوة 3: رفع الملفات

### 3.1 التحضير

في نافذة جهازك (اليسار):

1. انتقل إلى: `d:\AquaERP`
2. تأكد من رؤية جميع الملفات

### 3.2 رفع المجلدات

**اسحب وأفلت هذه المجلدات من اليسار إلى اليمين:**

```
✅ tenants/
✅ frontend/          (بدون node_modules/)
✅ api/
✅ accounts/
✅ accounting/
✅ audit/
✅ biological/
✅ daily_operations/
✅ inventory/
✅ sales/
✅ nginx/
```

### 3.3 رفع الملفات

**اسحب وأفلت هذه الملفات:**

```
✅ docker-compose.prod.yml
✅ Dockerfile
✅ deploy.sh
✅ manage.py
✅ requirements.txt
✅ env.prod.template
```

### 3.4 انتظار الرفع

- انتظر حتى يكتمل رفع جميع الملفات
- قد يستغرق وقتاً حسب حجم الملفات
- راقب شريط التقدم في أسفل النافذة

---

## 💻 الخطوة 4: فتح Terminal

### 4.1 فتح Terminal في WinSCP

**الطريقة 1:**
1. **Commands** → **Open Terminal**

**الطريقة 2:**
- اضغط `Ctrl+P`

### 4.2 التحقق من الموقع

في Terminal، نفّذ:

```bash
pwd
```

يجب أن يظهر: `/root` أو `/home/root`

---

## 🔧 الخطوة 5: إعداد البيئة

### 5.1 الانتقال إلى مجلد المشروع

```bash
cd /opt/tidesight
ls -la
```

يجب أن ترى جميع الملفات التي رفعتها.

### 5.2 إنشاء ملف .env.prod

```bash
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

**أو لتوليد كلمات مرور عشوائية:**

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

### 5.3 التحقق من الملف

```bash
cat .env.prod
```

---

## 🐳 الخطوة 6: تثبيت Docker

### 6.1 تحديث النظام

```bash
apt-get update
```

### 6.2 تثبيت Docker

```bash
apt-get install -y docker.io docker-compose
```

### 6.3 تشغيل Docker

```bash
systemctl start docker
systemctl enable docker
```

### 6.4 التحقق

```bash
docker --version
docker-compose --version
```

---

## 🚀 الخطوة 7: تشغيل التطبيق

### 7.1 جعل Script قابل للتنفيذ

```bash
chmod +x deploy.sh
```

### 7.2 تشغيل Script النشر

```bash
./deploy.sh
```

**أو النشر اليدوي:**

```bash
# بناء الصور
docker-compose -f docker-compose.prod.yml build

# تشغيل الخدمات
docker-compose -f docker-compose.prod.yml up -d

# الانتظار قليلاً
sleep 10

# Migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate_schemas --shared
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

---

## 🔒 الخطوة 8: إعداد SSL

### 8.1 تثبيت Certbot

```bash
apt-get install -y certbot python3-certbot-nginx
```

### 8.2 الحصول على SSL Certificate

```bash
certbot --nginx -d tidesight.cloud -d www.tidesight.cloud --non-interactive --agree-tos --email admin@tidesight.cloud
```

---

## 👤 الخطوة 9: إنشاء Superuser

```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

أدخل:
- **Username:** `admin`
- **Email:** `admin@tidesight.cloud`
- **Password:** `[كلمة مرور قوية]`

---

## ✅ الخطوة 10: التحقق

### 10.1 التحقق من الخدمات

```bash
docker-compose -f docker-compose.prod.yml ps
```

### 10.2 عرض Logs

```bash
docker-compose -f docker-compose.prod.yml logs -f
```

اضغط `Ctrl+C` للخروج.

### 10.3 اختبار الموقع

افتح في المتصفح:
- ✅ `https://tidesight.cloud`
- ✅ `https://tidesight.cloud/admin/`

---

## 🎉 تم النشر بنجاح!

---

## 🔧 أوامر مفيدة

### عرض حالة الخدمات

```bash
docker-compose -f docker-compose.prod.yml ps
```

### إعادة تشغيل الخدمات

```bash
docker-compose -f docker-compose.prod.yml restart
```

### عرض Logs

```bash
docker-compose -f docker-compose.prod.yml logs -f web
```

### تحديث الكود

```bash
# في WinSCP: رفع الملفات الجديدة
# ثم في Terminal:
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

---

**تاريخ الإنشاء:** 2025-12-12
