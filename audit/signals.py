"""
Audit Logging Signals
Signals لتسجيل العمليات الحساسة تلقائياً
"""
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from accounting.models import JournalEntry, Account
from sales.models import Invoice, SalesOrder, Harvest
from .utils import log_action, log_financial_transaction, get_client_ip
import inspect


def get_request_from_context():
    """محاولة الحصول على request من thread local (يتم حفظه في Middleware)"""
    import threading
    try:
        thread_local = threading.current_thread()
        if hasattr(thread_local, 'request'):
            return thread_local.request
    except Exception:
        pass
    return None


# ==================== Accounting Signals ====================

@receiver(post_save, sender=JournalEntry)
def log_journal_entry_change(sender, instance, created, **kwargs):
    """تسجيل إنشاء أو تعديل قيد محاسبي"""
    request = get_request_from_context()
    user = getattr(request, 'auth', None) if request else None
    
    action_type = 'create' if created else 'update'
    
    # تحضير البيانات
    new_values = {
        'entry_number': instance.entry_number,
        'entry_date': str(instance.entry_date),
        'description': instance.description,
        'is_posted': instance.is_posted,
        'total_debit': float(instance.total_debit) if hasattr(instance, 'total_debit') else None,
        'total_credit': float(instance.total_credit) if hasattr(instance, 'total_credit') else None,
    }
    
    log_financial_transaction(
        action_type=action_type,
        entity_type='journal_entry',
        entity_id=instance.id,
        entity_description=f"قيد محاسبي {instance.entry_number}",
        user=user,
        old_values=None if created else {},  # TODO: حفظ old values من pre_save
        new_values=new_values,
        description=f"{'إنشاء' if created else 'تعديل'} قيد محاسبي",
        request=request,
    )


@receiver(post_save, sender=Account)
def log_account_change(sender, instance, created, **kwargs):
    """تسجيل إنشاء أو تعديل حساب"""
    request = get_request_from_context()
    user = getattr(request, 'auth', None) if request else None
    
    action_type = 'create' if created else 'update'
    
    log_action(
        action_type=action_type,
        entity_type='account',
        entity_id=instance.id,
        entity_description=f"{instance.code} - {instance.arabic_name}",
        user=user,
        new_values={
            'code': instance.code,
            'name': instance.name,
            'arabic_name': instance.arabic_name,
            'account_type': instance.account_type,
            'balance': float(instance.balance),
        },
        description=f"{'إنشاء' if created else 'تعديل'} حساب",
        request=request,
    )


# ==================== Sales Signals ====================

@receiver(post_save, sender=Invoice)
def log_invoice_change(sender, instance, created, **kwargs):
    """تسجيل إنشاء أو تعديل فاتورة"""
    request = get_request_from_context()
    user = getattr(request, 'auth', None) if request else None
    
    action_type = 'create' if created else 'update'
    
    log_financial_transaction(
        action_type=action_type,
        entity_type='invoice',
        entity_id=instance.id,
        entity_description=f"فاتورة {instance.invoice_number}",
        user=user,
        amount=float(instance.total_amount),
        old_values=None if created else {},
        new_values={
            'invoice_number': instance.invoice_number,
            'total_amount': float(instance.total_amount),
            'vat_amount': float(instance.vat_amount),
            'status': instance.status,
        },
        description=f"{'إنشاء' if created else 'تعديل'} فاتورة",
        request=request,
    )


@receiver(post_save, sender=SalesOrder)
def log_sales_order_change(sender, instance, created, **kwargs):
    """تسجيل إنشاء أو تعديل طلب بيع"""
    request = get_request_from_context()
    user = getattr(request, 'auth', None) if request else None
    
    action_type = 'create' if created else 'update'
    
    log_financial_transaction(
        action_type=action_type,
        entity_type='sales_order',
        entity_id=instance.id,
        entity_description=f"طلب بيع {instance.order_number}",
        user=user,
        amount=float(instance.total_amount),
        new_values={
            'order_number': instance.order_number,
            'customer_name': instance.customer_name,
            'total_amount': float(instance.total_amount),
            'status': instance.status,
        },
        description=f"{'إنشاء' if created else 'تعديل'} طلب بيع",
        request=request,
    )


@receiver(post_save, sender=Harvest)
def log_harvest_change(sender, instance, created, **kwargs):
    """تسجيل إنشاء أو تعديل حصاد"""
    request = get_request_from_context()
    user = getattr(request, 'auth', None) if request else None
    
    action_type = 'create' if created else 'update'
    
    log_financial_transaction(
        action_type=action_type,
        entity_type='harvest',
        entity_id=instance.id,
        entity_description=f"حصاد دفعة {instance.batch.batch_number}",
        user=user,
        amount=float(instance.fair_value),
        new_values={
            'batch_id': instance.batch.id,
            'quantity_kg': float(instance.quantity_kg),
            'fair_value': float(instance.fair_value),
            'status': instance.status,
        },
        description=f"{'إنشاء' if created else 'تعديل'} حصاد",
        request=request,
    )

