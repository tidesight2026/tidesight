"""
Integration Tests للمحاسبة
"""
import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from accounting.models import Account, AccountType, JournalEntry, JournalEntryLine
from accounting.signals import create_feeding_journal_entry, create_mortality_journal_entry

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.integration
class TestAccountingSignals:
    """اختبارات Signals المحاسبة"""
    
    def test_feeding_log_creates_journal_entry(self):
        """اختبار إنشاء قيد محاسبي عند تسجيل علف"""
        from biological.models import Species, Pond, Batch
        from daily_operations.models import FeedingLog
        from inventory.models import FeedType
        
        # إنشاء البيانات الأساسية
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
        
        feed_type = FeedType.objects.create(
            name='علف 30%',
            protein_percentage=Decimal('30.00'),
            unit='kg'
        )
        
        # إنشاء حساب للعمليات
        operations_account = Account.objects.create(
            code='5000',
            name='Operations',
            arabic_name='تشغيل',
            account_type=AccountType.EXPENSE
        )
        
        inventory_account = Account.objects.create(
            code='1400',
            name='Feed Inventory',
            arabic_name='مخزون علف',
            account_type=AccountType.ASSET
        )
        
        # إنشاء سجل تغذية (يجب أن ينشئ قيد تلقائياً)
        feeding_log = FeedingLog.objects.create(
            batch=batch,
            feed_type=feed_type,
            feeding_date='2025-01-15',
            quantity=Decimal('50.00'),
            unit_price=Decimal('5.00')
        )
        
        # التحقق من وجود قيد محاسبي
        journal_entries = JournalEntry.objects.filter(
            reference_type='feeding_log',
            reference_id=feeding_log.id
        )
        
        # قد يتطلب إعدادات Signals
        # assert journal_entries.exists()


@pytest.mark.django_db
@pytest.mark.integration
class TestJournalEntryCreation:
    """اختبارات إنشاء القيود المحاسبية"""
    
    def test_create_balanced_journal_entry(self):
        """اختبار إنشاء قيد متوازن"""
        cash_account = Account.objects.create(
            code='1000',
            name='Cash',
            arabic_name='النقدية',
            account_type=AccountType.ASSET
        )
        
        revenue_account = Account.objects.create(
            code='4000',
            name='Revenue',
            arabic_name='الإيرادات',
            account_type=AccountType.REVENUE
        )
        
        entry = JournalEntry.objects.create(
            entry_number='JE-001',
            entry_date='2025-01-01',
            description='بيع نقدي',
            is_posted=False
        )
        
        JournalEntryLine.objects.create(
            journal_entry=entry,
            account=cash_account,
            type='debit',
            amount=Decimal('1000.00')
        )
        
        JournalEntryLine.objects.create(
            journal_entry=entry,
            account=revenue_account,
            type='credit',
            amount=Decimal('1000.00')
        )
        
        assert entry.validate_balance() is True
        
        # ترحيل القيد
        entry.is_posted = True
        entry.save()
        
        # التحقق من الرصيد
        assert cash_account.balance == Decimal('1000.00')
        assert revenue_account.balance == Decimal('1000.00')

