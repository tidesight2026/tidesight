# 🧪 دليل البدء بالاختبار - AquaERP

**التاريخ:** ديسمبر 2025  
**الهدف:** اختبار المشروع بالكامل خطوة بخطوة

---

## ✅ التحضير

### 1. التحقق من المتطلبات

تأكد من أن لديك:
- ✅ Docker Desktop يعمل
- ✅ Node.js 20+ مثبت
- ✅ جميع الملفات موجودة

---

## 🚀 الخطوة 1: إعداد Backend

### 1.1 إنشاء ملف `.env`

```bash
python setup_env.py
```

أو أنشئ ملف `.env` يدوياً:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,*
POSTGRES_DB=aqua_erp_db
POSTGRES_USER=aqua_admin
POSTGRES_PASSWORD=secure_pass_123
POSTGRES_HOST=db
POSTGRES_PORT=5432
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

### 1.2 تشغيل الخدمات

```bash
docker-compose up -d
```

### 1.3 التحقق من الحالة

```bash
docker-compose ps
```

يجب أن ترى:
- `web` (running)
- `db` (running)
- `redis` (running)
- `celery_worker` (running)
- `celery_beat` (running)

### 1.4 إجراء Migrations

```bash
# Migrations للـ Schema المشترك
docker-compose exec web python manage.py migrate_schemas --shared

# Migrations للـ Tenants
docker-compose exec web python manage.py migrate_schemas
```

### 1.5 إنشاء Tenant تجريبي

```bash
docker-compose exec web python manage.py create_tenant \
  --name "مزرعة تجريبية" \
  --domain "farm1" \
  --email "test@example.com" \
  --admin-username "admin" \
  --admin-email "admin@example.com" \
  --admin-password "Admin123!"
```

### 1.6 اختبار API

افتح المتصفح:
- **Swagger UI:** `http://farm1.localhost:8000/api/docs`
- يجب أن ترى 4 Endpoints للمصادقة

---

## 🎨 الخطوة 2: إعداد Frontend

### 2.1 الانتقال إلى مجلد Frontend

```bash
cd frontend
```

### 2.2 التحقق من المكتبات

```bash
npm list --depth=0
```

يجب أن ترى جميع المكتبات مثبتة.

### 2.3 تشغيل Frontend

```bash
npm run dev
```

### 2.4 الوصول

افتح المتصفح:
- **Frontend:** `http://localhost:5173`
- يجب أن ترى صفحة Login

---

## 🧪 الخطوة 3: الاختبار

### 3.1 اختبار صفحة Login

1. افتح `http://localhost:5173`
2. يجب أن ترى:
   - ✅ النص من اليمين لليسار (RTL)
   - ✅ خط Cairo
   - ✅ تصميم جميل
   - ✅ حقل اسم المستخدم
   - ✅ حقل كلمة المرور
   - ✅ زر تسجيل الدخول

### 3.2 اختبار تسجيل الدخول

1. أدخل بيانات Tenant:
   - **اسم المستخدم:** `admin`
   - **كلمة المرور:** `Admin123!`
2. اضغط "تسجيل الدخول"
3. يجب أن:
   - ✅ يتم تسجيل الدخول بنجاح
   - ✅ يتم التوجيه إلى Dashboard
   - ✅ تظهر معلومات المستخدم

### 3.3 اختبار Dashboard

1. بعد تسجيل الدخول، يجب أن ترى:
   - ✅ معلومات المستخدم
   - ✅ زر تسجيل الخروج
2. اضغط "تسجيل الخروج"
3. يجب أن:
   - ✅ يتم تسجيل الخروج
   - ✅ يتم التوجيه إلى Login

---

## 🐛 حل المشاكل

### المشكلة: Docker لا يعمل

```bash
# إعادة تشغيل Docker Desktop
# ثم:
docker-compose down
docker-compose up -d
```

### المشكلة: Backend لا يعمل

```bash
# التحقق من السجلات
docker-compose logs web

# إعادة بناء الصورة
docker-compose build
docker-compose up -d
```

### المشكلة: Frontend لا يعمل

```bash
# حذف node_modules وإعادة التثبيت
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### المشكلة: تسجيل الدخول لا يعمل

1. تحقق من Backend:
   ```bash
   curl http://localhost:8000/api/auth/login
   ```

2. تحقق من CORS في `settings.py`

3. تحقق من بيانات Tenant

---

## ✅ قائمة التحقق

### Backend
- [ ] Docker يعمل
- [ ] جميع الخدمات تعمل
- [ ] Migrations تمت بنجاح
- [ ] Tenant تم إنشاؤه
- [ ] API يعمل

### Frontend
- [ ] Frontend يعمل
- [ ] صفحة Login تظهر
- [ ] RTL يعمل
- [ ] Tailwind CSS يعمل

### التكامل
- [ ] تسجيل الدخول يعمل
- [ ] Dashboard يظهر
- [ ] تسجيل الخروج يعمل

---

## 🎯 الخطوات التالية

بعد نجاح الاختبار:

1. ✅ النظام جاهز للاستخدام
2. 📝 راجع `COMPLETE_PROJECT_SUMMARY.md`
3. 🚀 ابدأ Sprint 2

---

## 📚 المراجع

- **[TEST_GUIDE.md](TEST_GUIDE.md)** - دليل الاختبار الشامل
- **[COMPLETE_PROJECT_SUMMARY.md](COMPLETE_PROJECT_SUMMARY.md)** - الملخص الكامل
- **[PROJECT_STATUS.md](PROJECT_STATUS.md)** - حالة المشروع

---

**جاهز للاختبار! ابدأ الآن! 🚀**

---

**تاريخ الإنشاء:** ديسمبر 2025

