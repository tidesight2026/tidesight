"""
Unit Tests للبيانات البيولوجية
"""
import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from biological.models import Species, Pond, Batch, FarmLocation


@pytest.mark.django_db
@pytest.mark.unit
class TestSpeciesModel:
    """اختبارات نموذج الأنواع السمكية"""
    
    def test_create_species(self):
        """اختبار إنشاء نوع سمكي"""
        species = Species.objects.create(
            arabic_name='سمك البلطي',
            english_name='Tilapia',
            scientific_name='Oreochromis niloticus',
            typical_growth_rate=Decimal('0.5'),
            typical_fcr=Decimal('1.5')
        )
        
        assert species.arabic_name == 'سمك البلطي'
        assert species.is_active is True
    
    def test_species_str(self):
        """اختبار __str__ method"""
        species = Species.objects.create(
            arabic_name='سمك البلطي',
            english_name='Tilapia'
        )
        
        assert str(species) == 'سمك البلطي'


@pytest.mark.django_db
@pytest.mark.unit
class TestPondModel:
    """اختبارات نموذج الأحواض"""
    
    def test_create_pond(self):
        """اختبار إنشاء حوض"""
        pond = Pond.objects.create(
            name='حوض 1',
            pond_type='concrete',
            capacity=Decimal('1000.00'),
            status='empty'
        )
        
        assert pond.name == 'حوض 1'
        assert pond.status == 'empty'
    
    def test_pond_str(self):
        """اختبار __str__ method"""
        pond = Pond.objects.create(
            name='حوض 1',
            pond_type='concrete'
        )
        
        assert 'حوض 1' in str(pond)


@pytest.mark.django_db
@pytest.mark.unit
class TestBatchModel:
    """اختبارات نموذج الدفعات"""
    
    def test_create_batch(self):
        """اختبار إنشاء دفعة"""
        species = Species.objects.create(
            arabic_name='سمك البلطي',
            english_name='Tilapia'
        )
        pond = Pond.objects.create(
            name='حوض 1',
            pond_type='concrete'
        )
        
        batch = Batch.objects.create(
            pond=pond,
            species=species,
            batch_number='BATCH-001',
            start_date='2025-01-01',
            initial_count=1000,
            initial_weight=Decimal('100.00'),
            initial_cost=Decimal('5000.00')
        )
        
        assert batch.batch_number == 'BATCH-001'
        assert batch.status == 'active'
        assert batch.current_count == 1000
        assert batch.current_weight == Decimal('100.00')
    
    def test_batch_calculate_mortality_rate(self):
        """اختبار حساب معدل النفوق"""
        species = Species.objects.create(
            arabic_name='سمك البلطي',
            english_name='Tilapia'
        )
        pond = Pond.objects.create(
            name='حوض 1',
            pond_type='concrete'
        )
        
        batch = Batch.objects.create(
            pond=pond,
            species=species,
            batch_number='BATCH-001',
            start_date='2025-01-01',
            initial_count=1000,
            initial_weight=Decimal('100.00'),
            initial_cost=Decimal('5000.00')
        )
        
        # تحديث العدد الحي بعد نفوق 50 سمكة
        batch.current_count = 950
        batch.save()
        
        assert batch.mortality_rate == Decimal('5.00')  # 5%
    
    def test_batch_average_weight(self):
        """اختبار حساب متوسط الوزن"""
        species = Species.objects.create(
            arabic_name='سمك البلطي',
            english_name='Tilapia'
        )
        pond = Pond.objects.create(
            name='حوض 1',
            pond_type='concrete'
        )
        
        batch = Batch.objects.create(
            pond=pond,
            species=species,
            batch_number='BATCH-001',
            start_date='2025-01-01',
            initial_count=1000,
            initial_weight=Decimal('100.00'),
            initial_cost=Decimal('5000.00')
        )
        
        # تحديث الوزن الحالي
        batch.current_weight = Decimal('200.00')
        batch.current_count = 950
        batch.save()
        
        # متوسط الوزن = الوزن الحالي / العدد الحالي
        expected_avg = Decimal('200.00') / Decimal('950')
        assert batch.average_weight == expected_avg
