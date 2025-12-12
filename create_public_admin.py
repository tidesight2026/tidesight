#!/usr/bin/env python
"""
Script لإنشاء مستخدم admin في public schema باستخدام Django's default User
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tenants.aqua_core.settings')
django.setup()

from django.db import connection
from django_tenants.utils import get_public_schema_name
from django.contrib.auth import get_user_model

# استخدام Django's default User model في public schema
# (لأن accounts.User موجود فقط في tenant schemas)
User = get_user_model()

# الانتقال إلى public schema
public_schema = get_public_schema_name()
connection.set_schema_to_public()

# معلومات المستخدم
USERNAME = 'admin'
EMAIL = 'admin@aquaerp.com'
PASSWORD = 'admin123'

try:
    # التحقق من وجود المستخدم
    try:
        existing_user = User.objects.get(username=USERNAME)
        # تحديث كلمة المرور
        existing_user.set_password(PASSWORD)
        existing_user.email = EMAIL
        existing_user.is_staff = True
        existing_user.is_superuser = True
        existing_user.save()
        print(f'✅ تم تحديث مستخدم موجود: {USERNAME}')
    except User.DoesNotExist:
        # إنشاء مستخدم جديد
        user = User.objects.create_user(
            username=USERNAME,
            email=EMAIL,
            password=PASSWORD,
            is_staff=True,
            is_superuser=True
        )
        print(f'✅ تم إنشاء مستخدم جديد: {USERNAME}')
    
    print(f'\n✅ تم إنشاء مستخدم Admin في Public Schema بنجاح!')
    print(f'   Username: {USERNAME}')
    print(f'   Email: {EMAIL}')
    print(f'   Password: {PASSWORD}')
    print(f'   Schema: {public_schema}')
    print(f'\n🌐 يمكنك الآن تسجيل الدخول على:')
    print(f'   http://localhost:8000/admin/')
    
except Exception as e:
    print(f'❌ حدث خطأ: {str(e)}')
    import traceback
    traceback.print_exc()
    print(f'\n💡 ملاحظة: إذا كان الخطأ يتعلق بـ accounts.User،')
    print(f'   فهذا يعني أن AUTH_USER_MODEL يشير إلى accounts.User')
    print(f'   لكن accounts موجود فقط في TENANT_APPS.')
    print(f'   يجب استخدام Django\'s default User في public schema.')
