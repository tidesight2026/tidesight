# حالة نشر AquaERP على Docker Desktop

## ✅ الحالة الحالية

تم نشر التطبيق على Docker Desktop بنجاح!

## 🔧 الخدمات المتاحة

### 1. Backend API
- **URL:** http://localhost:8000
- **API Docs:** http://localhost:8000/api/docs
- **Health Check:** http://localhost:8000/api/dashboard/health

### 2. Database (PostgreSQL)
- **Host:** localhost
- **Port:** 5432
- **Database:** aqua_erp_db
- **User:** aqua_admin
- **Password:** secure_pass_123

### 3. Redis
- **Host:** localhost
- **Port:** 6379

## 📋 الأوامر المفيدة

### عرض حالة الحاويات
```bash
docker-compose ps
```

### عرض السجلات
```bash
docker-compose logs -f web
docker-compose logs -f celery
docker-compose logs -f celery-beat
```

### إيقاف التطبيق
```bash
docker-compose down
```

### إيقاف وحذف البيانات
```bash
docker-compose down -v
```

### إعادة بناء وتشغيل
```bash
docker-compose up -d --build
```

### تنفيذ أوامر Django
```bash
docker-compose exec web python manage.py <command>
```

### إنشاء مستخدم فائق
```bash
docker-compose exec web python manage.py createsuperuser
```

## 🐛 استكشاف الأخطاء

### إذا فشل الاتصال بقاعدة البيانات
```bash
docker-compose logs db
```

### إذا فشل تشغيل Web Server
```bash
docker-compose logs web
```

### إعادة تشغيل خدمة معينة
```bash
docker-compose restart web
docker-compose restart celery
```

## 📝 ملاحظات

- البيانات محفوظة في Docker volumes (postgres_data, redis_data)
- الملفات الثابتة في `/app/staticfiles` داخل الحاوية
- ملفات Media في `/app/media` داخل الحاوية
- السجلات في `/app/logs` داخل الحاوية

## 🎯 الخطوات التالية

1. ✅ الحاويات تعمل
2. ⏳ تشغيل الترحيلات (Migrations)
3. ⏳ إنشاء مستخدم فائق (اختياري)
4. ⏳ الوصول للتطبيق عبر المتصفح
