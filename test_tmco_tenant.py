#!/usr/bin/env python
"""
Script لاختبار tenant resolution لـ tmco.localhost
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tenants.aqua_core.settings')
django.setup()

from django.test import RequestFactory
from django_tenants.utils import get_tenant, get_public_schema_name
from django.db import connection
from django_tenants.utils import get_public_schema_name
from tenants.models import Domain, Client

# الانتقال إلى public schema
public_schema = get_public_schema_name()
connection.set_schema_to_public()

print('=' * 60)
print('🔍 اختبار Tenant Resolution لـ tmco.localhost')
print('=' * 60)

# 1. التحقق من Domain في قاعدة البيانات
print('\n1️⃣ التحقق من Domain في قاعدة البيانات:')
try:
    domain = Domain.objects.get(domain='tmco.localhost')
    print(f'   ✅ Domain موجود: {domain.domain}')
    print(f'   ✅ Tenant: {domain.tenant.name}')
    print(f'   ✅ Schema: {domain.tenant.schema_name}')
    print(f'   ✅ Is Primary: {domain.is_primary}')
except Domain.DoesNotExist:
    print('   ❌ Domain "tmco.localhost" غير موجود!')
    print('   Domains المتاحة:')
    for d in Domain.objects.all():
        print(f'      - {d.domain} (Tenant: {d.tenant.name})')
    exit(1)

# 2. اختبار tenant resolution من request
print('\n2️⃣ اختبار Tenant Resolution من Request:')
factory = RequestFactory()

# محاكاة request من tmco.localhost:8000
request = factory.get('/admin/', HTTP_HOST='tmco.localhost:8000')
host = request.get_host()
hostname = host.split(':')[0]

print(f'   Request Host: {host}')
print(f'   Hostname (بدون port): {hostname}')

try:
    tenant = get_tenant(request)
    if tenant:
        print(f'   ✅ Tenant تم العثور عليه: {tenant.name}')
        print(f'   ✅ Schema: {tenant.schema_name}')
    else:
        print('   ❌ لم يتم العثور على Tenant!')
        print('\n   🔍 محاولة البحث اليدوي:')
        try:
            domain_obj = Domain.objects.get(domain=hostname)
            print(f'   ✅ Domain موجود: {domain_obj.domain}')
            print(f'   ✅ Tenant: {domain_obj.tenant.name}')
            print(f'   ⚠️  المشكلة: get_tenant() لا يعيد Tenant رغم وجود Domain')
        except Domain.DoesNotExist:
            print(f'   ❌ Domain "{hostname}" غير موجود في قاعدة البيانات')
except Exception as e:
    print(f'   ❌ خطأ: {str(e)}')
    import traceback
    traceback.print_exc()

# 3. التحقق من ALLOWED_HOSTS
print('\n3️⃣ التحقق من ALLOWED_HOSTS:')
from django.conf import settings
allowed_hosts = settings.ALLOWED_HOSTS
print(f'   ALLOWED_HOSTS: {allowed_hosts}')
if 'tmco.localhost' in allowed_hosts or '*.localhost' in allowed_hosts or any('localhost' in h for h in allowed_hosts):
    print('   ✅ tmco.localhost مسموح به')
else:
    print('   ⚠️  قد يكون هناك مشكلة في ALLOWED_HOSTS')

# 4. اختبار مع hostname مختلف
print('\n4️⃣ اختبار مع hostname بدون port:')
request2 = factory.get('/admin/', HTTP_HOST='tmco.localhost')
host2 = request2.get_host()
print(f'   Request Host: {host2}')
try:
    tenant2 = get_tenant(request2)
    if tenant2:
        print(f'   ✅ Tenant تم العثور عليه: {tenant2.name}')
    else:
        print('   ❌ لم يتم العثور على Tenant')
except Exception as e:
    print(f'   ❌ خطأ: {str(e)}')

print('\n' + '=' * 60)
