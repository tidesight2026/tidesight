#!/usr/bin/env python
"""
Script لإصلاح Domain tmco
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tenants.aqua_core.settings')
django.setup()

from django.db import connection
from django_tenants.utils import get_public_schema_name
from tenants.models import Domain

# الانتقال إلى public schema
public_schema = get_public_schema_name()
connection.set_schema_to_public()

try:
    # البحث عن Domain الذي يحتوي على tmco
    domain = Domain.objects.filter(domain__icontains='tmco').first()
    
    if not domain:
        # البحث عن Domain الذي يحتوي على localhost فقط
        domain = Domain.objects.filter(domain='localhost').first()
    
    if domain:
        print(f'Domain الحالي: {domain.domain}')
        print(f'Tenant: {domain.tenant.name}')
        print(f'Schema: {domain.tenant.schema_name}')
        
        # تحديث Domain إلى tmco.localhost
        domain.domain = 'tmco.localhost'
        domain.save()
        
        print(f'\n✅ تم تحديث Domain إلى: {domain.domain}')
        print(f'\n📋 الخطوات التالية:')
        print(f'1. أضف إلى hosts file: 127.0.0.1    tmco.localhost')
        print(f'2. شغّل migrations: docker-compose exec web python manage.py migrate_schemas --tenant --schema_name {domain.tenant.schema_name}')
        print(f'3. أنشئ مستخدم admin في Tenant')
        print(f'4. افتح: http://tmco.localhost:8000/admin/')
    else:
        print('❌ لم يتم العثور على Domain')
        
except Exception as e:
    print(f'❌ حدث خطأ: {str(e)}')
    import traceback
    traceback.print_exc()
