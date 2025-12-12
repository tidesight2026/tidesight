"""
Unit Tests للعمليات اليومية
"""
import pytest
from decimal import Decimal
from datetime import date, timedelta
from django.utils import timezone
from biological.models import Species, Pond, Batch
from daily_operations.models import FeedingLog, MortalityLog
from daily_operations.utils import (
    calculate_fcr,
    calculate_estimated_biomass,
    calculate_total_feed_cost,
    calculate_total_mortality,
    get_batch_statistics
)


@pytest.mark.django_db
@pytest.mark.unit
class TestFeedingLog:
    """اختبارات نموذج FeedingLog"""
    
    def test_create_feeding_log(self):
        """اختبار إنشاء سجل تغذية"""
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
        
        from inventory.models import FeedType
        feed_type = FeedType.objects.create(
            name='علف 30% بروتين',
            protein_percentage=Decimal('30.00'),
            unit='kg'
        )
        
        feeding_log = FeedingLog.objects.create(
            batch=batch,
            feed_type=feed_type,
            feeding_date=date.today(),
            quantity=Decimal('50.00'),
            unit_price=Decimal('5.00')
        )
        
        assert feeding_log.batch == batch
        assert feeding_log.total_cost == Decimal('250.00')  # 50 * 5


@pytest.mark.django_db
@pytest.mark.unit
class TestMortalityLog:
    """اختبارات نموذج MortalityLog"""
    
    def test_create_mortality_log(self):
        """اختبار إنشاء سجل نفوق"""
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
        
        mortality_log = MortalityLog.objects.create(
            batch=batch,
            mortality_date=date.today(),
            count=10,
            reason='مرض'
        )
        
        assert mortality_log.batch == batch
        assert mortality_log.count == 10


@pytest.mark.django_db
@pytest.mark.unit
class TestBiologicalUtils:
    """اختبارات Utilities البيولوجية"""
    
    def test_calculate_fcr(self):
        """اختبار حساب FCR"""
        species = Species.objects.create(
            arabic_name='سمك البلطي',
            name='Tilapia'
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
        
        # تحديث الوزن
        batch.current_weight = Decimal('200.00')
        batch.save()
        
        # إضافة علف
        from inventory.models import FeedType
        feed_type = FeedType.objects.create(
            name='علف',
            arabic_name='علف',
            unit='kg'
        )
        
        FeedingLog.objects.create(
            batch=batch,
            feed_type=feed_type,
            feeding_date=date.today(),
            quantity=Decimal('100.00'),
            unit_price=Decimal('5.00')
        )
        
        fcr = calculate_fcr(batch)
        
        # FCR = إجمالي العلف / (الوزن الحالي - الوزن الأولي)
        # 100 / (200 - 100) = 1.0
        assert fcr == Decimal('1.0')
    
    def test_calculate_weight_gain(self):
        """اختبار حساب زيادة الوزن"""
        from daily_operations.utils import calculate_weight_gain
        
        species = Species.objects.create(
            arabic_name='سمك البلطي',
            name='Tilapia'
        )
        pond = Pond.objects.create(
            name='حوض 1',
            pond_type='concrete'
        )
        batch = Batch.objects.create(
            pond=pond,
            species=species,
            batch_number='BATCH-002',
            start_date='2025-01-01',
            initial_count=1000,
            initial_weight=Decimal('100.00'),
            initial_cost=Decimal('5000.00')
        )
        
        batch.current_weight = Decimal('250.00')
        batch.save()
        
        weight_gain = calculate_weight_gain(batch)
        assert weight_gain == Decimal('150.00')
    
    def test_calculate_weight_gain_rate(self):
        """اختبار حساب معدل النمو"""
        from daily_operations.utils import calculate_weight_gain_rate
        from datetime import date, timedelta
        
        species = Species.objects.create(
            arabic_name='سمك البلطي',
            name='Tilapia'
        )
        pond = Pond.objects.create(
            name='حوض 1',
            pond_type='concrete'
        )
        
        # إنشاء دفعة قبل 30 يوم
        start_date = date.today() - timedelta(days=30)
        batch = Batch.objects.create(
            pond=pond,
            species=species,
            batch_number='BATCH-003',
            start_date=start_date,
            initial_count=1000,
            initial_weight=Decimal('100.00'),
            initial_cost=Decimal('5000.00')
        )
        
        batch.current_weight = Decimal('400.00')
        batch.save()
        
        # معدل النمو اليومي = (400 - 100) / 30 = 10 كجم/يوم
        daily_rate = calculate_weight_gain_rate(batch, period='daily')
        assert daily_rate is not None
        assert abs(float(daily_rate) - 10.0) < 0.01
        
        # معدل النمو الأسبوعي = 10 * 7 = 70 كجم/أسبوع
        weekly_rate = calculate_weight_gain_rate(batch, period='weekly')
        assert weekly_rate is not None
        assert abs(float(weekly_rate) - 70.0) < 0.01
    
    def test_calculate_estimated_biomass(self):
        """اختبار حساب الكتلة الحيوية"""
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
        
        biomass = calculate_estimated_biomass(batch.id)
        assert biomass == Decimal('100.00')
    
    def test_calculate_total_feed_cost(self):
        """اختبار حساب إجمالي تكلفة العلف"""
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
        
        from inventory.models import FeedType
        feed_type = FeedType.objects.create(
            name='علف',
            protein_percentage=Decimal('30.00'),
            unit='kg'
        )
        
        FeedingLog.objects.create(
            batch=batch,
            feed_type=feed_type,
            feeding_date=date.today(),
            quantity=Decimal('50.00'),
            unit_price=Decimal('5.00')
        )
        
        FeedingLog.objects.create(
            batch=batch,
            feed_type=feed_type,
            feeding_date=date.today() + timedelta(days=1),
            quantity=Decimal('30.00'),
            unit_price=Decimal('5.00')
        )
        
        total_cost = calculate_total_feed_cost(batch)
        assert total_cost == Decimal('400.00')  # (50 * 5) + (30 * 5)
    
    def test_calculate_total_mortality(self):
        """اختبار حساب إجمالي النفوق"""
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
        
        MortalityLog.objects.create(
            batch=batch,
            mortality_date=date.today(),
            count=10
        )
        
        MortalityLog.objects.create(
            batch=batch,
            mortality_date=date.today() + timedelta(days=1),
            count=5
        )
        
        total_mortality = calculate_total_mortality(batch)
        assert total_mortality == 15
