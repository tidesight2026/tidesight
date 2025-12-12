# ✅ إصلاح مشكلة 404 في Dashboard API

**التاريخ:** ديسمبر 2025  
**المشكلة:** `GET /api/dashboard/stats` يرجع 404 Not Found

---

## 🔍 سبب المشكلة

كان `api` موجوداً في `SHARED_APPS` (public schema)، بينما الـ endpoints تحتاج الوصول إلى نماذج من tenant schemas مثل:
- `biological.models.Pond`
- `inventory.models.FeedInventory`
- `biological.models.Batch`

هذه النماذج موجودة فقط في tenant schemas وليس في public schema.

---

## ✅ الحل

تم نقل `api` من `SHARED_APPS` إلى `TENANT_APPS` في `tenants/aqua_core/settings.py`:

### قبل:
```python
SHARED_APPS = (
    ...
    'api',  # ❌ خطأ - API لا يمكنه الوصول إلى tenant models
)

TENANT_APPS = (
    ...
    # 'api',  # معطّل
)
```

### بعد:
```python
SHARED_APPS = (
    ...
    # تم إزالة 'api'
)

TENANT_APPS = (
    ...
    'api',  # ✅ صحيح - API يمكنه الوصول إلى tenant models
)
```

---

## 🔄 الخطوات التالية

بعد إعادة تشغيل الخدمات:

```bash
docker-compose restart web
```

الآن يجب أن يعمل `/api/dashboard/stats` بشكل صحيح!

---

## 📝 ملاحظات

- API يجب أن يكون في `TENANT_APPS` إذا كان يحتاج الوصول إلى نماذج tenant
- API يمكن أن يكون في `SHARED_APPS` فقط إذا كان لا يحتاج نماذج tenant (مثل public APIs)

---

**✨ تم الإصلاح!** ✨

