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

