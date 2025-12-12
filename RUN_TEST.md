# 🚀 تشغيل واختبار AquaERP - دليل سريع

**التاريخ:** ديسمبر 2025

---

## ✅ الوضع الحالي

- ✅ Backend يعمل (Docker Compose)
- ✅ Migrations تمت للـ Public Schema
- ⏳ نحتاج لإنشاء Tenant تجريبي
- ⏳ ثم تشغيل Frontend

---

## 📝 الخطوات

### 1. إنشاء Tenant تجريبي

#### الطريقة الأولى: استخدام Python Script

```bash
# من المجلد الرئيسي
docker-compose exec web python /app/create_test_tenant.py
```

#### الطريقة الثانية: استخدام Django Admin (بعد إنشاء Tenant)

1. افتح: `http://localhost:8000/admin/`
2. سجل دخول (بعد إنشاء Tenant)

---

### 2. إجراء Migrations للـ Tenant

بعد إنشاء Tenant، قم بإجراء migrations للـ Tenant Schema:

```bash
docker-compose exec web python manage.py migrate_schemas
```

---

### 3. تشغيل Frontend

```bash
cd frontend
npm run dev
```

---

### 4. الوصول

- **Frontend:** `http://localhost:5173`
- **Backend API:** `http://farm1.localhost:8000/api/`
- **Swagger UI:** `http://farm1.localhost:8000/api/docs`
- **Admin:** `http://farm1.localhost:8000/admin/`

---

### 5. تسجيل الدخول

- **اسم المستخدم:** `admin`
- **كلمة المرور:** `Admin123!`

---

## ⚠️ ملاحظات مهمة

### إضافة Domain إلى hosts (للتطوير المحلي)

إذا كنت تستخدم Windows، أضف هذا السطر إلى `C:\Windows\System32\drivers\etc\hosts`:

```
127.0.0.1    farm1.localhost
```

إذا كنت تستخدم Linux/Mac، أضف إلى `/etc/hosts`:

```
127.0.0.1    farm1.localhost
```

---

## 🔧 الأوامر السريعة

```bash
# التحقق من حالة الخدمات
docker-compose ps

# عرض سجلات Backend
docker-compose logs -f web

# إعادة تشغيل الخدمات
docker-compose restart web

# إيقاف الخدمات
docker-compose down
```

---

**جاهز للاختبار! 🎉**

