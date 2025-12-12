"""
Django Signals للربط الآلي بين العمليات والمحاسبة
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from decimal import Decimal
from datetime import date

from .models import Account, JournalEntry, JournalEntryLine
from daily_operations.models import FeedingLog, MortalityLog


def get_or_create_account(code: str, name: str, arabic_name: str, account_type: str):
    """الحصول على حساب أو إنشاؤه إذا لم يكن موجوداً"""
    account, created = Account.objects.get_or_create(
        code=code,
        defaults={
            'name': name,
            'arabic_name': arabic_name,
            'account_type': account_type,
            'is_active': True,
        }
    )
    return account


def create_journal_entry(
    entry_number: str,
    entry_date: date,
    description: str,
    reference_type: str,
    reference_id: int,
    lines: list,
    created_by=None
):
    """إنشاء قيد محاسبي مع بنوده"""
    # التحقق من التوازن
    total_debit = sum(line['amount'] for line in lines if line['type'] == 'debit')
    total_credit = sum(line['amount'] for line in lines if line['type'] == 'credit')
    
    if total_debit != total_credit:
        raise ValueError(f"القيد غير متوازن! المدين: {total_debit}, الدائن: {total_credit}")
    
    # إنشاء القيد
    entry = JournalEntry.objects.create(
        entry_number=entry_number,
        entry_date=entry_date,
        description=description,
        reference_type=reference_type,
        reference_id=reference_id,
        is_posted=True,
        created_by=created_by,
    )
    
    # إنشاء بنود القيد
    for line_data in lines:
        JournalEntryLine.objects.create(
            journal_entry=entry,
            account=line_data['account'],
            type=line_data['type'],
            amount=Decimal(str(line_data['amount'])),
            description=line_data.get('description'),
        )
    
    return entry


@receiver(post_save, sender=FeedingLog)
def create_feeding_journal_entry(sender, instance, created, **kwargs):
    """
    عند تسجيل تغذية، يتم إنشاء قيد محاسبي:
    من: ح/ تكاليف تشغيل الدفعات (مدين)
    إلى: ح/ مخزون الأعلاف (دائن)
    """
    if not created or instance.is_posted or getattr(instance, '_skip_accounting_signal', False):
        return
    
    try:
        # الحصول على الحسابات
        operating_cost_account = get_or_create_account(
            '5120',
            'Batch Operating Costs',
            'تكاليف تشغيل الدفعات',
            'expense'
        )
        
        feed_inventory_account = get_or_create_account(
            '1140',
            'Feed Inventory',
            'مخزون الأعلاف',
            'asset'
        )
        
        # إنشاء رقم القيد
        entry_number = f"FEED-{instance.id}-{instance.feeding_date.strftime('%Y%m%d')}"
        
        # إنشاء القيد
        create_journal_entry(
            entry_number=entry_number,
            entry_date=instance.feeding_date,
            description=f"تغذية دفعة {instance.batch.batch_number} - {instance.feed_type.arabic_name}",
            reference_type='feeding_log',
            reference_id=instance.id,
            lines=[
                {
                    'account': operating_cost_account,
                    'type': 'debit',
                    'amount': float(instance.total_cost),
                    'description': f"علف: {instance.quantity} كجم × {instance.unit_price} ريال",
                },
                {
                    'account': feed_inventory_account,
                    'type': 'credit',
                    'amount': float(instance.total_cost),
                    'description': f"خصم من المخزون",
                },
            ],
            created_by=instance.created_by,
        )
        
        # تحديث حالة التسجيل
        instance._state.adding = False
        instance.is_posted = True
        instance.save(update_fields=['is_posted'])
        
    except Exception as e:
        # Log error but don't break the save
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating journal entry for feeding log {instance.id}: {str(e)}")


@receiver(post_save, sender=MortalityLog)
def create_mortality_journal_entry(sender, instance, created, **kwargs):
    """
    عند تسجيل نفوق، يتم إنشاء قيد محاسبي:
    من: ح/ خسائر النفوق (مدين)
    إلى: ح/ الأصول البيولوجية (دائن)
    """
    if not created:
        return
    
    try:
        # حساب قيمة النفوق (متوسط الوزن × العدد)
        mortality_value = Decimal('0.00')
        if instance.average_weight and instance.average_weight > 0:
            mortality_value = Decimal(str(instance.average_weight)) * instance.count
        else:
            # إذا لم يتم تحديد الوزن، نستخدم متوسط وزن الدفعة
            if instance.batch.current_count > 0:
                avg_weight = instance.batch.current_weight / instance.batch.current_count
                mortality_value = avg_weight * instance.count
        
        if mortality_value <= 0:
            return  # لا ننشئ قيداً إذا كانت القيمة صفر
        
        # الحصول على الحسابات
        mortality_loss_account = get_or_create_account(
            '5210',
            'Mortality Loss',
            'خسائر النفوق',
            'expense'
        )
        
        biological_asset_account = get_or_create_account(
            '1310',
            'Active Batches',
            'الدفعات النشطة',
            'biological_asset'
        )
        
        # إنشاء رقم القيد
        entry_number = f"MORT-{instance.id}-{instance.mortality_date.strftime('%Y%m%d')}"
        
        # إنشاء القيد
        create_journal_entry(
            entry_number=entry_number,
            entry_date=instance.mortality_date,
            description=f"نفوق {instance.count} سمكة من الدفعة {instance.batch.batch_number}",
            reference_type='mortality_log',
            reference_id=instance.id,
            lines=[
                {
                    'account': mortality_loss_account,
                    'type': 'debit',
                    'amount': float(mortality_value),
                    'description': f"{instance.count} سمكة × {instance.average_weight if instance.average_weight else 'متوسط'} كجم",
                },
                {
                    'account': biological_asset_account,
                    'type': 'credit',
                    'amount': float(mortality_value),
                    'description': f"تقليل قيمة الأصل البيولوجي",
                },
            ],
            created_by=instance.created_by,
        )
        
    except Exception as e:
        # Log error but don't break the save
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating journal entry for mortality log {instance.id}: {str(e)}")

