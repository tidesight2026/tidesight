# 🔴 إصلاح عاجل: مشكلة 404 للـ API

**الأولوية:** عاجل جداً  
**الحالة:** يمنع استكمال الخطة

---

## 🎯 الحل التجريبي المقترح

نقل `api` من `TENANT_APPS` إلى `SHARED_APPS` مؤقتاً لاختبار إذا كانت المشكلة في tenant context loading.

### التعديل المطلوب

في `tenants/aqua_core/settings.py`:

**قبل:**

```python
TENANT_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'accounts',  # تطبيق المستخدمين - معزول لكل tenant
    'api',  # ❌ API endpoints - معزول لكل tenant
)
```

**بعد (تجريبي):**

```python
SHARED_APPS = (
    'django_tenants',
    'tenants',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'django_celery_beat',
    'api',  # ✅ نقل api هنا مؤقتاً للاختبار
)

TENANT_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'accounts',  # تطبيق المستخدمين - معزول لكل tenant
)
```

---

## ⚠️ تحذير

هذا حل تجريبي فقط! الهدف هو:

1. التحقق من أن المشكلة في tenant context loading
2. إكمال Sprint 1
3. البحث عن حل أفضل لاحقاً

---

## 🔄 الخطوات بعد التعديل

1. إعادة تشغيل Backend
2. اختبار `/api/auth/login`
3. إذا عمل: متابعة الخطة ✅
4. إذا لم يعمل: البحث عن حل آخر

---

**هل تريد تجربة هذا الحل؟** 🚀
