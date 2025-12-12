#!/usr/bin/env python
"""
Script مفصل لاختبار tenant resolution
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tenants.aqua_core.settings')
django.setup()

from django.test import RequestFactory
from django_tenants.utils import get_tenant, get_tenant_model, get_public_schema_name
from django.db import connection
from django_tenants.utils import schema_context
from tenants.models import Domain, Client

# الانتقال إلى public schema
public_schema = get_public_schema_name()
connection.set_schema_to_public()

print('=' * 60)
print('🔍 اختبار مفصل لـ Tenant Resolution')
print('=' * 60)

# 1. التحقق من Domain
print('\n1️⃣ Domains في قاعدة البيانات:')
domains = Domain.objects.all()
for d in domains:
    print(f'   - {d.domain} -> {d.tenant.name} (schema: {d.tenant.schema_name}, primary: {d.is_primary})')

# 2. اختبار get_tenant مباشرة
print('\n2️⃣ اختبار get_tenant() مباشرة:')
factory = RequestFactory()

# اختبار مع HTTP_HOST
test_hosts = [
    'tmco.localhost:8000',
    'tmco.localhost',
    'http://tmco.localhost:8000',
]

for host in test_hosts:
    print(f'\n   Testing: {host}')
    try:
        request = factory.get('/admin/', HTTP_HOST=host)
        print(f'   Request.get_host(): {request.get_host()}')
        
        # محاولة get_tenant
        tenant = get_tenant(request)
        if tenant:
            print(f'   ✅ Tenant: {tenant.name} (schema: {tenant.schema_name})')
        else:
            print(f'   ❌ No tenant found')
            
            # محاولة البحث اليدوي
            hostname = request.get_host().split(':')[0]
            print(f'   Hostname extracted: {hostname}')
            try:
                domain_obj = Domain.objects.get(domain=hostname)
                print(f'   ✅ Domain found manually: {domain_obj.domain} -> {domain_obj.tenant.name}')
            except Domain.DoesNotExist:
                print(f'   ❌ Domain "{hostname}" not found in DB')
    except Exception as e:
        print(f'   ❌ Error: {str(e)}')

# 3. اختبار TenantMainMiddleware مباشرة
print('\n3️⃣ اختبار TenantMainMiddleware:')
try:
    from django_tenants.middleware.main import TenantMainMiddleware
    
    def dummy_view(request):
        return None
    
    middleware = TenantMainMiddleware(dummy_view)
    request = factory.get('/admin/', HTTP_HOST='tmco.localhost:8000')
    
    print(f'   Request Host: {request.get_host()}')
    
    # تشغيل middleware
    try:
        response = middleware(request)
        tenant = get_tenant(request)
        if tenant:
            print(f'   ✅ Tenant after middleware: {tenant.name}')
        else:
            print(f'   ❌ No tenant after middleware')
    except Exception as e:
        print(f'   ❌ Middleware error: {str(e)}')
        import traceback
        traceback.print_exc()
except Exception as e:
    print(f'   ❌ Error importing middleware: {str(e)}')

# 4. التحقق من إعدادات django-tenants
print('\n4️⃣ إعدادات django-tenants:')
from django.conf import settings
print(f'   TENANT_MODEL: {getattr(settings, "TENANT_MODEL", "Not set")}')
print(f'   TENANT_DOMAIN_MODEL: {getattr(settings, "TENANT_DOMAIN_MODEL", "Not set")}')
print(f'   SHOW_PUBLIC_IF_NO_TENANT_FOUND: {getattr(settings, "SHOW_PUBLIC_IF_NO_TENANT_FOUND", "Not set")}')

print('\n' + '=' * 60)
