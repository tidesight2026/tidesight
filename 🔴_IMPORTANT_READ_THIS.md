# 🔴 مهم جداً - اقرأ هذا أولاً!

**التاريخ:** ديسمبر 2025

---

## ⚠️ أنت داخل Python Shell!

إذا كنت ترى `>>>` في Terminal، أنت داخل Python Shell.

### للخروج:

اكتب:
```
exit()
```

أو اضغط: `Ctrl+Z` ثم Enter (في Windows)

---

## 🚀 الخطوات السريعة (بعد الخروج من Shell)

### 1️⃣ إنشاء Tenant

```powershell
docker-compose exec web python /app/create_test_tenant.py
```

### 2️⃣ إجراء Migrations

```powershell
docker-compose exec web python manage.py migrate_schemas
```

### 3️⃣ تشغيل Frontend (في terminal جديد)

```powershell
cd frontend
npm run dev
```

### 4️⃣ إضافة Domain إلى hosts

افتح Notepad **كمسؤول** وافتح:
```
C:\Windows\System32\drivers\etc\hosts
```

أضف هذا السطر:
```
127.0.0.1    farm1.localhost
```

احفظ الملف.

---

## 🌐 الوصول

- **Frontend:** `http://localhost:5173`
- **API Docs:** `http://farm1.localhost:8000/api/docs`
- **Admin:** `http://farm1.localhost:8000/admin/`

**تسجيل الدخول:**
- اسم المستخدم: `admin`
- كلمة المرور: `Admin123!`

---

## 📚 المزيد من التفاصيل

- `FINAL_TESTING_STEPS.md` - دليل شامل
- `RUN_TEST.md` - خطوات مفصلة

---

**ابدأ بالخروج من Python Shell أولاً! 🚀**

