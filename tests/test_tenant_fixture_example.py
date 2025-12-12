"""
مثال على استخدام Tenant Fixtures في الاختبارات
"""
import pytest
from decimal import Decimal
from django_tenants.utils import schema_context
from inventory.models import FeedType, FeedInventory
from accounts.models import User


def test_feed_type_creation(test_tenant):
    """
    مثال: استخدام test_tenant fixture
    
    ⚠️ مهم: يجب استخدام schema_context عند الوصول إلى نماذج tenant
    """
    with schema_context(test_tenant.schema_name):
        # إنشاء FeedType داخل tenant schema
        feed_type = FeedType.objects.create(
            name="Protein 45%",
            arabic_name="بروتين 45%",
            protein_percentage=Decimal('45.00'),
            unit="كجم",
            description="High quality feed"
        )
        
        assert feed_type.id is not None
        assert feed_type.name == "Protein 45%"
        assert FeedType.objects.count() == 1


def test_feed_inventory_with_context(test_tenant, tenant_schema_context):
    """
    مثال: استخدام tenant_schema_context fixture
    """
    with tenant_schema_context:
        # جميع العمليات هنا تتم داخل tenant schema
        feed_type = FeedType.objects.create(
            name="Protein 45%",
            arabic_name="بروتين 45%",
            protein_percentage=Decimal('45.00'),
            unit="كجم"
        )
        
        feed_inventory = FeedInventory.objects.create(
            feed_type=feed_type,
            quantity=Decimal('1000.00'),
            unit_price=Decimal('5.00')
        )
        
        assert feed_inventory.id is not None
        assert feed_inventory.quantity == Decimal('1000.00')
        assert feed_inventory.feed_type == feed_type


def test_with_user(test_tenant, tenant_user):
    """
    مثال: استخدام tenant_user fixture
    """
    with schema_context(test_tenant.schema_name):
        # tenant_user متاح داخل tenant schema
        assert tenant_user.username == 'tenant_user'
        assert tenant_user.role == 'owner'
        
        # يمكن استخدامه في الاختبارات
        feed_type = FeedType.objects.create(
            name="Test Feed",
            arabic_name="علف تجريبي",
            protein_percentage=Decimal('45.00'),
            unit="كجم"
        )
        
        assert feed_type.id is not None

