#!/usr/bin/env python
"""
سكريبت لاختبار URL resolution في tenant context
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tenants.aqua_core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django_tenants.utils import tenant_context
from tenants.models import Client
from django.test import RequestFactory
from django.urls import resolve

def test_url_resolution():
    """اختبار URL resolution"""
    tenant = Client.objects.filter(schema_name='farm1').first()
    
    if not tenant:
        print("❌ Tenant 'farm1' غير موجود!")
        return
    
    print(f"✅ Tenant موجود: {tenant.name}")
    
    # اختبار في tenant context
    with tenant_context(tenant):
        factory = RequestFactory()
        request = factory.get('/api/docs', HTTP_HOST='farm1.localhost:8000')
        
        try:
            match = resolve('/api/docs')
            print(f"✅ Route found: {match.view_name}")
            print(f"   URL Name: {match.url_name}")
            print(f"   Namespace: {match.namespace}")
        except Exception as e:
            print(f"❌ Route NOT found: {e}")
            
        # محاولة أخرى
        try:
            match = resolve('/api/')
            print(f"✅ Route /api/ found: {match.view_name}")
        except Exception as e:
            print(f"❌ Route /api/ NOT found: {e}")

if __name__ == '__main__':
    test_url_resolution()

