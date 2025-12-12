# AquaERP: خطة التنفيذ العملية الشاملة

**النسخة:** 1.0  
**التاريخ:** ديسمبر 2025  
**الحالة:** قابلة للتنفيذ الفوري  
**الهدف:** تحويل خارطة الطريق إلى خطة عملية قابلة للتنفيذ خطوة بخطوة

---

## 📊 تحليل الوضع الحالي

### ✅ ما تم إنجازه

1. **البنية التحتية الأساسية:**
   - ✅ Docker Compose مع PostgreSQL 16
   - ✅ Dockerfile للإنتاج
   - ✅ إعدادات Django Multi-tenancy (django-tenants)
   - ✅ نماذج Client و Domain الأساسية
   - ✅ هيكلية المجلدات الأساسية

### ⚠️ ما يحتاج إلى إكمال

1. **ملفات Django الأساسية:**
   - ❌ `manage.py`
   - ❌ `wsgi.py` و `asgi.py`
   - ❌ `urls.py` الرئيسي
   - ❌ ملفات `apps.py` للتطبيقات

2. **الإعدادات المطلوبة:**
   - ❌ إعدادات البيئة (.env)
   - ❌ Redis في docker-compose
   - ❌ Celery Worker
   - ❌ إعدادات Django Ninja

3. **المكتبات المطلوبة:**
   - ❌ مكتبات المصادقة (JWT)
   - ❌ مكتبات ZATCA
   - ❌ مكتبات المحاسبة
   - ❌ مكتبات PDF والطباعة

---

## 🎯 خطة التنفيذ الشاملة (60 يوم عمل)

### **المرحلة 0: الإعداد الأولي والإصلاحات (Pre-Sprint)**

**المدة:** 2-3 أيام  
**الهدف:** إكمال البنية الأساسية وإصلاح الملفات الناقصة

---

## 📅 Sprint 1: التأسيس والبنية التحتية (Foundation & Tenants)

**المدة:** أسبوعين (10 أيام عمل)  
**الهدف:** بيئة عمل جاهزة، نظام تسجيل دخول، وعزل الشركات (Tenants)

### **اليوم 1-2: إعداد البيئة والبنية الأساسية**

#### المهام التفصيلية

**1.1 إكمال هيكلية Django:**

```python
# إنشاء manage.py
# إنشاء wsgi.py و asgi.py
# إنشاء urls.py الرئيسي
# إنشاء apps.py للتطبيقات
```

**1.2 إعداد Docker Compose الكامل:**

- ✅ إضافة Redis service
- ✅ إضافة Celery Worker service
- ✅ إضافة Celery Beat service (للمهام المجدولة)
- ✅ إعداد متغيرات البيئة

**1.3 تحديث requirements.txt:**

```
Django>=5.0,<5.1
django-tenants>=3.6.0
psycopg2-binary>=2.9.9
django-ninja>=1.1.0
gunicorn>=21.2.0
celery>=5.3.0
redis>=5.0.0
djangorestframework-simplejwt>=5.3.0
python-dotenv>=1.0.0
django-cors-headers>=4.3.0
```

**1.4 إعداد ملف .env.example:**

```
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgresql://aqua_admin:secure_pass_123@db:5432/aqua_erp_db
REDIS_URL=redis://redis:6379/0
ALLOWED_HOSTS=localhost,127.0.0.1
```

#### المخرجات

- [ ] `manage.py` موجود ويعمل
- [ ] `wsgi.py` و `asgi.py` جاهزان
- [ ] Docker Compose يشغل جميع الخدمات بنجاح
- [ ] قاعدة البيانات متصلة

---

### **اليوم 3: إعداد PostgreSQL و Redis و Tenant Schemas**

#### المهام التفصيلية

**3.1 إعداد PostgreSQL:**

- [ ] التحقق من اتصال قاعدة البيانات
- [ ] إنشاء Public Schema يدوياً إذا لزم الأمر
- [ ] إعداد PostGIS إذا كان مطلوباً للخرائط المستقبلية

