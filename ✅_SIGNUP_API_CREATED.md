# ✅ Sign-up API - تم الإنشاء

**التاريخ:** ديسمبر 2025  
**الحالة:** ✅ تم الإنجاز

---

## ✅ ما تم إنجازه

### 1. إنشاء Sign-up API Endpoint

تم إنشاء ملف `api/signup.py` مع endpoint `/api/signup` الذي يقوم بـ:

1. ✅ **التحقق من النطاق المتاح**
   - التحقق من أن `schema_name` غير مستخدم
   - التحقق من أن البريد الإلكتروني غير مستخدم

2. ✅ **إنشاء Client (Tenant)**
   - إنشاء tenant جديد مع البيانات المطلوبة
   - تعيين `subscription_type='trial'` و `on_trial=True`

3. ✅ **إنشاء Domain**
   - ربط Domain بـ Tenant
   - استخدام `{domain}.localhost` للتطوير

4. ✅ **إنشاء Subscription**
   - ربط Tenant بـ "Hatchery Plan" (الباقة التجريبية)
   - فترة تجريبية: **14 يوم**
   - `status='trial'` و `auto_renew=False`

5. ✅ **إنشاء مستخدم Admin**
   - إنشاء Owner في tenant schema
   - `is_staff=True` و `is_superuser=True`

---

## 📋 Schema

### SignUpRequest
```python
{
    "company_name": "مزرعة تجريبية",
    "domain": "farm2",
    "email": "farm2@example.com",
    "phone": "0501234567",  # optional
    "admin_username": "admin",
    "admin_email": "admin@farm2.com",
    "admin_password": "SecurePass123",
    "admin_full_name": "مدير المزرعة"
}
```

### SignUpResponse
```python
{
    "success": true,
    "message": "✅ تم إنشاء Tenant بنجاح!",
    "tenant_id": 1,
    "domain": "farm2.localhost",
    "subscription_status": "trial",
    "trial_end_date": "2025-12-20"
}
```

---

## 🚀 استخدام API

### مثال باستخدام curl:
```bash
curl -X POST http://localhost:8000/api/signup \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "مزرعة تجريبية",
    "domain": "farm2",
    "email": "farm2@example.com",
    "admin_username": "admin",
    "admin_email": "admin@farm2.com",
    "admin_password": "SecurePass123",
    "admin_full_name": "مدير المزرعة"
  }'
```

### مثال باستخدام JavaScript/TypeScript:
```typescript
const response = await fetch('http://localhost:8000/api/signup', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    company_name: 'مزرعة تجريبية',
    domain: 'farm2',
    email: 'farm2@example.com',
    admin_username: 'admin',
    admin_email: 'admin@farm2.com',
    admin_password: 'SecurePass123',
    admin_full_name: 'مدير المزرعة'
  })
});

const data = await response.json();
console.log(data);
```

---

## ✅ المخرجات

1. ✅ Tenant جديد مع Schema منفصل
2. ✅ Domain مربوط بـ Tenant
3. ✅ Subscription تجريبي لمدة 14 يوم
4. ✅ مستخدم Admin جاهز للتسجيل

---

## 📝 ملاحظات

- **Authentication:** Sign-up لا يحتاج authentication (مفتوح للجميع)
- **Trial Period:** الفترة التجريبية 14 يوم
- **Default Plan:** Hatchery Plan (الخطة الأقل سعراً)
- **Auto Renew:** `False` للفترة التجريبية (لا يتم التجديد التلقائي)

---

## 🔄 الخطوات التالية

1. ✅ إنشاء Frontend form للتسجيل
2. ✅ إضافة validation للـ domain (تجنب أحرف خاصة)
3. ✅ إرسال email تأكيد بعد التسجيل
4. ✅ إضافة صفحة تفعيل الحساب

---

**✨ Sign-up API جاهز للاستخدام!** ✨

