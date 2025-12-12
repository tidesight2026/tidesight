#!/usr/bin/env python
"""
اختبار تطابق domain
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tenants.aqua_core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from tenants.models import Domain
from django_tenants.utils import get_tenant_domain_model

def test_domain():
    """اختبار domain matching"""
    DomainModel = get_tenant_domain_model()
    
    # اختبار مختلف formats
    test_hosts = [
        'farm1.localhost',
        'farm1.localhost:8000',
        'www.farm1.localhost',
    ]
    
    print("=== Domains in DB ===")
    domains = DomainModel.objects.all()
    for d in domains:
        print(f"Domain: '{d.domain}' | Tenant: {d.tenant.schema_name}")
    
    print("\n=== Testing host matching ===")
    for host in test_hosts:
        # إزالة port
        host_without_port = host.split(':')[0]
        
        try:
            domain = DomainModel.objects.get(domain=host_without_port)
            print(f"✅ '{host}' -> matches '{domain.domain}' (tenant: {domain.tenant.schema_name})")
        except DomainModel.DoesNotExist:
            print(f"❌ '{host}' -> No match found")

if __name__ == '__main__':
    test_domain()

