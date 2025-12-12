#!/usr/bin/env python
"""
سكريبت لاختبار API endpoint والتحقق من المسارات
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
from django.urls import resolve, Resolver404

def test_api_routes():
    """اختبار API routes"""
    
    print("=" * 60)
    print("🔍 اختبار API Routes")
    print("=" * 60)
    
    # الحصول على tenant
    try:
        tenant = Client.objects.get(schema_name='farm1')
        print(f"✅ Tenant موجود: {tenant.name} (schema: {tenant.schema_name})")
    except Client.DoesNotExist:
        print("❌ Tenant 'farm1' غير موجود!")
        return
    
    # التحقق من domain
    domains = tenant.domains.all()
    if domains:
        print(f"✅ Domains موجودة: {', '.join([d.domain for d in domains])}")
    else:
        print("❌ لا توجد domains!")
        return
    
    print("\n" + "-" * 60)
    print("🔍 اختبار المسارات في tenant context...")
    print("-" * 60)
    
    factory = RequestFactory()
    
    # قائمة المسارات للاختبار
    test_paths = [
        '/api/',
        '/api/auth/',
        '/api/auth/login',
        '/api/docs',
        '/api/openapi.json',
    ]
    
    with tenant_context(tenant):
        print("\n📋 نتائج اختبار المسارات:")
        for path in test_paths:
            try:
                # إنشاء request مع domain
                request = factory.get(path, HTTP_HOST='farm1.localhost:8000')
                request.tenant = tenant
                
                # محاولة resolve المسار
                resolver_match = resolve(path)
                print(f"✅ {path:30s} -> {resolver_match.view_name if hasattr(resolver_match, 'view_name') else resolver_match.func}")
            except Resolver404 as e:
                print(f"❌ {path:30s} -> Not Found ({str(e)})")
            except Exception as e:
                print(f"⚠️  {path:30s} -> Error: {str(e)}")
    
    print("\n" + "-" * 60)
    print("🔍 اختبار Django Ninja API مباشرة...")
    print("-" * 60)
    
    with tenant_context(tenant):
        try:
            from tenants.aqua_core.urls import api
            print(f"✅ Django Ninja API object: {api}")
            print(f"✅ API title: {api.title}")
            
            # محاولة الوصول إلى routers
            if hasattr(api, '_routers'):
                print(f"✅ API routers: {len(api._routers)} routers")
                for router in api._routers:
                    print(f"   - Router: {router}")
            else:
                print("⚠️  لا يمكن الوصول إلى _routers")
                
        except Exception as e:
            print(f"❌ خطأ في تحميل Django Ninja API: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "-" * 60)
    print("🔍 اختبار api_router مباشرة...")
    print("-" * 60)
    
    with tenant_context(tenant):
        try:
            from api.router import api_router
            print(f"✅ api_router موجود: {api_router}")
            
            # محاولة الوصول إلى routes
            if hasattr(api_router, '_routers'):
                print(f"✅ api_router routers: {len(api_router._routers)} routers")
                for router_path, router_info in api_router._routers.items():
                    print(f"   - Path: {router_path}, Router: {router_info}")
            else:
                print("⚠️  لا يمكن الوصول إلى _routers")
                
        except Exception as e:
            print(f"❌ خطأ في تحميل api_router: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ انتهى الاختبار")
    print("=" * 60)

if __name__ == '__main__':
    test_api_routes()

