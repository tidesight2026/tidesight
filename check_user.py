#!/usr/bin/env python
"""
سكريبت للتحقق من وجود المستخدم والبيانات
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tenants.aqua_core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django_tenants.utils import tenant_context
from tenants.models import Client
from django.contrib.auth import get_user_model

User = get_user_model()

def check_user():
    """التحقق من وجود المستخدم"""
    tenant = Client.objects.filter(schema_name='farm1').first()
    
    if not tenant:
        print("❌ Tenant 'farm1' غير موجود!")
        return
    
    print(f"✅ Tenant موجود: {tenant.name}")
    
    with tenant_context(tenant):
        users = User.objects.all()
        print(f"\n📊 عدد المستخدمين: {users.count()}")
        
        for user in users:
            print(f"\n👤 المستخدم:")
            print(f"   - Username: {user.username}")
            print(f"   - Email: {user.email}")
            print(f"   - Full Name: {getattr(user, 'full_name', 'N/A')}")
            print(f"   - Is Active: {user.is_active}")
            print(f"   - Is Staff: {user.is_staff}")
            print(f"   - Is Superuser: {user.is_superuser}")
            
            # اختبار المصادقة
            from django.contrib.auth import authenticate
            authenticated = authenticate(username=user.username, password='Admin123!')
            if authenticated:
                print(f"   ✅ المصادقة تعمل! (password: Admin123!)")
            else:
                print(f"   ❌ المصادقة فشلت!")
                
            # اختبار بالبريد الإلكتروني
            try:
                user_by_email = User.objects.get(email=user.email)
                authenticated_email = authenticate(username=user_by_email.username, password='Admin123!')
                if authenticated_email:
                    print(f"   ✅ المصادقة تعمل بالبريد الإلكتروني!")
            except:
                pass

if __name__ == '__main__':
    check_user()

