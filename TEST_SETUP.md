# 🧪 دليل اختبار الإعدادات - AquaERP

هذا الدليل يوضح كيفية اختبار أن جميع الإعدادات تعمل بشكل صحيح.

---

## 📋 الخطوات السريعة

### 1. إنشاء ملف .env

```bash
# الطريقة 1: استخدام السكريبت المساعد
python setup_env.py

# الطريقة 2: النسخ اليدوي
copy env.example .env
# ثم عدّل SECRET_KEY يدوياً
```

### 2. بناء وتشغيل Docker Containers

```bash
# بناء الصور
docker-compose build

# تشغيل الخدمات في الخلفية
docker-compose up -d

# عرض حالة الخدمات
docker-compose ps
```

### 3. التحقق من حالة الخدمات

```bash
# عرض سجلات جميع الخدمات
docker-compose logs

# عرض سجلات خدمة معينة
docker-compose logs web
docker-compose logs db
docker-compose logs redis
```

---

## ✅ اختبارات التحقق

### اختبار 1: الاتصال بقاعدة البيانات

```bash
docker-compose exec web python manage.py dbshell
```

في shell قاعدة البيانات:
```sql
\dt  -- عرض الجداول
\l   -- عرض قواعد البيانات
\q   -- الخروج
```

### اختبار 2: Redis

```bash
# اختبار الاتصال بـ Redis
docker-compose exec redis redis-cli ping
# يجب أن يعيد: PONG

# اختبار Redis من Python
docker-compose exec web python -c "import redis; r = redis.Redis(host='redis', port=6379); print(r.ping())"
```

### اختبار 3: Django

```bash
# التحقق من إعدادات Django
docker-compose exec web python manage.py check

# عرض الإعدادات
docker-compose exec web python manage.py diffsettings
```

### اختبار 4: Migrations

```bash
# عرض Migrations المعلقة
docker-compose exec web python manage.py showmigrations --settings=tenants.aqua_core.settings

# إجراء Migrations للـ Public Schema
docker-compose exec web python manage.py migrate_schemas --shared

# إجراء Migrations لجميع Tenants
docker-compose exec web python manage.py migrate_schemas
```

---

## 🆕 اختبار إنشاء Tenant

### 1. إنشاء Tenant جديد

```bash
docker-compose exec web python manage.py create_tenant \
  --name "مزرعة تجريبية" \
  --domain "farm1" \
  --email "test@example.com" \
  --admin-username "admin" \
  --admin-email "admin@example.com" \
  --admin-password "Admin123!"
```

### 2. التحقق من Tenant

```bash
# عرض Tenants الموجودة
docker-compose exec web python manage.py shell
```

في Python shell:
```python
from tenants.models import Client, Domain
clients = Client.objects.all()
for client in clients:
    print(f"Client: {client.name}, Schema: {client.schema_name}")
    domains = Domain.objects.filter(tenant=client)
    for domain in domains:
        print(f"  Domain: {domain.domain}")
```

### 3. الوصول إلى Admin Panel

1. افتح المتصفح على: `http://farm1.localhost:8000/admin/`
2. استخدم بيانات تسجيل الدخول التي أنشأتها

**ملاحظة:** قد تحتاج إلى إضافة `127.0.0.1 farm1.localhost` في ملف `C:\Windows\System32\drivers\etc\hosts` على Windows.

---

## 🔍 التحقق من Celery

### 1. التحقق من تشغيل Celery Worker

```bash
# عرض سجلات Celery
docker-compose logs celery

# يجب أن ترى رسالة مثل:
# celery@xxx ready.
```

### 2. التحقق من Celery Beat

```bash
# عرض سجلات Celery Beat
docker-compose logs celery-beat
```

### 3. اختبار مهمة Celery بسيطة

في Django shell:
```bash
docker-compose exec web python manage.py shell
```

```python
from tenants.aqua_core.celery import debug_task
result = debug_task.delay()
print(f"Task ID: {result.id}")
print(f"Ready: {result.ready()}")
print(f"Result: {result.get(timeout=10)}")
```

---

## 🐛 حل المشاكل الشائعة

### مشكلة: Database connection error

**الحل:**
```bash
# تأكد من أن PostgreSQL يعمل
docker-compose ps db

# تحقق من السجلات
docker-compose logs db

# إعادة تشغيل قاعدة البيانات
docker-compose restart db
```

### مشكلة: Redis connection error

**الحل:**
```bash
# تأكد من أن Redis يعمل
docker-compose ps redis

# إعادة تشغيل Redis
docker-compose restart redis
```

### مشكلة: Port already in use

**الحل:**
```bash
# تغيير المنافذ في docker-compose.yml
# أو إيقاف الخدمة التي تستخدم المنفذ
```

### مشكلة: Cannot create tenant

**الحل:**
```bash
# تأكد من إجراء Migrations أولاً
docker-compose exec web python manage.py migrate_schemas --shared
docker-compose exec web python manage.py migrate_schemas
```

### مشكلة: Module not found

**الحل:**
```bash
# إعادة بناء Docker image
docker-compose build --no-cache

# تثبيت المتطلبات يدوياً
docker-compose exec web pip install -r requirements.txt
```

---

## 📊 قائمة التحقق النهائية

- [ ] ملف .env موجود و SECRET_KEY آمن
- [ ] جميع الخدمات تعمل (web, db, redis, celery, celery-beat)
- [ ] قاعدة البيانات متصلة
- [ ] Redis يعمل
- [ ] Migrations تمت بنجاح
- [ ] يمكن إنشاء Tenant جديد
- [ ] Admin Panel يعمل
- [ ] Celery Worker يعمل
- [ ] Celery Beat يعمل

---

## 🚀 الخطوات التالية

بعد التأكد من أن كل شيء يعمل:

1. ✅ ابدأ في Sprint 1 - اليوم 1
2. ✅ راجع `AquaERP_Implementation_Plan.md`
3. ✅ ابدأ في بناء تطبيق `accounts` (Custom User Model)

---

**تاريخ الإنشاء:** ديسمبر 2025

