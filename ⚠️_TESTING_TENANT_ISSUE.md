# ⚠️ ملاحظة: مشكلة الاختبارات مع django-tenants

**التاريخ:** ديسمبر 2025

---

## 🔍 المشكلة

الاختبارات فشلت لأن:

1. **`inventory` موجود في `TENANT_APPS`** - يعني أن جداولها يجب أن تكون في tenant schema وليس public schema
2. **pytest-django** يعمل migrations على test database لكن **داخل public schema فقط**
3. **الاختبارات تحتاج للعمل ضمن tenant schema** ولكن migrations لم تعمل على tenant schema

---

## ✅ الحل الموصى به

### الخيار 1: استخدام Django TestCase بدلاً من pytest (موصى به للـ django-tenants)

```python
from django.test import TestCase
from django_tenants.test.cases import TenantTestCase

class TestFeedLifecycle(TenantTestCase):
    """اختبارات دورة حياة العلف"""
    
    def setUp(self):
        # TenantTestCase يقوم تلقائياً بإنشاء tenant وتشغيل migrations
        pass
```

### الخيار 2: إصلاح pytest fixtures

يجب تحديث `tests/conftest.py` لضمان:
1. إنشاء tenant في public schema
2. تشغيل migrations على tenant schema
3. استخدام tenant_context في جميع الاختبارات

### الخيار 3: استخدام Django Test Client

```python
from django.test import TestCase
from django_tenants.test.client import TenantClient

class TestFeedLifecycle(TestCase):
    def setUp(self):
        # استخدام TenantClient
        self.client = TenantClient(...)
```

---

## 📝 الخطوات التالية

1. **تحديث الاختبارات** لاستخدام `TenantTestCase` من `django-tenants`
2. **أو** إصلاح fixtures في `conftest.py` لضمان تشغيل migrations بشكل صحيح

---

**ملاحظة:** django-tenants له طريقة خاصة للاختبارات. يجب استخدام `TenantTestCase` أو `TenantClient` المخصص له.

