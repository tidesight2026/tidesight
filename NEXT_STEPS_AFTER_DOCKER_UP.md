# ✅ الخطوات التالية بعد تشغيل Docker

## 🎉 تم تشغيل جميع الحاويات بنجاح!

---

## 📋 الخطوات التالية

### 1. التحقق من حالة الحاويات

```bash
cd /opt/tidesight
docker-compose -f docker-compose.prod.yml ps
```

يجب أن ترى جميع الحاويات في حالة `Up` أو `healthy`.

---

### 2. تشغيل Migrations

```bash
# Shared Schema (للبيانات المشتركة)
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate_schemas --shared

# Tenant Schemas (لبيانات العملاء)
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate_schemas --tenant

# جمع Static Files
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

---

### 3. إنشاء Superuser

```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

أدخل:
- Username: `admin`
- Email: `admin@tidesight.cloud`
- Password: `[كلمة مرور قوية]`

---

### 4. إعداد SSL (Let's Encrypt)

```bash
# تثبيت Certbot
apt-get install -y certbot python3-certbot-nginx

# الحصول على SSL Certificate
certbot --nginx -d tidesight.cloud -d www.tidesight.cloud --non-interactive --agree-tos --email admin@tidesight.cloud
```

**ملاحظة:** تأكد من أن DNS records (A و CNAME) موجهة بشكل صحيح قبل تشغيل Certbot.

---

### 5. التحقق من Logs

```bash
# Logs لجميع الخدمات
docker-compose -f docker-compose.prod.yml logs -f

# أو Logs لخدمة محددة
docker-compose -f docker-compose.prod.yml logs web
docker-compose -f docker-compose.prod.yml logs nginx
```

---

## 🌐 الوصول للتطبيق

بعد إكمال الخطوات:

- **Frontend:** `http://tidesight.cloud` أو `https://tidesight.cloud` (بعد SSL)
- **Admin:** `http://tidesight.cloud/admin/` أو `https://tidesight.cloud/admin/`

---

## ✅ التحقق من النشر

```bash
# حالة الحاويات
docker-compose -f docker-compose.prod.yml ps

# اختبار الاتصال
curl http://localhost
curl http://tidesight.cloud
```

---

**جاهز! 🎉**
