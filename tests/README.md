# 📋 دليل الاختبارات - AquaERP

**التاريخ:** ديسمبر 2025

---

## 🚀 تشغيل الاختبارات

### ✅ الطريقة الموصى بها: استخدام Django Test مع TenantTestCase

لأن المشروع يستخدم django-tenants مع tenant schemas، الطريقة الأفضل هي استخدام `TenantTestCase`:

```bash
# اختبار واحد
docker-compose exec web python manage.py test tests.test_feed_lifecycle_tenant.TestFeedLifecycleTenant.test_feed_purchase_and_inventory

# جميع اختبارات دورة حياة العلف
docker-compose exec web python manage.py test tests.test_feed_lifecycle_tenant

# جميع اختبارات دورة حياة السمكة
docker-compose exec web python manage.py test tests.test_fish_lifecycle_tenant
```

### ⚠️ استخدام pytest (يحتاج إصلاحات إضافية)

pytest مع tenant schemas يحتاج إعدادات خاصة. حالياً يوجد مشكلة في migrations.

```bash
# لن يعمل حالياً - يحتاج إصلاح
docker-compose exec web pytest tests/test_feed_lifecycle.py
```

---

## 📁 ملفات الاختبار

### ✅ الملفات التي تعمل حالياً:

1. **`tests/test_feed_lifecycle_tenant.py`**
   - يستخدم `TenantTestCase`
   - يعمل بشكل صحيح ✅
   - اختبارات دورة حياة العلف

2. **`tests/test_fish_lifecycle_tenant.py`**
   - يستخدم `TenantTestCase`
   - يعمل بشكل صحيح ✅
   - اختبارات دورة حياة السمكة

### ⚠️ الملفات التي تحتاج إصلاح:

1. **`tests/test_feed_lifecycle.py`**
   - يستخدم pytest
   - يحتاج إصلاح conftest.py لدعم tenant schemas بشكل صحيح

---

## 🔧 كيفية إصلاح pytest للاختبارات

المشكلة الأساسية هي أن pytest لا يقوم تلقائياً بتشغيل migrations على tenant schemas. 

### الحل الموصى به:

**استخدام TenantTestCase بدلاً من pytest للاختبارات التي تحتاج tenant schemas.**

أو إصلاح `conftest.py` لضمان تشغيل migrations بشكل صحيح:

```python
@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        # إنشاء tenant
        # تشغيل migrations على tenant schema
        pass
```

---

## ✅ الاختبارات الناجحة

- ✅ `test_feed_purchase_and_inventory` في `test_feed_lifecycle_tenant.py`
- ✅ جميع الاختبارات في `TestFeedLifecycleTenant` (مع بعض التحذيرات)

---

## 📝 ملاحظات

- `TenantTestCase` يقوم تلقائياً بإنشاء tenant schema وتشغيل migrations
- جميع الاختبارات تعمل ضمن tenant context
- البيانات معزولة بين الاختبارات

---

**✨ استخدم Django Test مع TenantTestCase للاختبارات!** ✨
