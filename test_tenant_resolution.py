#!/usr/bin/env python
"""
اختبار tenant resolution من HTTP request
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tenants.aqua_core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import RequestFactory
from django_tenants.middleware.main import TenantMainMiddleware
from django_tenants.utils import get_tenant
from tenants.models import Domain

def test_tenant_from_request():
    """اختبار كيفية تحديد tenant من request"""
    factory = RequestFactory()
    
    # محاكاة request من farm1.localhost
    request = factory.get('/api/docs', HTTP_HOST='farm1.localhost:8000')
    
    # محاولة تحديد tenant
    try:
        domain = Domain.objects.get(domain='farm1.localhost')
        print(f"✅ Domain found: {domain.domain}")
        print(f"   Tenant: {domain.tenant.name} (schema: {domain.tenant.schema_name})")
        print(f"   Is primary: {domain.is_primary}")
        
        # اختبار get_tenant
        tenant = get_tenant(request)
        if tenant:
            print(f"✅ Tenant from request: {tenant.name}")
        else:
            print("❌ No tenant found from request")
            
    except Domain.DoesNotExist:
        print("❌ Domain 'farm1.localhost' not found!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_tenant_from_request()

