# tests/conftest.py
"""
Pytest Configuration and Fixtures للاختبارات مع django-tenants
"""
import pytest
from django.test import override_settings
from django_tenants.utils import schema_context, tenant_context, get_tenant_model
from django.core.management import call_command
from django.db import connection

TenantModel = get_tenant_model()


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """
    إعداد قاعدة البيانات مع إنشاء tenant schema للاختبار
    """
    with django_db_blocker.unblock():
        # إنشاء tenant للاختبار
        try:
            # التحقق من وجود tenant
            tenant = TenantModel.objects.filter(schema_name='test_farm').first()
            if not tenant:
                tenant = TenantModel.objects.create(
                    name='Test Farm',
                    schema_name='test_farm',
                    paid_until='2099-12-31',
                    on_trial=False
                )
                
                from tenants.models import Domain
                Domain.objects.create(
                    domain='test.localhost',
                    tenant=tenant,
                    is_primary=True
                )
            
            # تشغيل migrations على tenant schema
            connection.set_schema_to_public()
            call_command('migrate_schemas', '--tenant', schema_name='test_farm', verbosity=0)
        except Exception as e:
            print(f"Warning: Could not setup tenant: {e}")


@pytest.fixture
def tenant(db):
    """
    Tenant fixture - يعيد tenant للاختبار
    """
    try:
        tenant = TenantModel.objects.get(schema_name='test_farm')
        return tenant
    except TenantModel.DoesNotExist:
        pytest.skip("Test tenant not found")


@pytest.fixture
def tenant_context_fixture(tenant):
    """
    Context manager للعمل ضمن tenant schema
    """
    with tenant_context(tenant):
        yield tenant


@pytest.fixture(autouse=True)
def use_tenant_schema(db, tenant):
    """
    Fixture تلقائي - يجعل جميع الاختبارات تعمل ضمن tenant schema
    """
    with tenant_context(tenant):
        yield


@pytest.fixture
def user_setup(tenant_context_fixture):
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