**3.2 إعداد Redis:**

- [ ] التحقق من اتصال Redis
- [ ] اختبار تخزين واسترجاع البيانات

**3.3 تكوين Tenant Schemas:**

- [ ] إنشاء سكريبت لإعداد Public Schema
- [ ] اختبار إنشاء Tenant جديد
- [ ] التحقق من عزل البيانات

#### المخرجات

- [ ] جميع الخدمات تعمل في Docker
- [ ] يمكن إنشاء Tenant جديد بنجاح
- [ ] البيانات معزولة بشكل صحيح

#### الكود المطلوب

**إنشاء: `scripts/setup_public_schema.py`**

```python
"""
سكريبت لإعداد Public Schema
"""
from django.core.management import execute_from_command_line
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aqua_core.settings')
django.setup()

from django_tenants.utils import schema_context
from django.db import connection

def setup_public_schema():
    with schema_context('public'):
        # إنشاء جداول Public Schema
        from django.core.management import call_command
        call_command('migrate', schema_name='public')
    print("✅ Public Schema تم إعداده بنجاح")

if __name__ == '__main__':
    setup_public_schema()
```

---

### **اليوم 4: تحسين نماذج Client و Domain + Tenant Provisioning**

#### المهام التفصيلية

**4.1 تحسين نموذج Client:**

- [ ] إضافة حقول إضافية (رقم السجل التجاري، البريد الإلكتروني، الهاتف)
- [ ] إضافة حقول الاشتراك (نوع الاشتراك، تاريخ الانتهاء)
- [ ] إضافة Soft Delete

**4.2 تحسين نموذج Domain:**

- [ ] إصلاح خطأ في `__str__` method
- [ ] إضافة التحقق من صحة النطاق

**4.3 إنشاء سكريبت Tenant Provisioning:**

- [ ] سكريبت لإنشاء Tenant جديد
- [ ] إنشاء Domain افتراضي
- [ ] إنشاء مستخدم Admin افتراضي

#### المخرجات

- [ ] نماذج Client و Domain محسنة
- [ ] سكريبت `create_tenant.py` جاهز
- [ ] يمكن إنشاء Tenant جديد بسهولة

#### الكود المطلوب

**تحديث: `tenants/models.py`**

```python
from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
from django.core.validators import EmailValidator

class Client(TenantMixin):
    name = models.CharField(max_length=200, verbose_name="اسم الشركة")
    trade_number = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="رقم السجل التجاري")
    email = models.EmailField(validators=[EmailValidator()], verbose_name="البريد الإلكتروني")
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name="الهاتف")
    
    # معلومات الاشتراك
    subscription_type = models.CharField(
        max_length=20,
        choices=[
            ('trial', 'تجريبي'),
            ('basic', 'أساسي'),
            ('professional', 'احترافي'),
            ('enterprise', 'مؤسسي')
        ],
        default='trial',
        verbose_name="نوع الاشتراك"
    )
    subscription_start = models.DateField(auto_now_add=True, verbose_name="تاريخ بدء الاشتراك")
    subscription_end = models.DateField(null=True, blank=True, verbose_name="تاريخ انتهاء الاشتراك")
    
    on_trial = models.BooleanField(default=True, verbose_name="في فترة تجريبية")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    
    created_on = models.DateField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_on = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    
    auto_create_schema = True
    auto_drop_schema = False  # لا نحذف Schema تلقائياً (Soft Delete)
    
    class Meta:
        verbose_name = "عميل"
        verbose_name_plural = "العملاء"
    
    def __str__(self):
        return self.name

class Domain(DomainMixin):
    def __str__(self):
        return self.domain
```

**إنشاء: `tenants/management/commands/create_tenant.py`**

