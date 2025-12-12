#!/usr/bin/env python
"""
اختبار كامل لـ request مع tenant resolution
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tenants.aqua_core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django_tenants.utils import get_tenant

def test_request():
    """اختبار request كامل"""
    client = Client(HTTP_HOST='farm1.localhost:8000')
    
    # اختبار root
    print("\n=== Testing Root Path ===")
    response = client.get('/')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.content.decode()}")
    
    # اختبار API docs
    print("\n=== Testing /api/docs ===")
    response = client.get('/api/docs')
    print(f"Status: {response.status_code}")
    
    # اختبار API root
    print("\n=== Testing /api/ ===")
    response = client.get('/api/')
    print(f"Status: {response.status_code}")
    
    # التحقق من tenant في request
    from django.test import RequestFactory
    factory = RequestFactory()
    request = factory.get('/', HTTP_HOST='farm1.localhost:8000')
    tenant = get_tenant(request)
    print(f"\n=== Tenant from get_tenant() ===")
    print(f"Tenant: {tenant.schema_name if tenant else 'None'}")

if __name__ == '__main__':
    test_request()

