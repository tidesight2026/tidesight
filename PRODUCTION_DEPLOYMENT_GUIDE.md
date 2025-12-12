# 🚀 دليل النشر للإنتاج - AquaERP

**الحالة:** جاهز للاستخدام  
**التاريخ:** ديسمبر 2024

---

## 📋 نظرة عامة

هذا الدليل يوضح خطوات نشر AquaERP في بيئة إنتاجية آمنة وقابلة للتوسع.

---

## ✅ المتطلبات الأساسية

1. **خادم VPS** (Ubuntu 22.04 LTS أو أحدث)
   - الحد الأدنى: 4GB RAM, 2 vCPUs, 50GB Storage
   - الموصى به: 8GB RAM, 4 vCPUs, 100GB Storage

2. **نطاق (Domain)** مع إمكانية إعداد DNS
   - مثال: `aquaerp.com`
   - يجب دعم Wildcard Subdomains (`*.aquaerp.com`)

3. **معرفة أساسية بـ:**
   - Docker & Docker Compose
   - Linux Command Line
   - DNS Configuration

---

## 🔧 الخطوة 1: إعداد الخادم

### 1.1 تثبيت Docker و Docker Compose

```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# إضافة المستخدم الحالي إلى مجموعة docker
sudo usermod -aG docker $USER

# تثبيت Docker Compose
sudo apt install docker-compose-plugin -y

# إعادة تسجيل الدخول أو تنفيذ:
newgrp docker

# التحقق من التثبيت
docker --version
docker compose version
```

### 1.2 تثبيت Git

```bash
sudo apt install git -y
```

---

## 📥 الخطوة 2: سحب الكود

```bash
# الانتقال إلى مجلد مناسب
cd /opt

# سحب المشروع (استبدل بالرابط الصحيح)
git clone https://github.com/your-org/AquaERP.git
cd AquaERP
```

---

## 🔐 الخطوة 3: إعداد متغيرات البيئة

### 3.1 إنشاء ملف `.env.prod`

```bash
# نسخ الملف النموذجي
cp env.prod.example .env.prod

# تعديل الملف بالقيم الصحيحة
nano .env.prod
```

### 3.2 توليد SECRET_KEY

```bash
# داخل حاوية Python أو محلياً
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**⚠️ مهم:** 
- استبدل جميع القيم التي تبدأ بـ `CHANGE_THIS`
- استخدم كلمات مرور قوية (32+ حرف)
- لا ترفع ملف `.env.prod` على GitHub

---

## 🌐 الخطوة 4: إعداد DNS

### 4.1 إعداد DNS Records

في لوحة تحكم مزود النطاق، أضف:

```
Type    Name    Value           TTL
A       @       YOUR_SERVER_IP  3600
A       *       YOUR_SERVER_IP  3600
```

هذا يسمح بـ:
- `aquaerp.com` → الخادم
- `*.aquaerp.com` → الخادم (للمستأجرين)

### 4.2 التحقق من DNS

```bash
# التحقق من النطاق الرئيسي
dig aquaerp.com

# التحقق من Wildcard
dig farm1.aquaerp.com
```

---

## 🔒 الخطوة 5: إعداد SSL (Let's Encrypt)

### 5.1 تثبيت Certbot

```bash
sudo apt install certbot -y
```

### 5.2 الحصول على شهادة Wildcard

```bash
# استخدام DNS Challenge (مطلوب لـ Wildcard)
certbot certonly --manual --preferred-challenges dns \
  -d aquaerp.com -d *.aquaerp.com \
  --email your-email@example.com \
  --agree-tos --no-eff-email
```

**ملاحظة:** Certbot سيعطيك سجل TXT لإضافته في DNS. بعد إضافته، اضغط Enter.

### 5.3 نسخ الشهادات إلى مجلد المشروع

```bash
# إنشاء مجلد SSL
mkdir -p nginx/ssl

