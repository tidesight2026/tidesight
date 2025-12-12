#!/usr/bin/env python
"""
Script لإصلاح صيغة Domains الخاطئة
"""
import os
import django
import re
from urllib.parse import urlparse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tenants.aqua_core.settings')
django.setup()

from django.db import connection
from django_tenants.utils import get_public_schema_name
from tenants.models import Domain

# الانتقال إلى public schema
public_schema = get_public_schema_name()
connection.set_schema_to_public()

print(f'🔍 Schema الحالي: {public_schema}')

def clean_domain(domain):
    """تنظيف Domain من URL إلى hostname فقط"""
    domain = domain.strip()
    
    # إزالة http:// أو https://
    if domain.startswith('http://') or domain.startswith('https://'):
        parsed = urlparse(domain)
        domain = parsed.netloc or parsed.path
    
    # إزالة :port إذا كان موجوداً
    if ':' in domain:
        domain = domain.split(':')[0]
    
    # إزالة المسار (path) إذا كان موجوداً
    if '/' in domain:
        domain = domain.split('/')[0]
    
    return domain.strip()

try:
    domains = Domain.objects.all()
    print(f'📋 عدد Domains: {domains.count()}')
    
    fixed_count = 0
    for domain in domains:
        original = domain.domain
        cleaned = clean_domain(original)
        
        if original != cleaned:
            print(f'\n🔧 إصلاح Domain:')
            print(f'   قبل: {original}')
            print(f'   بعد: {cleaned}')
            
            domain.domain = cleaned
            domain.save()
            fixed_count += 1
            print(f'   ✅ تم الإصلاح')
        else:
            print(f'✅ Domain صحيح: {original}')
    
    print(f'\n📊 الملخص:')
    print(f'   ✅ تم إصلاح {fixed_count} Domain(s)')
    print(f'   ✅ {domains.count() - fixed_count} Domain(s) كانت صحيحة')
    
except Exception as e:
    print(f'❌ حدث خطأ: {str(e)}')
    import traceback
    traceback.print_exc()
