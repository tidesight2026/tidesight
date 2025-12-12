"""
Pytest Configuration and Fixtures

🔥 جاهزة للعمل مباشرة وبأفضل ممارسات django-tenants + pytest
"""
import pytest
from django.contrib.auth import get_user_model
from django_tenants.utils import (
    schema_context, get_tenant_model, get_tenant_domain_model
)
from django.core.management import call_command
from django.db import connection

User = get_user_model()
TenantModel = get_tenant_model()
DomainModel = get_tenant_domain_model()


# ============================================================
# 🧪 1) Default Test Client
# ============================================================
@pytest.fixture
def client():
    """Django test client"""
    from django.test import Client
    return Client()


# ============================================================
# 👤 2) Public Schema Users (not tenant users)
# ============================================================
@pytest.fixture
def test_user(db):
    """User in PUBLIC schema"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        full_name='Test User',
        role='owner'
    )


@pytest.fixture
def test_manager(db):
    """Manager user in PUBLIC schema"""
    return User.objects.create_user(
        username='manager',
        email='manager@example.com',
        password='testpass123',
        full_name='Manager User',
        role='manager'
    )


@pytest.fixture
def test_worker(db):
    """Worker user in PUBLIC schema"""
    return User.objects.create_user(
        username='worker',
        email='worker@example.com',
        password='testpass123',
        full_name='Worker User',
        role='worker'
    )


# ============================================================
# 🏡 3) Tenant Fixture (creates schema + runs migrations)
# ============================================================
@pytest.fixture(scope='function')
def test_tenant(db):
    """
    Creates a complete tenant with:
    - schema creation
    - domain
    - migrations
    - returned tenant instance

    ❗ DOES NOT automatically activate the schema.
       Use:  with schema_context(tenant.schema_name):
    """
    connection.set_schema_to_public()

    schema_name = "test_farm"

    tenant, created = TenantModel.objects.get_or_create(
        schema_name=schema_name,
        defaults=dict(
            name="Test Farm",
            email="test@example.com",
            subscription_type="trial",
            on_trial=True,
            is_active=True,
            is_active_subscription=True,
        ),
    )

    # Domain always recreated for clean tests
    DomainModel.objects.get_or_create(
        domain=f"{schema_name}.localhost",
        tenant=tenant,
        is_primary=True,
    )

    # ✅ Run tenant migrations - الصيغة الصحيحة
    # استخدام schema_name محدد أو tenant=True
    # migrate_schemas يقبل: --schema SCHEMA_NAME أو --tenant
    try:
        # محاولة 1: استخدام schema_name محدد
        call_command("migrate_schemas", schema_name=schema_name, verbosity=0, interactive=False)
    except Exception as e1:
        try:
            # محاولة 2: استخدام tenant=True (لجميع tenants)
            call_command("migrate_schemas", shared=False, tenant=True, verbosity=0, interactive=False)
        except Exception as e2:
            # fallback: استخدام schema_context مع migrate مباشرة
            print(f"⚠️ migrate_schemas failed, using direct migrate...")
            with schema_context(schema_name):
                call_command("migrate", verbosity=0, interactive=False)
    
    # ✅ التحقق من أن migrations تم تطبيقها بشكل صحيح
    with schema_context(schema_name):
        tables = connection.introspection.table_names()
        required_tables = ['inventory_feedtype', 'accounts_user']
        missing_tables = [t for t in required_tables if t not in tables]
        
        if missing_tables:
            # محاولة ثانية مع migrate مباشرة
            print(f"⚠️ Warning: Missing tables {missing_tables}, running migrate directly...")
            call_command("migrate", verbosity=1, interactive=False)
            
            # التحقق مرة أخرى
            tables_after = connection.introspection.table_names()
            missing_after = [t for t in required_tables if t not in tables_after]
            
            if missing_after:
                raise AssertionError(
                    f"❌ Migrations didn't run inside tenant! Missing tables: {missing_after}. "
                    f"Available tables: {[t for t in tables_after if 'inventory' in t or 'accounts' in t]}"
                )
            else:
                print(f"✅ Migrations completed successfully. All tables exist.")
        else:
            print(f"✅ All required tables exist in tenant schema '{schema_name}'")

    yield tenant

    # Cleanup
    connection.set_schema_to_public()


# ============================================================
# 🏷️ 4) Tenant Context Fixture (automatic context manager)
# ============================================================
@pytest.fixture(scope='function')
def tenant_schema_context(test_tenant):
    """
    Usage:
        def test_x(test_tenant, tenant_schema_context):
            with tenant_schema_context:
                FeedType.objects.create(...)
    """
    return schema_context(test_tenant.schema_name)


# ============================================================
# 👤 5) Tenant User Fixture (user created INSIDE tenant schema)
# ============================================================
@pytest.fixture
def tenant_user(test_tenant):
    """
    Creates a user INSIDE the tenant schema.
    
    Usage:
        def test_x(test_tenant, tenant_user):
            with schema_context(test_tenant.schema_name):
                assert tenant_user.username == 'tenant_user'
    """
    with schema_context(test_tenant.schema_name):
        user = User.objects.create_user(
            username="tenant_user",
            email="tenant@example.com",
            password="testpass123",
            full_name="Tenant User",
            role="owner",
        )
    return user
