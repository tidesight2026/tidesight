#!/usr/bin/env python
"""
سكريبت لإنشاء Tenant تجريبي
"""
import os
import sys
import django

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tenants.aqua_core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django_tenants.utils import tenant_context
from tenants.models import Client, Domain
from django.contrib.auth import get_user_model

User = get_user_model()

def create_test_tenant():
    """إنشاء Tenant تجريبي"""
    
    schema_name = "farm1"
    name = "مزرعة تجريبية"
    email = "test@example.com"
    domain_name = "farm1.localhost"
    
    admin_username = "admin"
    admin_email = "admin@example.com"
    admin_password = "Admin123!"
    
    print(f'جاري إنشاء Tenant "{name}"...')
    
    try:
        # إنشاء Client (Tenant)
        tenant = Client.objects.create(
            name=name,
            email=email,
            schema_name=schema_name,
            subscription_type='trial',
            is_active=True,
        )
        
        print(f'✅ تم إنشاء Tenant "{name}"')
        
        # إنشاء Domain
        domain = Domain.objects.create(
            domain=domain_name,
            tenant=tenant,
            is_primary=True
        )
        
        print(f'✅ تم إنشاء Domain "{domain.domain}"')
        
        # إنشاء مستخدم Admin في Schema الخاص بالعميل
        with tenant_context(tenant):
            admin_user = User.objects.create_user(
                username=admin_username,
                email=admin_email,
                password=admin_password,
                full_name="مدير النظام",
                is_staff=True,
                is_superuser=True,
                role='owner'
            )
        
        print(f'✅ تم إنشاء مستخدم Admin')
        
        # عرض النتائج
        print('\n' + '='*50)
        print('✅ تم إنشاء Tenant بنجاح!')
        print('='*50)
        print(f'اسم الشركة: {name}')
        print(f'النطاق: {domain.domain}')
        print(f'Schema Name: {schema_name}')
        print(f'اسم المستخدم: {admin_username}')
        print(f'البريد الإلكتروني: {admin_email}')
        print(f'كلمة المرور: {admin_password}')
        print('='*50)
        print(f'\n⚠️  للوصول إلى لوحة التحكم: http://{domain.domain}:8000/admin/')
        print(f'للوصول إلى API: http://{domain.domain}:8000/api/')
        
    except Exception as e:
        print(f'❌ حدث خطأ أثناء إنشاء Tenant: {str(e)}')
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    success = create_test_tenant()
    sys.exit(0 if success else 1)

