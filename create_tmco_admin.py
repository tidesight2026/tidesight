#!/usr/bin/env python
"""
Script لإنشاء مستخدم admin في tenant tmco
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tenants.aqua_core.settings')
django.setup()

from django_tenants.utils import tenant_context
from tenants.models import Client
from accounts.models import User

# معلومات المستخدم
SCHEMA_NAME = 'tilapia_marine_company'
USERNAME = 'admin'
EMAIL = 'admin@tmco.com'
PASSWORD = 'admin123'

try:
    # الحصول على Tenant
    tenant = Client.objects.get(schema_name=SCHEMA_NAME)
    print(f'✅ تم العثور على Tenant: {tenant.name}')
    
    # إنشاء المستخدم داخل tenant context
    with tenant_context(tenant):
        # التحقق من وجود المستخدم أولاً
        try:
            existing_user = User.objects.get(username=USERNAME)
            # تحديث كلمة المرور
            existing_user.set_password(PASSWORD)
            existing_user.email = EMAIL
            existing_user.is_staff = True
            existing_user.is_superuser = True
            existing_user.role = 'owner'
            existing_user.save()
            print(f'✅ تم تحديث مستخدم موجود: {USERNAME}')
        except User.DoesNotExist:
            # إنشاء مستخدم جديد
            user = User.objects.create_user(
                username=USERNAME,
                email=EMAIL,
                password=PASSWORD,
                is_staff=True,
                is_superuser=True,
                role='owner'
            )
            print(f'✅ تم إنشاء مستخدم جديد: {USERNAME}')
        
        print(f'✅ تم إنشاء مستخدم Admin بنجاح!')
        print(f'   Username: {USERNAME}')
        print(f'   Email: {EMAIL}')
        print(f'   Password: {PASSWORD}')
        print(f'   Schema: {SCHEMA_NAME}')
        print(f'\n🌐 يمكنك الآن تسجيل الدخول على:')
        print(f'   http://tmco.localhost:8000/admin/')
        
except Client.DoesNotExist:
    print(f'❌ Tenant "{SCHEMA_NAME}" غير موجود!')
    print('   قم بإنشاء tenant أولاً')
except Exception as e:
    print(f'❌ حدث خطأ: {str(e)}')
    import traceback
    traceback.print_exc()
