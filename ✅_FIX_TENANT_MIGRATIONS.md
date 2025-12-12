# ✅ إصلاح مشكلة Migrations في Tenant Schemas

**التاريخ:** ديسمبر 2025  
**المشكلة:** `inventory_feedtype` غير موجود في tenant schema أثناء الاختبارات

---

## 🔍 تحليل المشكلة

### المشكلة الأساسية:
عند تشغيل الاختبارات باستخدام `TenantTestCase`، يظهر الخطأ:
```
django.db.utils.ProgrammingError: relation "inventory_feedtype" does not exist
```

### السبب:
1. ✅ `inventory` موجود في `TENANT_APPS` (صحيح)
2. ⚠️ `TenantTestCase` قد لا يقوم بتشغيل migrations بشكل كامل لجميع التطبيقات
3. ⚠️ قد يكون هناك مشاكل في ترتيب migrations أو تطبيقها

---

## ✅ الحلول المطبقة

### 1. إضافة فحص Migrations في setUpClass

تم إضافة كود في `setUpClass` للتحقق من وجود الجداول المطلوبة وتشغيل migrations إذا لزم الأمر:

```python
@classmethod
def setUpClass(cls):
    super().setUpClass()
    
    with schema_context(cls.tenant.schema_name):
        from django.db import connection
        tables = connection.introspection.table_names()
        
        required_tables = ['inventory_feedtype', 'inventory_feedinventory']
        missing_tables = [t for t in required_tables if t not in tables]
        
        if missing_tables:
            print(f"⚠️ Warning: Missing tables: {missing_tables}")
            call_command('migrate', 
                       schema_name=cls.tenant.schema_name,
                       verbosity=0,
                       interactive=False)
```

### 2. إضافة فحص إضافي في setUp

تم إضافة فحص إضافي في `setUp` للتأكد من وجود الجداول قبل بدء الاختبارات.

### 3. إصلاح Batch Model

تم إضافة حقل `start_date` المطلوب عند إنشاء `Batch` في الاختبارات.

---

## 🔧 كيفية التحقق من المشكلة يدوياً

### 1. التحقق من إعدادات التطبيقات:

```bash
docker-compose exec web python manage.py shell
```

```python
from tenants.aqua_core.settings import TENANT_APPS, SHARED_APPS
print("TENANT_APPS:", [app for app in TENANT_APPS if 'inventory' in app.lower()])
print("SHARED_APPS:", [app for app in SHARED_APPS if 'inventory' in app.lower()])
```

**يجب أن يظهر:**
```
TENANT_APPS: ['inventory']
SHARED_APPS: []
```

### 2. التحقق من وجود Migrations:

```bash
docker-compose exec web python manage.py showmigrations inventory
```

يجب أن ترى قائمة migrations متاحة.

### 3. التحقق من الجداول في Tenant Schema:

```bash
docker-compose exec web python manage.py shell
```

```python
from tenants.models import Client
from django_tenants.utils import schema_context
from django.db import connection

# الحصول على tenant
tenant = Client.objects.get(schema_name='test_farm')  # أو أي tenant آخر

# الانتقال إلى tenant schema
with schema_context(tenant.schema_name):
    tables = connection.introspection.table_names()
    print("Tables in tenant schema:")
    for table in sorted(tables):
        if 'inventory' in table:
            print(f"  ✅ {table}")
    
    # التحقق من وجود الجداول المطلوبة
    required_tables = ['inventory_feedtype', 'inventory_feedinventory']
    missing = [t for t in required_tables if t not in tables]
    if missing:
        print(f"\n❌ Missing tables: {missing}")
    else:
        print(f"\n✅ All required tables exist!")
```

### 4. تشغيل Migrations يدوياً:

```bash
# للـ Public Schema
docker-compose exec web python manage.py migrate_schemas --shared

# لـ Tenant محدد
docker-compose exec web python manage.py migrate_schemas --schema test_farm

# لجميع Tenants
docker-compose exec web python manage.py migrate_schemas
```

---

## 🧪 تشغيل الاختبارات

### بعد الإصلاح:

```bash
# تشغيل اختبار محدد
docker-compose exec web python manage.py test tests.test_feed_lifecycle_tenant.TestFeedLifecycleTenant.test_feed_purchase_and_inventory --verbosity=2

# تشغيل جميع اختبارات feed lifecycle
docker-compose exec web python manage.py test tests.test_feed_lifecycle_tenant --verbosity=2
```

---

## 📋 قائمة التحقق

- [x] `inventory` موجود في `TENANT_APPS` (وليس `SHARED_APPS`)
- [x] إضافة فحص migrations في `setUpClass`
- [x] إضافة فحص إضافي في `setUp`
- [x] إصلاح `Batch` model في الاختبارات (إضافة `start_date`)
- [ ] التحقق من أن migrations تعمل بشكل صحيح في `TenantTestCase`
- [ ] اختبار يدوي للتأكد من وجود الجداول

---

## 🎯 الخطوة التالية

إذا استمرت المشكلة:

1. **تأكد من وجود migrations:**
   ```bash
   ls -la inventory/migrations/
   ```

2. **تحقق من أن migrations ليست فارغة:**
   ```bash
   docker-compose exec web python manage.py showmigrations inventory
   ```

3. **إذا لم تكن migrations موجودة، قم بإنشائها:**
   ```bash
   docker-compose exec web python manage.py makemigrations inventory
   ```

4. **قم بتطبيق migrations:**
   ```bash
   docker-compose exec web python manage.py migrate_schemas --shared
   docker-compose exec web python manage.py migrate_schemas
   ```

---

**ملاحظة:** `TenantTestCase` يجب أن يقوم تلقائياً بتشغيل migrations عند إنشاء tenant schema للاختبارات. إذا لم يحدث ذلك، قد تكون هناك مشكلة في إعداد `django-tenants` أو في ترتيب migrations.

