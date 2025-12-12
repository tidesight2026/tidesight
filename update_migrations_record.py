#!/usr/bin/env python
"""
Script لتحديث سجل migrations لـ accounts في public schema
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tenants.aqua_core.settings')
django.setup()

from django.db import connection
from django_tenants.utils import get_public_schema_name

# الانتقال إلى public schema
public_schema = get_public_schema_name()
connection.set_schema_to_public()

print(f'🔍 Schema الحالي: {connection.schema_name}')

try:
    with connection.cursor() as cursor:
        # تحديث django_migrations
        cursor.execute("""
            INSERT INTO django_migrations (app, name, applied)
            VALUES ('accounts', '0001_initial', NOW())
            ON CONFLICT DO NOTHING
        """)
        print('✅ تم تحديث django_migrations لـ accounts')
        
except Exception as e:
    print(f'❌ حدث خطأ: {str(e)}')
    import traceback
    traceback.print_exc()