```python
from django.core.management.base import BaseCommand
from tenants.models import Client, Domain
from django.contrib.auth import get_user_model
import secrets

User = get_user_model()

class Command(BaseCommand):
    help = 'إنشاء Tenant جديد مع Domain ومستخدم Admin'

    def add_arguments(self, parser):
        parser.add_argument('--name', type=str, required=True, help='اسم الشركة')
        parser.add_argument('--domain', type=str, required=True, help='النطاق (مثال: farm1)')
        parser.add_argument('--email', type=str, required=True, help='البريد الإلكتروني')
        parser.add_argument('--admin-username', type=str, required=True, help='اسم مستخدم Admin')
        parser.add_argument('--admin-email', type=str, required=True, help='بريد Admin')
        parser.add_argument('--admin-password', type=str, help='كلمة مرور Admin (إذا لم يتم تحديدها سيتم توليد واحدة)')

    def handle(self, *args, **options):
        name = options['name']
        domain_name = options['domain']
        email = options['email']
        admin_username = options['admin_username']
        admin_email = options['admin_email']
        admin_password = options.get('admin_password') or secrets.token_urlsafe(12)

        # إنشاء Client (Tenant)
        tenant = Client(
            name=name,
            email=email,
            schema_name=domain_name.lower().replace('-', '_').replace('.', '_')
        )
        tenant.save()

        # إنشاء Domain
        domain = Domain()
        domain.domain = f"{domain_name}.localhost"  # للتطوير
        domain.tenant = tenant
        domain.is_primary = True
        domain.save()

        # إنشاء مستخدم Admin في Schema الخاص بالعميل
        with tenant.schema_context():
            admin_user = User.objects.create_user(
                username=admin_username,
                email=admin_email,
                password=admin_password,
                is_staff=True,
                is_superuser=True
            )
            admin_user.save()

        self.stdout.write(
            self.style.SUCCESS(
                f'✅ تم إنشاء Tenant "{name}" بنجاح!\n'
                f'   النطاق: {domain.domain}\n'
                f'   اسم المستخدم: {admin_username}\n'
                f'   كلمة المرور: {admin_password}'
            )
        )
```

---

### **اليوم 5: نظام المصادقة (Custom User Model + JWT)**

#### المهام التفصيلية

**5.1 إنشاء Custom User Model:**

- [ ] إنشاء تطبيق `accounts` أو `users`
- [ ] إنشاء نموذج User مخصص
- [ ] إضافة حقول إضافية (اسم كامل، رقم الهاتف، الدور)

**5.2 إعداد JWT Authentication:**

- [ ] تثبيت `djangorestframework-simplejwt`
- [ ] إعداد URLs للـ JWT
- [ ] إنشاء Endpoints (Login, Refresh, Verify)

**5.3 إنشاء Permissions System:**

- [ ] تحديد الأدوار (Roles): Owner, Manager, Accountant, Worker
- [ ] إنشاء Permissions مخصصة

#### المخرجات

- [ ] Custom User Model جاهز
- [ ] JWT Authentication يعمل
- [ ] نظام Permissions أساسي جاهز

#### الكود المطلوب

**إنشاء: `accounts/models.py`**

```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('owner', 'مالك'),
        ('manager', 'مدير'),
        ('accountant', 'محاسب'),
        ('worker', 'عامل'),
        ('viewer', 'مشاهد'),
    ]
    
    full_name = models.CharField(max_length=255, verbose_name="الاسم الكامل")
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name="الهاتف")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='worker', verbose_name="الدور")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    
    class Meta:
        verbose_name = "مستخدم"
        verbose_name_plural = "المستخدمون"
    
    def __str__(self):
        return f"{self.full_name} ({self.username})"
```

**تحديث: `tenants/aqua_core/settings.py`**

```python
# إضافة في INSTALLED_APPS
'accounts',  # تطبيق المستخدمين

# إضافة في نهاية الملف
AUTH_USER_MODEL = 'accounts.User'

# إعدادات JWT
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# CORS Settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_CREDENTIALS = True
```

---

