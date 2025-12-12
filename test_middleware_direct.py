#!/usr/bin/env python
"""
اختبار TenantMainMiddleware مباشرة
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

def dummy_view(request):
    return None

def test_middleware():
    """اختبار middleware مباشرة"""
    factory = RequestFactory()
    request = factory.get('/', HTTP_HOST='farm1.localhost:8000')
    
    print(f"Request Host: {request.get_host()}")
    
    # إنشاء middleware instance
    middleware = TenantMainMiddleware(dummy_view)
    
    # تحقق من domain قبل middleware
    host = request.get_host().split(':')[0]  # إزالة port
    print(f"Host without port: {host}")
    
    try:
        domain = Domain.objects.get(domain=host)
        print(f"✅ Domain found in DB: {domain.domain}")
        print(f"   Tenant: {domain.tenant.schema_name}")
    except Domain.DoesNotExist:
        print(f"❌ Domain '{host}' not found in DB!")
        print(f"Available domains:")
        for d in Domain.objects.all():
            print(f"  - {d.domain}")
    
    # تشغيل middleware
    print("\n=== Running middleware ===")
    try:
        response = middleware(request)
        tenant = get_tenant(request)
        print(f"Tenant after middleware: {tenant.schema_name if tenant else 'None'}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_middleware()

