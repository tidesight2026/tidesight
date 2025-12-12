# ⚡ أوامر سريعة للاختبار - AquaERP

**التاريخ:** ديسمبر 2025

---

## 🚀 الخطوات السريعة (Copy & Paste)

### 1. إنشاء Tenant (من PowerShell في المجلد الرئيسي)

```powershell
# إنشاء Tenant باستخدام Python script
docker-compose exec web python /app/create_test_tenant.py
```

إذا لم يعمل، استخدم هذه الطريقة:

```powershell
# طريقة بديلة - استخدام Django shell
docker-compose exec -T web python manage.py shell < create_tenant_commands.py
```

---

### 2. إجراء Migrations للـ Tenant

```powershell
docker-compose exec web python manage.py migrate_schemas
```

---

### 3. تشغيل Frontend (في terminal جديد)

```powershell
cd frontend
npm run dev
```

---

## 📋 إنشاء ملف create_tenant_commands.py

أنشئ ملف `create_tenant_commands.py`:

```python
from django_tenants.utils import tenant_context
from tenants.models import Client, Domain
from django.contrib.auth import get_user_model

User = get_user_model()

# إنشاء Tenant
tenant = Client.objects.create(
    name="مزرعة تجريبية",
    email="test@example.com",
    schema_name="farm1",
    subscription_type='trial',
    is_active=True,
)
print(f'✅ تم إنشاء Tenant: {tenant.name}')

# إنشاء Domain
domain = Domain.objects.create(
    domain="farm1.localhost",
    tenant=tenant,
    is_primary=True
)
print(f'✅ تم إنشاء Domain: {domain.domain}')

# إنشاء Admin User
with tenant_context(tenant):
    admin = User.objects.create_user(
        username="admin",
        email="admin@example.com",
        password="Admin123!",
        full_name="مدير النظام",
        is_staff=True,
        is_superuser=True,
        role='owner'
    )
    print(f'✅ تم إنشاء Admin: {admin.username}')

print('\n' + '='*50)
print('✅ تم إنشاء Tenant بنجاح!')
print('='*50)
print(f'النطاق: {domain.domain}')
print(f'اسم المستخدم: admin')
print(f'كلمة المرور: Admin123!')
print('='*50)
```

---

## 🌐 الوصول

بعد إكمال الخطوات:

1. **Frontend:** `http://localhost:5173`
2. **API:** `http://farm1.localhost:8000/api/`
3. **Swagger:** `http://farm1.localhost:8000/api/docs`
4. **Admin:** `http://farm1.localhost:8000/admin/`

---

**جاهز! 🎉**

