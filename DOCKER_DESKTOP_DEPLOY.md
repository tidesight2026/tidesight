# دليل نشر AquaERP على Docker Desktop

## المتطلبات
- Docker Desktop مثبت ويعمل
- Windows 10/11 أو macOS

## خطوات النشر

### 1. التحقق من ملف .env
تأكد من وجود ملف `.env` في المجلد الرئيسي. إذا لم يكن موجوداً، انسخ `env.example` إلى `.env`:
```bash
copy env.example .env
```

### 2. بناء وتشغيل الحاويات
```bash
docker-compose up --build -d
```

### 3. تشغيل الترحيلات (Migrations)
```bash
docker-compose exec web python manage.py migrate_schemas --shared
```

### 4. إنشاء مستخدم فائق (Superuser) - اختياري
```bash
docker-compose exec web python manage.py createsuperuser
```

### 5. التحقق من الحالة
```bash
docker-compose ps
```

## الوصول للتطبيق

- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/api/docs
- **Database:** localhost:5432
- **Redis:** localhost:6379

## أوامر مفيدة

### عرض السجلات (Logs)
```bash
docker-compose logs -f web
```

### إيقاف التطبيق
```bash
docker-compose down
```

### إيقاف وحذف البيانات
```bash
docker-compose down -v
```

### إعادة بناء الحاويات
```bash
docker-compose up --build -d
```

### تنفيذ أوامر Django
```bash
docker-compose exec web python manage.py <command>
```

## استكشاف الأخطاء

### إذا فشل الاتصال بقاعدة البيانات
```bash
docker-compose logs db
```

### إذا فشل تشغيل Web Server
```bash
docker-compose logs web
```

### التحقق من حالة الحاويات
```bash
docker-compose ps
```

## ملاحظات

- البيانات محفوظة في Docker volumes (postgres_data, redis_data)
- الملفات الثابتة في `/app/staticfiles`
- ملفات Media في `/app/media`
