# 🚀 ابدأ من هنا - AquaERP

دليل سريع للبدء في المشروع خطوة بخطوة.

---

## ✅ الخطوة 1: إنشاء ملف .env

قم بتشغيل السكريبت المساعد:

```bash
python setup_env.py
```

أو نسخ يدوي:

```bash
copy env.example .env
```

ثم عدّل `SECRET_KEY` في ملف `.env` إلى قيمة آمنة.

---

## ✅ الخطوة 2: تشغيل المشروع

```bash
# بناء الصور
docker-compose build

# تشغيل الخدمات
docker-compose up -d

# عرض السجلات
docker-compose logs -f
```

---

## ✅ الخطوة 3: إعداد قاعدة البيانات

```bash
# Migrations للـ Public Schema
docker-compose exec web python manage.py migrate_schemas --shared

# Migrations لجميع Tenants
docker-compose exec web python manage.py migrate_schemas
```

---

## ✅ الخطوة 4: إنشاء Tenant تجريبي

```bash
docker-compose exec web python manage.py create_tenant \
  --name "مزرعة تجريبية" \
  --domain "farm1" \
  --email "test@example.com" \
  --admin-username "admin" \
  --admin-email "admin@example.com" \
  --admin-password "Admin123!"
```

---

## ✅ الخطوة 5: الوصول إلى النظام

**لوحة التحكم:**

- <http://farm1.localhost:8000/admin/>

**ملاحظة:** قد تحتاج لإضافة `127.0.0.1 farm1.localhost` في ملف hosts.

---

## 📚 الوثائق المفيدة

- 📖 [دليل الاختبار](TEST_SETUP.md) - اختبار جميع المكونات
- 📖 [دليل البدء السريع](QUICK_START_GUIDE.md) - خطوات مفصلة
- 📖 [خطة التنفيذ](AquaERP_Implementation_Plan.md) - خطة المشروع الكاملة
- 📖 [README](README.md) - معلومات عامة

---

## ⚠️ استكشاف الأخطاء

إذا واجهت مشاكل:

1. تحقق من السجلات: `docker-compose logs`
2. راجع [دليل الاختبار](TEST_SETUP.md) لحل المشاكل
3. تأكد من أن جميع الخدمات تعمل: `docker-compose ps`

---

**🎉 الآن جاهز للبدء في Sprint 1!**

راجع `AquaERP_Implementation_Plan.md` للخطة التفصيلية.
