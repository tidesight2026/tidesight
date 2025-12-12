# 🚀 دليل البدء السريع - AquaERP على Docker Desktop

## ✅ التطبيق جاهز ويعمل!

### 📍 الوصول للتطبيق

**⚠️ مهم:** يجب إضافة `farm1.localhost` إلى ملف hosts أولاً!

#### خطوة 1: إعداد hosts (مطلوب)

1. افتح Notepad **كمسؤول (Run as Administrator)**
2. افتح الملف: `C:\Windows\System32\drivers\etc\hosts`
3. أضف السطر التالي:
```
127.0.0.1    farm1.localhost
```
4. احفظ الملف

#### خطوة 2: الوصول للتطبيق

بعد إضافة hosts، افتح المتصفح وانتقل إلى:

- **Admin Panel:** http://farm1.localhost:8000/admin/
- **API Documentation:** http://farm1.localhost:8000/api/docs
- **Root API:** http://farm1.localhost:8000/

## 👤 معلومات تسجيل الدخول

### Tenant: Farm 1
- **Domain:** farm1.localhost
- **Username:** SmartFarm
- **Email:** admin@farm1.com
- **Password:** (تم إنشاؤه تلقائياً)

### إنشاء كلمة مرور جديدة

إذا أردت تحديد كلمة مرور محددة:

```bash
docker-compose exec web python manage.py create_tenant_superuser --schema_name farm1 --username SmartFarm --email admin@farm1.com --password YourPasswordHere
```

## 🔧 الأوامر المفيدة

### عرض حالة الحاويات
```bash
docker-compose ps
```

### عرض السجلات
```bash
docker-compose logs -f web
```

### إيقاف التطبيق
```bash
docker-compose down
```

### إعادة تشغيل
```bash
docker-compose restart web
```

## 📊 الخدمات المتاحة

- ✅ **Backend API:** http://farm1.localhost:8000
- ✅ **Database:** localhost:5432
- ✅ **Redis:** localhost:6379
- ✅ **Celery Worker:** Running
- ✅ **Celery Beat:** Running

## 🎯 الخطوات التالية

1. ✅ إضافة farm1.localhost إلى hosts
2. ✅ الوصول إلى http://farm1.localhost:8000/admin/
3. ✅ تسجيل الدخول باستخدام SmartFarm
4. ✅ استكشاف التطبيق!

**🎊 التطبيق جاهز للاستخدام!**