### **اليوم 6: إعداد الهيكل الأساسي للواجهة الأمامية (React + Vite + Tailwind)**

#### المهام التفصيلية

**6.1 إنشاء مشروع React:**

```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
```

**6.2 تثبيت المكتبات المطلوبة:**

```bash
npm install axios react-router-dom
npm install -D tailwindcss postcss autoprefixer
npm install -D @types/react @types/react-dom
```

**6.3 إعداد Tailwind CSS:**

- [ ] تهيئة Tailwind
- [ ] إعداد RTL Support
- [ ] إعداد الخطوط (Cairo font)

**6.4 إنشاء الهيكل الأساسي:**

```
frontend/
├── src/
│   ├── components/
│   │   ├── auth/
│   │   │   └── LoginForm.tsx
│   │   └── layout/
│   │       └── Layout.tsx
│   ├── pages/
│   │   ├── Login.tsx
│   │   └── Dashboard.tsx
│   ├── services/
│   │   └── api.ts
│   ├── utils/
│   │   └── auth.ts
│   └── App.tsx
```

**6.5 ربط صفحة تسجيل الدخول:**

- [ ] إنشاء Login Form
- [ ] ربط مع Backend API
- [ ] حفظ Token في localStorage
- [ ] Redirect بعد تسجيل الدخول

#### المخرجات

- [ ] مشروع React جاهز
- [ ] Tailwind CSS مع RTL يعمل
- [ ] صفحة تسجيل الدخول متصلة بالـ Backend

---

### **اليوم 7-8: إعداد Django Ninja API + Endpoints أساسية**

#### المهام التفصيلية

**7.1 إعداد Django Ninja:**

- [ ] إنشاء ملف `api/router.py`
- [ ] إعداد Authentication للـ API
- [ ] إنشاء Schema باستخدام Pydantic

**7.2 إنشاء API Endpoints:**

- [ ] `/api/auth/login` - تسجيل الدخول
- [ ] `/api/auth/refresh` - تجديد Token
- [ ] `/api/auth/me` - معلومات المستخدم الحالي
- [ ] `/api/health` - فحص حالة النظام

#### المخرجات

- [ ] Django Ninja يعمل
- [ ] Endpoints الأساسية جاهزة ومختبرة

---

### **اليوم 9-10: اختبارات ومراجعة Sprint 1**

#### المهام

- [ ] كتابة Unit Tests للـ Models
- [ ] كتابة Integration Tests للـ API
- [ ] اختبار Multi-tenancy بشكل كامل
- [ ] مراجعة الكود وتنظيمه
- [ ] توثيق ما تم إنجازه

---

## 📅 Sprint 2: النواة البيولوجية (The Biological Engine)

**المدة:** أسبوعان (10 أيام عمل)  
**الهدف:** القدرة على إنشاء مزرعة، أحواض، وإضافة زريعة

### **اليوم 11: تصميم نماذج Species و Lifecycle Stages**

#### المهام

- [ ] إنشاء تطبيق `biological`
- [ ] نموذج `Species` (الأنواع السمكية)
- [ ] نموذج `LifecycleStage` (مراحل النمو)
- [ ] Migrations

### **اليوم 12: وحدة Farm Structure (الأحواض/الأقفاص)**

#### المهام

- [ ] نموذج `Pond` أو `Tank`
- [ ] نموذج `FarmLocation` (موقع المزرعة)
- [ ] API للـ CRUD
- [ ] واجهة React لإدارة الأحواض

### **اليوم 13: وحدة Batch Management**

#### المهام

- [ ] نموذج `Batch` (الدفعة)
- [ ] ربط مع Species و Pond
- [ ] حساب التكلفة الأولية
- [ ] API للإدارة

### **اليوم 14: واجهة المستخدم للمزرعة**

#### المهام

- [ ] خريطة تفاعلية للأحواض (بسيطة)
- [ ] Forms لإدخال البيانات
- [ ] عرض البيانات البيولوجية

### **اليوم 15: اختبارات**

