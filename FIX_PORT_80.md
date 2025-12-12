# 🔧 حل مشكلة Port 80 مستخدم

## ⚠️ المشكلة

```
ERROR: failed to bind host port for 0.0.0.0:80: address already in use
```

**السبب:** منفذ 80 مستخدم من قبل خدمة أخرى (Apache أو Nginx مثبت على النظام).

---

## ✅ الحل: إيقاف الخدمة أو تغيير المنفذ

### الطريقة 1: إيقاف Apache/Nginx المثبت على النظام (موصى به)

```bash
# التحقق من الخدمة التي تستخدم المنفذ 80
sudo netstat -tulpn | grep :80
# أو
sudo lsof -i :80

# إيقاف Apache
sudo systemctl stop apache2
sudo systemctl disable apache2

# أو إيقاف Nginx
sudo systemctl stop nginx
sudo systemctl disable nginx
```

### الطريقة 2: تغيير منفذ Nginx في docker-compose (بديل)

إذا كنت تريد الاحتفاظ بـ Apache/Nginx على النظام:

```bash
# تعديل docker-compose.prod.yml
# تغيير منفذ 80 إلى 8080 مثلاً
```

---

## 🚀 الحل السريع (الطريقة 1 - موصى به)

```bash
# التحقق من الخدمة
sudo systemctl status apache2
sudo systemctl status nginx

# إيقاف Apache
sudo systemctl stop apache2
sudo systemctl disable apache2

# أو إيقاف Nginx
sudo systemctl stop nginx
sudo systemctl disable nginx

# ثم إعادة تشغيل Docker Compose
cd /opt/tidesight
docker-compose -f docker-compose.prod.yml up -d
```

---

## ✅ التحقق

```bash
# التحقق من المنفذ
sudo netstat -tulpn | grep :80

# التحقق من الحاويات
docker-compose -f docker-compose.prod.yml ps
```

---

**ملاحظة:** بعد إيقاف Apache/Nginx، يمكن استخدام Nginx داخل Docker للتعامل مع SSL والـ reverse proxy.

---

**جاهز! 🎉**
