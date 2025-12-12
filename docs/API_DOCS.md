# توثيق APIs - AquaERP

> هذا الملف يوثق جميع APIs في AquaERP مع أمثلة على الاستخدام.

---

## Traceability APIs

### 1. GET /api/traceability/by-invoice/{invoice_id}

استرجاع سلسلة التتبع من الفاتورة إلى الدفعة.

#### الوصف
يعيد معلومات كاملة عن:
- الفاتورة
- طلب البيع المرتبط
- الحصاد المرتبط
- الدفعات المرتبطة
- سجلات التغذية والنفوق

#### المعاملات
- `invoice_id` (path parameter): معرف الفاتورة (integer)

#### المصادقة
يتطلب مصادقة JWT (TokenAuth)

#### الاستجابة

**نجاح (200):**
```json
{
  "invoice": {
    "id": 1,
    "invoice_number": "INV-001",
    "invoice_date": "2024-01-15",
    "total_amount": 3450.00,
    "status": "issued"
  },
  "sales_order": {
    "id": 1,
    "order_number": "SO-001",
    "order_date": "2024-01-13",
    "customer_name": "عميل تجريبي",
    "total_amount": 3450.00,
    "status": "confirmed"
  },
  "harvests": [
    {
      "id": 1,
      "harvest_date": "2024-01-10",
      "quantity_kg": 200.00,
      "count": 200,
      "average_weight": 1.00,
      "status": "completed"
    }
  ],
  "batches": [
    {
      "id": 1,
      "batch_number": "BATCH-001",
      "start_date": "2023-11-01",
      "species_name": "سمك البلطي",
      "pond_name": "حوض 1",
      "initial_count": 1000,
      "initial_weight": 100.00,
      "current_count": 950,
      "current_weight": 500.00,
      "status": "active"
    }
  ],
  "feeding_logs": [
    {
      "id": 1,
      "feeding_date": "2023-12-15",
      "quantity": 50.00,
      "feed_type_name": "علف"
    }
  ],
  "mortality_logs": [
    {
      "id": 1,
      "mortality_date": "2023-12-20",
      "count": 50,
      "cause": "مرض"
    }
  ]
}
```

**خطأ (404):**
```json
{
  "detail": "الفاتورة رقم 999 غير موجودة"
}
```

**خطأ (500):**
```json
{
  "detail": "خطأ في استرجاع البيانات: [تفاصيل الخطأ]"
}
```

#### مثال على الاستخدام

**cURL:**
```bash
curl -X GET "http://localhost:8000/api/traceability/by-invoice/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**JavaScript (fetch):**
```javascript
const response = await fetch('http://localhost:8000/api/traceability/by-invoice/1', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});

const data = await response.json();
console.log(data);
```

**Python (requests):**
```python
import requests

url = "http://localhost:8000/api/traceability/by-invoice/1"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)
data = response.json()
print(data)
```

---

### 2. GET /api/traceability/by-batch/{batch_id}

استرجاع سلسلة التتبع من الدفعة إلى المبيعات.

#### الوصف
يعيد معلومات كاملة عن:
- الدفعة
- جميع الحصاد المرتبطة
- جميع طلبات البيع المرتبطة
- جميع الفواتير المرتبطة
- سجلات التغذية والنفوق

#### المعاملات
- `batch_id` (path parameter): معرف الدفعة (integer)

#### المصادقة
يتطلب مصادقة JWT (TokenAuth)

#### الاستجابة

**نجاح (200):**
```json
{
  "batch": {
    "id": 1,
    "batch_number": "BATCH-001",
    "start_date": "2023-11-01",
    "species_name": "سمك البلطي",
    "pond_name": "حوض 1",
    "initial_count": 1000,
    "initial_weight": 100.00,
    "current_count": 950,
    "current_weight": 500.00,
    "status": "active"
  },
  "harvests": [
    {
      "id": 1,
      "harvest_date": "2024-01-10",
      "quantity_kg": 200.00,
      "count": 200,
      "average_weight": 1.00,
      "status": "completed"
    }
  ],
  "sales_orders": [
    {
      "id": 1,
      "order_number": "SO-001",
      "order_date": "2024-01-13",
      "customer_name": "عميل تجريبي",
      "total_amount": 3450.00,
      "status": "confirmed"
    }
  ],
  "invoices": [
    {
      "id": 1,
      "invoice_number": "INV-001",
      "invoice_date": "2024-01-15",
      "total_amount": 3450.00,
      "status": "issued"
    }
  ],
  "feeding_logs": [
    {
      "id": 1,
      "feeding_date": "2023-12-15",
      "quantity": 50.00,
      "feed_type_name": "علف"
    }
  ],
  "mortality_logs": [
    {
      "id": 1,
      "mortality_date": "2023-12-20",
      "count": 50,
      "cause": "مرض"
    }
  ]
}
```

**خطأ (404):**
```json
{
  "detail": "الدفعة رقم 999 غير موجودة"
}
```

**خطأ (500):**
```json
{
  "detail": "خطأ في استرجاع البيانات: [تفاصيل الخطأ]"
}
```

#### مثال على الاستخدام

**cURL:**
```bash
curl -X GET "http://localhost:8000/api/traceability/by-batch/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**JavaScript (fetch):**
```javascript
const response = await fetch('http://localhost:8000/api/traceability/by-batch/1', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});

const data = await response.json();
console.log(data);
```

**Python (requests):**
```python
import requests

url = "http://localhost:8000/api/traceability/by-batch/1"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)
data = response.json()
print(data)
```

---

## ملاحظات مهمة

### 1. المصادقة
جميع Traceability APIs تتطلب مصادقة JWT. يجب إرسال التوكن في header:
```
Authorization: Bearer YOUR_JWT_TOKEN
```

### 2. حدود البيانات
- يتم إرجاع آخر 50 سجل تغذية لكل دفعة
- يتم إرجاع آخر 50 سجل نفوق لكل دفعة
- يمكن تعديل هذه الحدود حسب الحاجة

### 3. الأداء
- يتم استخدام `select_related` و `prefetch_related` لتحسين الأداء
- يُنصح باستخدام pagination للدفعات الكبيرة

### 4. الأخطاء
- 404: المورد غير موجود
- 500: خطأ في الخادم
- 401: غير مصرح (مصادقة مطلوبة)
- 403: محظور (صلاحيات غير كافية)

---

## أمثلة على حالات الاستخدام

### حالة 1: تتبع منتج من الفاتورة
```
مستخدم يريد معرفة مصدر السمك المباع في فاتورة معينة
→ استخدام: GET /api/traceability/by-invoice/{invoice_id}
→ النتيجة: معلومات كاملة عن الدفعة، الحصاد، والتغذية
```

### حالة 2: تتبع مبيعات دفعة معينة
```
مستخدم يريد معرفة جميع المبيعات المرتبطة بدفعة معينة
→ استخدام: GET /api/traceability/by-batch/{batch_id}
→ النتيجة: جميع الحصاد، طلبات البيع، والفواتير المرتبطة
```

---

**تاريخ الإنشاء:** 2024  
**آخر تحديث:** 2024