#### المهام

- [ ] Unit Tests
- [ ] Integration Tests
- [ ] اختبار عزل البيانات

---

## 📅 Sprint 3: العمليات اليومية (Daily Operations & FCR)

**المدة:** أسبوعان (10 أيام عمل)  
**الهدف:** تسجيل ما يحدث في المزرعة يومياً

### **اليوم 16: وحدة Inventory (مخزون الأعلاف)**

#### المهام

- [ ] نموذج `FeedType` (نوع العلف)
- [ ] نموذج `FeedInventory` (مخزون العلف)
- [ ] نموذج `Medicine` (الأدوية)
- [ ] API لإدارة المخزون

### **اليوم 17: وحدة Feeding Log**

#### المهام

- [ ] نموذج `FeedingLog`
- [ ] خوارزمية خصم من المخزون
- [ ] توزيع التكلفة على الدفعة
- [ ] API للتسجيل

### **اليوم 18: وحدة Mortality Log**

#### المهام

- [ ] نموذج `MortalityLog`
- [ ] تحديث العدد الحي تلقائياً
- [ ] API للتسجيل

### **اليوم 19: Biological Calculator (FCR & Biomass)**

#### المهام

- [ ] دالة حساب FCR
- [ ] دالة حساب Estimated Biomass
- [ ] جداول النمو المعيارية
- [ ] API للتقارير

### **اليوم 20: واجهات React للعمليات اليومية**

#### المهام

- [ ] Mobile-First Design
- [ ] Forms لتسجيل العلف
- [ ] Forms لتسجيل النفوق
- [ ] Dashboard للعمليات

---

## 📅 Sprint 4: المحاسبة الأساسية (Core Accounting)

**المدة:** أسبوعان (10 أيام عمل)  
**الهدف:** نظام محاسبي Double Entry

### **اليوم 21: Chart of Accounts**

#### المهام

- [ ] إنشاء تطبيق `accounting`
- [ ] نموذج `Account` (الحساب)
- [ ] دليل الحسابات الموحد
- [ ] فئات الحسابات (أصول، خصوم، إيرادات، مصروفات)

### **اليوم 22: Journal Entry Model**

#### المهام

- [ ] نموذج `JournalEntry`
- [ ] نموذج `JournalEntryLine`
- [ ] التحقق من التوازن (Debit = Credit)
- [ ] API للقيود

### **اليوم 23-24: الربط الآلي (Automation Signals)**

#### المهام

- [ ] Signal عند تسجيل علف
- [ ] Signal عند تسجيل نفوق
- [ ] Signal عند الحصاد
- [ ] Signal عند المبيعات

### **اليوم 25: تقارير مالية أساسية**

#### المهام

- [ ] Trial Balance Report
- [ ] Balance Sheet
- [ ] Income Statement
- [ ] API للتقارير

---

## 📅 Sprint 5: المبيعات والامتثال (Sales & ZATCA)

**المدة:** أسبوعان (10 أيام عمل)  
**الهدف:** بيع السمك وإصدار فاتورة قانونية

### **اليوم 26: وحدة Harvesting (الحصاد)**

#### المهام

- [ ] نموذج `Harvest`
- [ ] تحويل الأصل البيولوجي إلى Finished Goods
- [ ] حساب القيمة العادلة
- [ ] API للحصاد

### **اليوم 27: وحدة Sales Order و Invoices**

#### المهام

- [ ] نموذج `SalesOrder`
- [ ] نموذج `Invoice`
- [ ] نموذج `InvoiceLine`
- [ ] API للمبيعات

### **اليوم 28-29: تكامل ZATCA**

#### المهام

- [ ] توليد QR Code (TLV Format)
- [ ] إنشاء ملفات XML (UBL 2.1)
- [ ] إعداد CSR
- [ ] التوقيع الإلكتروني (ECDSA)
- [ ] الاختبار مع ZATCA Sandbox

### **اليوم 30: واجهة الفوترة و PDF**

