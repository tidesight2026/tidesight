#!/usr/bin/env python
"""
Script لإعداد domain للـ public schema للوصول عبر localhost
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tenants.aqua_core.settings')
django.setup()

from django_tenants.utils import schema_context, get_public_schema_name
from tenants.models import Domain, Client
from django.db import connection

def setup_public_domain():
    """إعداد domain للـ public schema"""
    
    # الانتقال إلى public schema
    public_schema = get_public_schema_name()
    connection.set_schema_to_public()
    
    print(f'🔍 التحقق من public schema: {public_schema}')
    
    # التحقق من وجود domain للـ public schema
    try:
        # محاولة الحصول على Client للـ public schema
        # في django-tenants، public schema عادة لا يحتوي على Client
        # لكن يمكننا إنشاء Domain مباشرة
        
        # التحقق من وجود domain 'localhost'
        existing_domain = Domain.objects.filter(domain='localhost').first()
        
        if existing_domain:
            print(f'✅ Domain موجود بالفعل: localhost -> {existing_domain.tenant.name if existing_domain.tenant else "public"}')
            return
        
        # إنشاء domain للـ public schema
        # في django-tenants، public schema لا يحتاج tenant
        # لكن Domain model يتطلب tenant، لذا سنستخدم None أو ننشئ tenant خاص
        
        # الحل: إنشاء tenant خاص للـ public schema أو استخدام tenant موجود
        # الأفضل: استخدام tenant موجود أو إنشاء tenant افتراضي
        
        # محاولة الحصول على أول tenant
        first_tenant = Client.objects.first()
        
        if not first_tenant:
            print('⚠️  لا يوجد tenants في النظام. يجب إنشاء tenant أولاً.')
            print('   استخدم: python manage.py create_tenant ...')
            return
        
        # إنشاء domain للـ public schema
        # ملاحظة: في django-tenants، public schema عادة لا يحتاج domain
        # لكن يمكننا إنشاء domain خاص للوصول
        
        # الحل الأفضل: استخدام tenant موجود كـ fallback
        public_domain = Domain.objects.create(
            domain='localhost',
            tenant=first_tenant,  # استخدام tenant موجود كـ fallback
            is_primary=False
        )
        
        print(f'✅ تم إنشاء domain: localhost -> {first_tenant.name}')
        print(f'   ⚠️  ملاحظة: هذا domain مرتبط بـ tenant موجود كـ fallback')
        print(f'   💡 للوصول إلى public schema، استخدم: http://127.0.0.1:8000/admin/')
        
    except Exception as e:
        print(f'❌ حدث خطأ: {str(e)}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    setup_public_domain()
