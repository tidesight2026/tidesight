# دليل صيغة Domain - AquaERP

## ⚠️ مهم جداً: صيغة Domain الصحيحة

في `django-tenants`، حقل **Domain** يجب أن يكون **hostname فقط** وليس URL كامل.

---

## ✅ الصيغة الصحيحة

### للتطوير المحلي:
```
tmco.localhost
farm1.localhost
farm2.localhost
```

### للإنتاج:
```
tmco.example.com
farm1.aqua-erp.com
client1.aqua-erp.com
```

---

## ❌ الصيغة الخاطئة

### لا تستخدم:
```
❌ http://localhost:8000/tmco
❌ localhost:8000/tmco
❌ tmco.localhost:8000
❌ http://tmco.localhost
❌ https://tmco.localhost
❌ tmco.localhost/admin
```

---

## 📋 خطوات إضافة Domain

### 1. في Django Admin

1. **افتح صفحة إضافة Domain:**
   - http://localhost:8000/admin/tenants/domain/add/

2. **املأ البيانات:**
   - **Domain:** `tmco.localhost` (hostname فقط!)
   - **Tenant:** اختر Tenant من القائمة
   - **Is primary:** ✓ (إذا كان النطاق الأساسي)

3. **احفظ**

### 2. إضافة Domain إلى hosts file

**في Windows:**
```
C:\Windows\System32\drivers\etc\hosts
```

**أضف السطر:**
```
127.0.0.1    tmco.localhost
```

**في Linux/Mac:**
```
/etc/hosts
```

**أضف السطر:**
```
127.0.0.1    tmco.localhost
```

### 3. الوصول إلى Tenant

بعد إضافة Domain إلى hosts file، يمكنك الوصول إلى Tenant عبر:
```
http://tmco.localhost:8000/admin/
```

---

## 🔧 إصلاح Domain موجود

إذا كان Domain موجود بصيغة خاطئة (مثل `http://localhost:8000/tmco`):

1. **افتح صفحة تعديل Domain:**
   - http://localhost:8000/admin/tenants/domain/2/change/

2. **عدّل Domain إلى:**
   - `tmco.localhost` (بدون http:// وبدون port وبدون path)

3. **احفظ**

---

## 📝 أمثلة

| ❌ خاطئ | ✅ صحيح |
|---------|---------|
| `http://localhost:8000/tmco` | `tmco.localhost` |
| `localhost:8000/tmco` | `tmco.localhost` |
| `tmco.localhost:8000` | `tmco.localhost` |
| `http://tmco.localhost` | `tmco.localhost` |
| `tmco.localhost/admin` | `tmco.localhost` |

---

## ⚠️ ملاحظات مهمة

1. **Domain = Hostname فقط:** لا تضيف `http://` أو `https://`
2. **لا تضيف Port:** لا تضيف `:8000` أو أي port آخر
3. **لا تضيف Path:** لا تضيف `/admin` أو أي مسار آخر
4. **يجب أن يحتوي على نقطة:** مثل `tmco.localhost` أو `farm1.example.com`
5. **Hosts File:** يجب إضافة Domain إلى ملف hosts للوصول إليه محلياً

---

## 🚀 بعد إضافة Domain

1. **أضف Domain إلى hosts file**
2. **شغّل migrations للـ Tenant:**
   ```bash
   docker-compose exec web python manage.py migrate_schemas --tenant --schema_name tmco
   ```

3. **أنشئ مستخدم admin في Tenant:**
   ```bash
   docker-compose exec web python create_admin_user.py
   ```
   (عدّل `SCHEMA_NAME = 'tmco'` في السكريبت)

4. **الوصول:**
   - http://tmco.localhost:8000/admin/

---

**تاريخ الإنشاء:** 2025-12-11