#### المهام

- [ ] تصميم الفاتورة الضريبية
- [ ] تصدير PDF (ReportLab أو WeasyPrint)
- [ ] عرض الفاتورة في الواجهة
- [ ] طباعة الفاتورة

---

## 📅 Sprint 6: واجهة المستخدم والتقارير (UI Polish & Dashboards)

**المدة:** أسبوعان (10 أيام عمل)  
**الهدف:** جعل النظام جميلاً وقابلاً للاستخدام

### **اليوم 31: Dashboard الرئيسية**

#### المهام

- [ ] Widgets (نسبة النفوق، تكلفة الكيلو)
- [ ] Charts و Graphs
- [ ] التنبيهات
- [ ] آخر الأنشطة

### **اليوم 32: تحسين UX**

#### المهام

- [ ] Validations في Forms
- [ ] Error Messages بالعربية
- [ ] Loading States
- [ ] Success Messages

### **اليوم 33: الترجمة (i18n)**

#### المهام

- [ ] إعداد i18n في Frontend
- [ ] إعداد i18n في Backend
- [ ] محاذاة RTL كاملة
- [ ] دعم اللغة الإنجليزية

### **اليوم 34: تقارير الأداء**

#### المهام

- [ ] Cost per Kg Report
- [ ] Batch Profitability Analysis
- [ ] Feed Efficiency Report
- [ ] Mortality Analysis

### **اليوم 35: مراجعة أمنية**

#### المهام

- [ ] مراجعة Permissions
- [ ] فحص Data Leakage
- [ ] اختبارات الأمان
- [ ] توثيق الأمان

---

## 🔧 المتطلبات التقنية الإضافية

### **مكتبات Python المطلوبة:**

```txt
# Core
Django>=5.0,<5.1
django-tenants>=3.6.0
psycopg2-binary>=2.9.9
django-ninja>=1.1.0
gunicorn>=21.2.0

# Authentication
djangorestframework-simplejwt>=5.3.0
django-cors-headers>=4.3.0

# Async Tasks
celery>=5.3.0
redis>=5.0.0
django-celery-beat>=2.5.0

# Environment
python-dotenv>=1.0.0

# Accounting
django-money>=3.3.0

# PDF & Reports
reportlab>=4.0.0
weasyprint>=60.0

# ZATCA Integration
cryptography>=41.0.0
qrcode>=7.4.0
xmltodict>=0.13.0

# Validation
pydantic>=2.5.0

# Testing
pytest>=7.4.0
pytest-django>=4.7.0
pytest-cov>=4.1.0

# Code Quality
black>=23.11.0
flake8>=6.1.0
mypy>=1.7.0
```

