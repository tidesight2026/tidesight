# tests/conftest.py
"""
Pytest Configuration and Fixtures للاختبارات مع django-tenants
"""
import pytest
from django_tenants.utils import tenant_context, get_tenant_model
from django.core.management import call_command
from django.db import connection

TenantModel = get_tenant_model()


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """
    إعداد قاعدة البيانات مع إنشاء tenant schema للاختبار
    """
    with django_db_blocker.unblock():
        try:
            from tenants.models import Domain
            from django_tenants.utils import schema_context
            
            # التحقق من وجود tenant
            connection.set_schema_to_public()
            tenant = TenantModel.objects.filter(schema_name='test_farm').first()
            if not tenant:
                # إنشاء tenant في public schema
                tenant = TenantModel.objects.create(
                    name='Test Farm',
                    schema_name='test_farm',
                    subscription_type='trial',
                    on_trial=True,
                    email='test@test.com'
                )
                
                Domain.objects.create(
                    domain='test.localhost',
                    tenant=tenant,
                    is_primary=True
                )
                print(f"✅ Created tenant: {tenant.schema_name}")
            
            # تشغيل migrations على tenant schema
            connection.set_schema_to_public()
            print(f"🔄 Running migrations for tenant: {tenant.schema_name}")
            
            # استخدام schema_context للتأكد من تشغيل migrations بشكل صحيح
            with schema_context(tenant.schema_name):
                call_command('migrate', verbosity=0, interactive=False)
                print(f"✅ Migrations completed for tenant: {tenant.schema_name}")
        except Exception as e:
            print(f"❌ Warning: Could not setup tenant: {e}")
            import traceback
            traceback.print_exc()


@pytest.fixture
def tenant(db):
    """
    Tenant fixture - يعيد tenant للاختبار ويضمن أن migrations قد تم تشغيلها
    """
    from django_tenants.utils import schema_context
    
    connection.set_schema_to_public()
    tenant = TenantModel.objects.filter(schema_name='test_farm').first()
    
    if not tenant:
        from tenants.models import Domain
        
        # إنشاء tenant
        tenant = TenantModel.objects.create(
            name='Test Farm',
            schema_name='test_farm',
            subscription_type='trial',
            on_trial=True,
            email='test@test.com'
        )
        
        Domain.objects.create(
            domain='test.localhost',
            tenant=tenant,
            is_primary=True
        )
    
    # تشغيل migrations على tenant schema
    connection.set_schema_to_public()
    try:
        # استخدام migrate_schemas
        call_command('migrate_schemas', '--tenant', schema_name=tenant.schema_name, verbosity=0, interactive=False)
    except Exception:
        # محاولة بديلة باستخدام schema_context
        try:
            with schema_context(tenant.schema_name):
                call_command('migrate', verbosity=0, interactive=False)
        except Exception as e:
            print(f"Warning: Could not migrate tenant schema: {e}")
    
    return tenant


@pytest.fixture(autouse=True)
def use_tenant_schema(tenant, db):
    """
    Fixture تلقائي - يجعل جميع الاختبارات تعمل ضمن tenant schema
    """
    with tenant_context(tenant):
        yield


@pytest.fixture
def user_setup():
    """
    إنشاء مستخدم تجريبي داخل tenant
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    user = User.objects.create_user(
        username="test_user",
        email="test@example.com",
        password="testpass123",
        full_name="مستخدم اختبار",
        role="owner"
    )
    return user
