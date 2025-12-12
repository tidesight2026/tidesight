"""
Unit Tests للمحاسبة
"""
import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from accounting.models import Account, AccountType, JournalEntry, JournalEntryLine


@pytest.mark.django_db
@pytest.mark.unit
class TestAccountModel:
    """اختبارات نموذج الحساب"""
    
    def test_create_account(self):
        """اختبار إنشاء حساب"""
        account = Account.objects.create(
            code='1000',
            name='Cash',
            arabic_name='النقدية',
            account_type=AccountType.ASSET
        )
        
        assert account.code == '1000'
        assert account.account_type == AccountType.ASSET
        assert account.is_active is True
    
    def test_account_balance_property(self):
        """اختبار حساب رصيد الحساب"""
        account = Account.objects.create(
            code='1000',
            name='Cash',
            arabic_name='النقدية',
            account_type=AccountType.ASSET
        )
        
        # إنشاء قيد
        entry = JournalEntry.objects.create(
            entry_number='JE-001',
            entry_date='2025-01-01',
            description='Test Entry',
            is_posted=True
        )
        
        JournalEntryLine.objects.create(
            journal_entry=entry,
            account=account,
            type='debit',
            amount=Decimal('1000.00')
        )
        
        # رصيد الأصل = مدين - دائن
        assert account.balance == Decimal('1000.00')


@pytest.mark.django_db
@pytest.mark.unit
class TestJournalEntryModel:
    """اختبارات نموذج القيد المحاسبي"""
    
    def test_create_journal_entry(self):
        """اختبار إنشاء قيد محاسبي"""
        entry = JournalEntry.objects.create(
            entry_number='JE-001',
            entry_date='2025-01-01',
            description='Test Entry',
            is_posted=False
        )
        
        assert entry.entry_number == 'JE-001'
        assert entry.is_posted is False
    
    def test_journal_entry_validate_balance(self):
        """اختبار التحقق من توازن القيد"""
        # إنشاء حسابات
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
        
        # إنشاء قيد متوازن
        entry = JournalEntry.objects.create(
            entry_number='JE-001',
            entry_date='2025-01-01',
            description='Test Entry',
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
    
    def test_journal_entry_unbalanced_fails(self):
        """اختبار فشل القيد غير المتوازن"""
        cash_account = Account.objects.create(
            code='1000',
            name='Cash',
            arabic_name='النقدية',
            account_type=AccountType.ASSET
        )
        
        entry = JournalEntry.objects.create(
            entry_number='JE-001',
            entry_date='2025-01-01',
            description='Test Entry',
            is_posted=False
        )
        
        JournalEntryLine.objects.create(
            journal_entry=entry,
            account=cash_account,
            type='debit',
            amount=Decimal('1000.00')
        )
        
        # القيد غير متوازن (لا يوجد دائن)
        assert entry.validate_balance() is False