### **مكتبات Frontend المطلوبة:**

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.0",
    "zustand": "^4.4.0",
    "react-query": "^3.39.0",
    "recharts": "^2.10.0",
    "date-fns": "^2.30.0",
    "react-hook-form": "^7.48.0",
    "zod": "^3.22.0",
    "@hookform/resolvers": "^3.3.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "tailwindcss": "^3.3.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "@vitejs/plugin-react": "^4.2.0"
  }
}
```

---

## 📋 قوالب الملفات المطلوبة

### **1. ملف manage.py**

```python
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aqua_core.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
```

### **2. ملف wsgi.py**

```python
"""
WSGI config for AquaERP project.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aqua_core.settings')

application = get_wsgi_application()
```

### **3. ملف urls.py الرئيسي**

```python
from django.contrib import admin
from django.urls import path, include
from django_tenants.utils import schema_context

urlpatterns = [
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),
]
```

---

## 🎯 معايير الجودة والاختبار

### **1. الاختبارات المطلوبة:**

- ✅ Unit Tests (Coverage > 80%)
- ✅ Integration Tests
- ✅ API Tests
- ✅ Multi-tenancy Tests
- ✅ Security Tests

### **2. مراجعة الكود:**

- ✅ استخدام Black للتنظيم
- ✅ استخدام Flake8 للتحقق
- ✅ Type Hints في Python
- ✅ TypeScript في Frontend

### **3. التوثيق:**

- ✅ Docstrings لجميع الوظائف
- ✅ README.md شامل
- ✅ API Documentation
- ✅ User Guide

---

## 🔐 متطلبات الأمان

1. **حماية البيانات:**
   - تشفير البيانات الحساسة
   - HTTPS في الإنتاج
   - Secure Cookies

2. **مفاتيح ZATCA:**
   - تخزين في Vault أو Environment Variables
   - عدم تخزين في قاعدة البيانات

3. **الصلاحيات:**
   - Role-Based Access Control (RBAC)
   - Audit Log للعمليات المهمة

4. **الحماية من الهجمات:**
   - CSRF Protection
   - SQL Injection Prevention
   - XSS Protection

---

## 📊 معايير الأداء

1. **الاستجابة:**
   - API Response Time < 200ms
   - Page Load Time < 2s

2. **قاعدة البيانات:**
   - Indexes على الحقول المهمة
   - Query Optimization
   - Connection Pooling

3. **المهام الخلفية:**
   - استخدام Celery للمهام الثقيلة
   - Caching باستخدام Redis

---

## 🚀 خطة النشر (Deployment)

### **المرحلة 1: التطوير (Development)**

- Docker Compose محلي
- قاعدة بيانات محلية
- Frontend Development Server

### **المرحلة 2: الاختبار (Staging)**

- Docker Containers
- قاعدة بيانات منفصلة
- CI/CD Pipeline

### **المرحلة 3: الإنتاج (Production)**

- Kubernetes Cluster
- PostgreSQL Cluster
- Redis Cluster
- Load Balancer
- CDN للـ Static Files

---

## 📝 ملاحظات التنفيذ الصارمة

1. **Soft Delete فقط:**
   - جميع البيانات المالية لا تُحذف
   - استخدام `is_active=False`
   - قيود عكسية للبيانات المالية

2. **معيار IAS 41:**
   - إعادة تقييم شهري للأسماك
   - حساب القيمة العادلة
   - تسجيل الربح/الخسارة غير المحققة

3. **الأداء:**
   - المهام الثقيلة في Celery فقط
   - لا توجد حسابات معقدة في Request/Response

4. **التوافق مع ZATCA:**
   - اتباع معايير Phase 2 بدقة
   - الاختبار مع Sandbox أولاً
   - التوثيق الكامل للعملية

---

## ✅ قائمة التحقق النهائية

### **Sprint 1:**

- [ ] Docker Compose يعمل بشكل كامل
- [ ] يمكن إنشاء Tenant جديد
- [ ] نظام تسجيل الدخول يعمل
- [ ] JWT Authentication جاهز
- [ ] Frontend متصل بالـ Backend
- [ ] جميع الاختبارات تمر

### **Sprint 2:**

- [ ] يمكن إنشاء أنواع سمكية
- [ ] يمكن إنشاء أحواض
- [ ] يمكن إضافة دفعات
- [ ] البيانات معزولة بشكل صحيح

### **Sprint 3:**

- [ ] يمكن تسجيل العلف
- [ ] يمكن تسجيل النفوق
- [ ] FCR Calculator يعمل
- [ ] الواجهات Mobile-Friendly

### **Sprint 4:**

- [ ] نظام Double Entry يعمل
- [ ] القيود الآلية تعمل
- [ ] التقارير المالية جاهزة

### **Sprint 5:**

- [ ] يمكن الحصاد
- [ ] يمكن إصدار فواتير
- [ ] ZATCA Integration يعمل
- [ ] PDF Export جاهز

### **Sprint 6:**

- [ ] Dashboard جميل ووظيفي
- [ ] جميع الواجهات محسنة
- [ ] RTL كامل
- [ ] مراجعة أمنية مكتملة

---

**نهاية خطة التنفيذ**
