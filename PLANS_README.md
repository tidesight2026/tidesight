# 📋 ملفات مميزات وقيود الباقات / Plans Features and Quotas Files

## 📁 الملفات المتوفرة / Available Files

### 1. `PLANS_FEATURES_AND_QUOTAS.json`
**ملف JSON شامل** يحتوي على جميع بيانات الباقات بصيغة JSON صالحة.

**المحتوى:**
- بيانات الباقات الثلاث (أساسي، احترافي، مؤسسي)
- المميزات (Features) لكل باقة
- القيود (Quotas) لكل باقة
- أوصاف المميزات والقيود باللغتين العربية والإنجليزية
- الأسعار وأيام التجربة

**الاستخدام:**
```python
import json

# قراءة الملف
with open('PLANS_FEATURES_AND_QUOTAS.json', 'r', encoding='utf-8') as f:
    plans_data = json.load(f)

# الحصول على بيانات الباقة الأساسية
basic_plan = plans_data['plans']['basic']
basic_features = basic_plan['features']
basic_quotas = basic_plan['quotas']
```

### 2. `PLANS_FEATURES_AND_QUOTAS.md`
**ملف Markdown مفصل** يحتوي على:
- وصف شامل لكل باقة
- جداول مقارنة للمميزات والقيود
- أوصاف باللغتين العربية والإنجليزية
- ملاحظات مهمة

**الاستخدام:** للقراءة والمراجعة والتوثيق

### 3. `PLANS_QUICK_REFERENCE.txt`
**ملف نصي بسيط** للمراجعة السريعة:
- ملخص سريع للباقات الثلاث
- مقارنة سريعة في جدول
- مناسب للطباعة أو المراجعة السريعة

**الاستخدام:** للرجوع السريع والطباعة

---

## 🚀 كيفية استخدام البيانات في Django

### مثال: إنشاء باقة في Django Admin

```python
# في Django Shell أو Management Command
from tenants.models import Plan
import json

# قراءة بيانات الباقة الأساسية
with open('PLANS_FEATURES_AND_QUOTAS.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

basic_data = data['plans']['basic']

# إنشاء الباقة الأساسية
basic_plan = Plan.objects.create(
    name='Basic',
    name_ar='أساسي',
    description=basic_data['description']['en'],
    description_ar=basic_data['description']['ar'],
    price_monthly=basic_data['price_monthly'],
    price_yearly=basic_data['price_yearly'],
    trial_days=basic_data['trial_days'],
    is_featured=basic_data['is_featured'],
    sort_order=basic_data['sort_order'],
    features=basic_data['features'],
    quotas=basic_data['quotas']
)
```

### مثال: إنشاء جميع الباقات

```python
import json
from tenants.models import Plan

with open('PLANS_FEATURES_AND_QUOTAS.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for plan_key, plan_data in data['plans'].items():
    plan, created = Plan.objects.update_or_create(
        name=plan_data['name']['en'],
        defaults={
            'name_ar': plan_data['name']['ar'],
            'description': plan_data['description']['en'],
            'description_ar': plan_data['description']['ar'],
            'price_monthly': plan_data['price_monthly'],
            'price_yearly': plan_data['price_yearly'],
            'trial_days': plan_data['trial_days'],
            'is_featured': plan_data['is_featured'],
            'sort_order': plan_data['sort_order'],
            'features': plan_data['features'],
            'quotas': plan_data['quotas'],
            'is_active': True
        }
    )
    if created:
        print(f"✅ تم إنشاء باقة: {plan.name_ar}")
    else:
        print(f"🔄 تم تحديث باقة: {plan.name_ar}")
```

---

## 📊 هيكل البيانات / Data Structure

### المميزات (Features)
كل ميزة هي `boolean` (true/false):
- `true` = متاحة في الباقة
- `false` = غير متاحة في الباقة

### القيود (Quotas)
كل قيد هو `number` أو `null`:
- `number` = الحد الأقصى المسموح
- `null` = غير محدود (unlimited)

---

## 🔍 المميزات المتاحة / Available Features

| الميزة | الوصف |
|--------|-------|
| `biological_management` | إدارة الأنواع والدفعات والبرك |
| `daily_operations` | تسجيل العمليات اليومية |
| `inventory_management` | إدارة المخزون |
| `basic_reports` | التقارير الأساسية |
| `advanced_reports` | التقارير المتقدمة |
| `accounting` | وحدة المحاسبة |
| `zatca_integration` | تكامل ZATCA |
| `iot_integration` | تكامل IoT |
| `api_access` | وصول API |
| `custom_reports` | تقارير مخصصة |
| `data_export` | تصدير البيانات |
| `email_support` | دعم بريد إلكتروني |
| `priority_support` | دعم ذو أولوية |
| `dedicated_support` | دعم مخصص |
| `white_label` | علامة بيضاء |
| `multi_location` | مواقع متعددة |
| `audit_logs` | سجلات التدقيق |
| `backup_restore` | نسخ احتياطي |

---

## 📏 القيود المتاحة / Available Quotas

| القيد | الوصف |
|-------|-------|
| `max_ponds` | الحد الأقصى للبرك |
| `max_users` | الحد الأقصى للمستخدمين |
| `max_batches` | الحد الأقصى للدفعات |
| `max_storage_gb` | الحد الأقصى لمساحة التخزين (GB) |
| `max_sales_orders_per_month` | الحد الأقصى لأوامر البيع شهرياً |
| `max_invoices_per_month` | الحد الأقصى للفواتير شهرياً |
| `api_rate_limit_per_hour` | معدل API في الساعة |
| `max_export_records` | الحد الأقصى للسجلات لكل تصدير |

---

## ⚠️ ملاحظات مهمة / Important Notes

1. **الأسعار:** جميع الأسعار بالريال السعودي (SAR)
2. **القيود غير المحدودة:** استخدم `null` في JSON للقيود غير المحدودة
3. **الترميز:** جميع الملفات تستخدم UTF-8 encoding
4. **التحديثات:** عند تحديث البيانات، تأكد من تحديث جميع الملفات الثلاثة

---

## 📅 معلومات الملفات

- **تاريخ الإنشاء:** 2025-12-11
- **آخر تحديث:** 2025-12-11
- **الإصدار:** 1.0

---

## 🔗 روابط مفيدة / Useful Links

- [Django JSONField Documentation](https://docs.djangoproject.com/en/stable/ref/models/fields/#jsonfield)
- [JSON Schema Validator](https://json-schema.org/)

---

**تم إنشاء هذه الملفات بواسطة:** AquaERP Development Team  
**للدعم:** راجع ملفات التوثيق في مجلد `docs/`