# نسخ الشهادات (استبدل بالمسار الصحيح)
sudo cp /etc/letsencrypt/live/aquaerp.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/aquaerp.com/privkey.pem nginx/ssl/
sudo chown $USER:$USER nginx/ssl/*.pem
```

**أو** تعديل `nginx/conf.d/aquaerp.conf` لاستخدام المسار الافتراضي:
```nginx
ssl_certificate /etc/letsencrypt/live/aquaerp.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/aquaerp.com/privkey.pem;
```

---

## 🐳 الخطوة 6: بناء وتشغيل الحاويات

### 6.1 بناء الصور

```bash
# بناء جميع الصور
docker compose -f docker-compose.prod.yml build
```

### 6.2 تشغيل الحاويات

```bash
# تشغيل في الخلفية
docker compose -f docker-compose.prod.yml up -d
```

### 6.3 التحقق من الحالة

```bash
# عرض الحاويات
docker compose -f docker-compose.prod.yml ps

# عرض السجلات
docker compose -f docker-compose.prod.yml logs -f
```

---

## 🗄️ الخطوة 7: إعداد قاعدة البيانات

### 7.1 تشغيل الترحيلات

```bash
# الدخول إلى حاوية Backend
docker compose -f docker-compose.prod.yml exec web bash

# داخل الحاوية
python manage.py migrate_schemas --shared
python manage.py migrate_schemas
```

### 7.2 إنشاء المستخدم الافتراضي

```bash
# إنشاء Superuser
python manage.py createsuperuser
```

### 7.3 إنشاء Public Tenant

```bash
python manage.py create_public_tenant --domain aquaerp.com --schema_name public
```

---

## 📧 الخطوة 8: إعداد البريد الإلكتروني

### 8.1 اختيار مزود البريد

**خيارات موصى بها:**
- **SendGrid** (سهل الإعداد)
- **AWS SES** (اقتصادي)
- **Mailgun** (موثوق)

### 8.2 تحديث `.env.prod`

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=YOUR_SENDGRID_API_KEY
DEFAULT_FROM_EMAIL=noreply@aquaerp.com
```

### 8.3 إعادة تشغيل الحاويات

```bash
docker compose -f docker-compose.prod.yml restart web
```

---

## ✅ الخطوة 9: التحقق من النشر

### 9.1 اختبارات أساسية

1. **الوصول إلى الموقع:**
   ```
   https://aquaerp.com
   ```

2. **إنشاء مستأجر جديد:**
   ```
   https://farm1.aquaerp.com
   ```

3. **تسجيل الدخول:**
   - استخدام بيانات Superuser

4. **إنشاء فاتورة تجريبية:**
   - التحقق من ZATCA Integration (في وضع Sandbox أولاً)

### 9.2 التحقق من السجلات

```bash
# سجلات Backend
docker compose -f docker-compose.prod.yml logs web

# سجلات Nginx
docker compose -f docker-compose.prod.yml logs nginx

# سجلات Celery
docker compose -f docker-compose.prod.yml logs celery
```

---

## 🔄 الخطوة 10: إعداد النسخ الاحتياطي

### 10.1 جعل سكربت النسخ الاحتياطي قابلاً للتنفيذ

```bash
chmod +x scripts/backup.sh
```

### 10.2 إضافة إلى Cron (يومياً في 2 صباحاً)

```bash
crontab -e

# إضافة السطر التالي:
0 2 * * * /opt/AquaERP/scripts/backup.sh >> /var/log/aquaerp_backup.log 2>&1
```

### 10.3 (اختياري) رفع النسخ الاحتياطية إلى S3

تعديل `scripts/backup.sh` وإضافة:

```bash
# تثبيت AWS CLI
sudo apt install awscli -y

# إضافة في نهاية السكربت
aws s3 sync "$BACKUP_DIR" s3://your-bucket/aquaerp-backups/ --delete
```

---

## 🔍 الخطوة 11: المراقبة (اختياري)

### 11.1 إعداد Sentry

1. إنشاء حساب على [Sentry.io](https://sentry.io)
2. إضافة DSN إلى `.env.prod`:
   ```env
   SENTRY_DSN=https://your-dsn@sentry.io/project-id
   SENTRY_ENVIRONMENT=production
   ```
3. تثبيت `sentry-sdk` في `requirements.txt`
4. إضافة التكوين في `settings.py`

---

## 🛠️ الصيانة

### إعادة تشغيل الخدمات

```bash
# إعادة تشغيل جميع الخدمات
docker compose -f docker-compose.prod.yml restart

# إعادة تشغيل خدمة محددة
docker compose -f docker-compose.prod.yml restart web
```

### تحديث التطبيق

```bash
# سحب التحديثات
git pull

# إعادة بناء الصور
docker compose -f docker-compose.prod.yml build

# إعادة تشغيل
docker compose -f docker-compose.prod.yml up -d

# تشغيل الترحيلات
docker compose -f docker-compose.prod.yml exec web python manage.py migrate_schemas
```

### عرض الاستخدام

```bash
# استخدام الموارد
docker stats

# استخدام القرص
df -h
```

---

## 🚨 استكشاف الأخطاء

### المشكلة: الحاويات لا تبدأ

```bash
# التحقق من السجلات
docker compose -f docker-compose.prod.yml logs

# التحقق من حالة الحاويات
docker compose -f docker-compose.prod.yml ps -a
```

### المشكلة: قاعدة البيانات غير متاحة

```bash
# التحقق من صحة الحاوية
docker compose -f docker-compose.prod.yml exec db pg_isready -U aqua_admin
```

### المشكلة: SSL لا يعمل

```bash
# التحقق من الشهادات
sudo certbot certificates

# تجديد الشهادات
sudo certbot renew
```

---

## 📚 موارد إضافية

- [Docker Documentation](https://docs.docker.com/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)

---

## ✅ قائمة التحقق النهائية

- [ ] الخادم جاهز ومحدث
- [ ] Docker و Docker Compose مثبتان
- [ ] الكود مسحوب من Git
- [ ] ملف `.env.prod` معد بشكل صحيح
- [ ] DNS معد بشكل صحيح
- [ ] شهادات SSL مثبتة
- [ ] الحاويات تعمل
- [ ] قاعدة البيانات مهاجرة
- [ ] Superuser منشأ
- [ ] Public Tenant منشأ
- [ ] البريد الإلكتروني معد
- [ ] النسخ الاحتياطي مجدول
- [ ] الموقع يعمل على HTTPS
- [ ] يمكن إنشاء مستأجرين جدد
- [ ] الاختبارات الأساسية نجحت

---

**🎉 تهانينا! AquaERP جاهز للإنتاج!**

