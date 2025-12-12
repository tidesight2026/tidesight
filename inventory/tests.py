"""
Unit Tests للمخزون
"""
import pytest
from decimal import Decimal
from inventory.models import FeedType, FeedInventory, Medicine, MedicineInventory


@pytest.mark.django_db
@pytest.mark.unit
class TestFeedTypeModel:
    """اختبارات نموذج نوع العلف"""
    
    def test_create_feed_type(self):
        """اختبار إنشاء نوع علف"""
        feed_type = FeedType.objects.create(
            name='علف 30% بروتين',
            protein_percentage=Decimal('30.00'),
            unit='kg'
        )
        
        assert feed_type.name == 'علف 30% بروتين'
        assert feed_type.protein_percentage == Decimal('30.00')
        assert feed_type.is_active is True


@pytest.mark.django_db
@pytest.mark.unit
class TestFeedInventoryModel:
    """اختبارات نموذج مخزون العلف"""
    
    def test_create_feed_inventory(self):
        """اختبار إنشاء مخزون علف"""
        feed_type = FeedType.objects.create(
            name='علف 30%',
            protein_percentage=Decimal('30.00'),
            unit='kg'
        )
        
        inventory = FeedInventory.objects.create(
            feed_type=feed_type,
            quantity=Decimal('1000.00'),
            unit_cost=Decimal('5.00'),
            expiry_date=None
        )
        
        assert inventory.feed_type == feed_type
        assert inventory.quantity == Decimal('1000.00')
        assert inventory.total_value == Decimal('5000.00')  # 1000 * 5
    
    def test_feed_inventory_deduction(self):
        """اختبار خصم من المخزون"""
        feed_type = FeedType.objects.create(
            name='علف 30%',
            protein_percentage=Decimal('30.00'),
            unit='kg'
        )
        
        inventory = FeedInventory.objects.create(
            feed_type=feed_type,
            quantity=Decimal('1000.00'),
            unit_cost=Decimal('5.00')
        )
        
        # خصم 100 كجم
        inventory.quantity -= Decimal('100.00')
        inventory.save()
        
        assert inventory.quantity == Decimal('900.00')
        assert inventory.total_value == Decimal('4500.00')  # 900 * 5


@pytest.mark.django_db
@pytest.mark.unit
class TestMedicineModel:
    """اختبارات نموذج الدواء"""
    
    def test_create_medicine(self):
        """اختبار إنشاء دواء"""
        medicine = Medicine.objects.create(
            name='دواء تجريبي',
            active_ingredient='مادة فعالة',
            dosage_unit='ml'
        )
        
        assert medicine.name == 'دواء تجريبي'
        assert medicine.is_active is True


@pytest.mark.django_db
@pytest.mark.unit
class TestMedicineInventoryModel:
    """اختبارات نموذج مخزون الأدوية"""
    
    def test_create_medicine_inventory(self):
        """اختبار إنشاء مخزون دواء"""
        medicine = Medicine.objects.create(
            name='دواء تجريبي',
            active_ingredient='مادة فعالة',
            dosage_unit='ml'
        )
        
        inventory = MedicineInventory.objects.create(
            medicine=medicine,
            quantity=Decimal('100.00'),
            unit_cost=Decimal('10.00'),
            expiry_date=None
        )
        
        assert inventory.medicine == medicine
        assert inventory.quantity == Decimal('100.00')
        assert inventory.total_value == Decimal('1000.00')  # 100 * 10
