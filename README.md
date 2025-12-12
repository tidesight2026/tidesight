# AquaERP - نظام ERP للمزارع السمكية

نظام ERP سحابي (SaaS) متخصص في إدارة المزارع السمكية، متوافق مع معايير ZATCA و SOCPA.

## 📋 المميزات الرئيسية

- ✅ **Multi-Tenancy**: عزل كامل للبيانات لكل عميل (Schema-based)
- ✅ **النواة البيولوجية**: إدارة الأنواع، الدفعات، والأحواض
- ✅ **العمليات اليومية**: تسجيل العلف، النفوق، وحساب FCR
- ✅ **نظام محاسبي**: Double-Entry Bookkeeping مع معيار IAS 41
- ✅ **تكامل ZATCA**: إصدار فواتير ضريبية متوافقة
- ✅ **واجهة حديثة**: React + TypeScript + Tailwind CSS

## 🛠️ المكدس التقني

### Backend
- Python 3.11+
- Django 5.0
- Django Ninja (API Framework)
- PostgreSQL 16
- Celery + Redis (Async Tasks)
- django-tenants (Multi-tenancy)

### Frontend
- React 18
- TypeScript
- Tailwind CSS
- Vite

### Infrastructure
- Docker & Docker Compose
- Gunicorn (Production)

## 🚀 البدء السريع

### المتطلبات الأساسية
- Docker & Docker Compose
- Git

### الخطوات

1. **استنساخ المشروع**
```bash
git clone <repository-url>
cd AquaERP
```

2. **إنشاء ملف .env**
```bash
cp env.example .env
# تعديل القيم حسب الحاجة
```

3. **تشغيل المشروع**
```bash
docker-compose up -d
```

4. **إجراء Migrations**
```bash
docker-compose exec web python manage.py migrate_schemas --shared
docker-compose exec web python manage.py migrate_schemas
```

5. **إنشاء Tenant جديد**
```bash
docker-compose exec web python manage.py create_tenant \
  --name "مزرعة تجريبية" \
  --domain "farm1" \
  --email "farm@example.com" \
  --admin-username "admin" \
  --admin-email "admin@example.com" \
  --admin-password "your-secure-password"
```

6. **الوصول إلى النظام**
- لوحة التحكم: http://farm1.localhost:8000/admin/
- API: http://farm1.localhost:8000/api/

## 📁 هيكل المشروع

```
AquaERP/
├── docker-compose.yml          # إعدادات Docker
├── Dockerfile                  # صورة Docker
├── requirements.txt            # مكتبات Python
├── manage.py                   # Django management
├── tenants/                    # التطبيقات الرئيسية
│   ├── models.py              # نماذج Client و Domain
│   ├── aqua_core/             # إعدادات Django
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── celery.py
│   └── management/
│       └── commands/
│           └── create_tenant.py
└── [التطبيقات الأخرى ستُضاف لاحقاً]
```

## 🔧 الأوامر المفيدة

### إدارة Docker
```bash
# تشغيل المشروع
docker-compose up -d

# إيقاف المشروع
docker-compose down

# عرض السجلات
docker-compose logs -f web

# الدخول إلى Container
docker-compose exec web bash
```

### إدارة قاعدة البيانات
```bash
# Migrations للـ Public Schema
docker-compose exec web python manage.py migrate_schemas --shared

# Migrations لجميع Tenants
docker-compose exec web python manage.py migrate_schemas

# إنشاء Superuser (للـ Public Schema)
docker-compose exec web python manage.py createsuperuser
```

### إدارة Tenants
```bash
# إنشاء Tenant جديد
docker-compose exec web python manage.py create_tenant ...

# عرض قائمة Tenants
docker-compose exec web python manage.py list_tenants
```

## 📚 الوثائق

- [خطة التنفيذ الشاملة](AquaERP_Implementation_Plan.md)
- [تحليل الوضع الحالي](AquaERP_Current_State_Analysis.md)
- [دليل البدء السريع](QUICK_START_GUIDE.md)
- [خارطة الطريق الأصلية](AquaERP_Roadmap_Execution.md)

## 🗺️ خارطة الطريق

المشروع مقسم إلى 6 Sprints:

- **Sprint 1** (10 أيام): التأسيس والبنية التحتية ✅
- **Sprint 2** (10 أيام): النواة البيولوجية
- **Sprint 3** (10 أيام): العمليات اليومية
- **Sprint 4** (10 أيام): المحاسبة الأساسية
- **Sprint 5** (10 أيام): المبيعات وZATCA
- **Sprint 6** (10 أيام): واجهة المستخدم والتقارير

## 🔐 الأمان

- استخدم كلمات مرور قوية في الإنتاج
- غيّر SECRET_KEY في ملف .env
- فعّل HTTPS في الإنتاج
- راجع إعدادات CORS قبل النشر

## 📝 الترخيص

[أضف معلومات الترخيص هنا]

## 👥 المساهمون

[أضف معلومات المساهمين هنا]

## 📧 التواصل

[أضف معلومات التواصل هنا]

---

**تم التطوير بواسطة فريق AquaERP** 🐟

