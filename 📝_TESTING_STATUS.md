# 📝 حالة الاختبارات - AquaERP

**التاريخ:** ديسمبر 2025

---

## ⚠️ المشكلة الحالية

الاختبارات لا تعمل بشكل صحيح مع `django-tenants` لأن:

1. **`inventory` موجود في `TENANT_APPS`** - يعني أن جداولها في tenant schemas وليس public schema
2. **pytest-django** يعمل migrations على public schema فقط في test database
3. **الاختبارات تحتاج للعمل ضمن tenant schema**

---

## ✅ الحلول المقترحة

### الحل 1: استخدام TenantTestCase (موصى به)

تم إنشاء `tests/test_feed_lifecycle_tenant.py` يستخدم `TenantTestCase` من `django-tenants`.

**المميزات:**
- ✅ يعمل تلقائياً مع django-tenants
- ✅ يقوم بإنشاء tenant schema وتشغيل migrations تلقائياً
- ✅ لا يحتاج لإعدادات إضافية

**الاستخدام:**
```python
from django_tenants.test.cases import TenantTestCase

class TestFeedLifecycle(TenantTestCase):
    def setUp(self):
        # إعداد البيانات
        pass
```

### الحل 2: إصلاح pytest fixtures

يحتاج لتحديث `tests/conftest.py` و `conftest.py` لضمان:
- إنشاء tenant
- تشغيل migrations على tenant schema
- استخدام tenant_context

---

## 📋 الملفات

- ✅ `tests/test_feed_lifecycle.py` - الاختبارات الأصلية (تحتاج إصلاح)
- ✅ `tests/test_feed_lifecycle_tenant.py` - اختبارات باستخدام TenantTestCase
- ✅ `tests/test_fish_lifecycle.py` - اختبارات دورة حياة السمكة (تحتاج إصلاح)
- ⚠️ `tests/conftest.py` - يحتاج تحديث لدعم tenant schemas

---

## 🚀 الخطوة التالية

1. **اختبار `test_feed_lifecycle_tenant.py`** باستخدام TenantTestCase
2. **إذا نجح** - تحديث جميع الاختبارات لاستخدام TenantTestCase
3. **أو** إصلاح pytest fixtures لدعم tenant schemas

---

**ملاحظة:** `django-tenants` يوفر `TenantTestCase` خصيصاً للاختبارات مع multi-tenancy.

