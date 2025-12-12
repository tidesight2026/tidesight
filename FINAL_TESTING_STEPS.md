# 🎯 الخطوات النهائية للاختبار - AquaERP

**التاريخ:** ديسمبر 2025

---

## ⚠️ مهم: أنت داخل Python Shell!

إذا كنت داخل Python shell (ترى `>>>`)، اخرج أولاً:

```
>>> exit()
```

أو اضغط `Ctrl+D` أو `Ctrl+Z` ثم Enter

---

## 🚀 الخطوات الكاملة

### الخطوة 1: إنشاء Tenant تجريبي

من PowerShell في المجلد الرئيسي `D:\AquaERP`:

```powershell
docker-compose exec web python /app/create_test_tenant.py
```

إذا لم يعمل، استخدم:

```powershell
docker-compose exec -T web python manage.py shell < create_tenant_commands.py
```

---

### الخطوة 2: إجراء Migrations للـ Tenant Schema

```powershell
docker-compose exec web python manage.py migrate_schemas
```

---

### الخطوة 3: تشغيل Frontend

**افتح terminal جديد** (لا تغلق الأول):

```powershell
cd D:\AquaERP\frontend
npm run dev
```

---

### الخطوة 4: إضافة Domain إلى hosts (مهم!)

#### Windows:

1. افتح Notepad كـ Administrator
2. افتح: `C:\Windows\System32\drivers\etc\hosts`
3. أضف هذا السطر:

```
127.0.0.1    farm1.localhost
```

4. احفظ الملف

#### Linux/Mac:

```bash
sudo echo "127.0.0.1    farm1.localhost" >> /etc/hosts
```

---

### الخطوة 5: الوصول والاختبار

1. **Frontend:**
   - افتح: `http://localhost:5173`
   - يجب أن ترى صفحة Login

2. **Backend API:**
   - افتح: `http://farm1.localhost:8000/api/docs`
   - يجب أن ترى Swagger UI

3. **Admin Panel:**
   - افتح: `http://farm1.localhost:8000/admin/`
   - سجل دخول:
     - **اسم المستخدم:** `admin`
     - **كلمة المرور:** `Admin123!`

---

## 📋 بيانات تسجيل الدخول

- **اسم المستخدم:** `admin`
- **كلمة المرور:** `Admin123!`
- **Domain:** `farm1.localhost`

---

## ✅ قائمة التحقق

- [ ] خرجت من Python shell
- [ ] أنشأت Tenant
- [ ] أجريت Migrations للـ Tenant
- [ ] أضفت Domain إلى hosts
- [ ] شغلت Frontend
- [ ] فتحت Frontend في المتصفح
- [ ] جربت تسجيل الدخول

---

## 🐛 حل المشاكل

### المشكلة: Tenant موجود بالفعل

```powershell
# حذف Tenant القديم وإعادة إنشائه
docker-compose exec web python manage.py shell
```

ثم في Shell:

```python
from tenants.models import Client
Client.objects.filter(schema_name='farm1').delete()
exit()
```

ثم أنشئ Tenant مرة أخرى.

### المشكلة: Frontend لا يتصل بالـ Backend

- تحقق من أن Backend يعمل: `docker-compose ps`
- تحقق من CORS settings في `settings.py`
- تأكد من إضافة Domain إلى hosts

---

## 📞 المساعدة

راجع:
- `RUN_TEST.md` - دليل الاختبار الكامل
- `QUICK_TEST_COMMANDS.md` - أوامر سريعة
- `TEST_GUIDE.md` - دليل حل المشاكل

---

**جاهز للاختبار! اتبع الخطوات أعلاه! 🚀**

---

**تاريخ الإنشاء:** ديسمبر 2025

