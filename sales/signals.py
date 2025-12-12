"""
Django Signals للربط بين المبيعات والمحاسبة
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from datetime import date

from .models import Harvest, SalesOrder, Invoice
from .zatca import generate_invoice_qr_code, generate_invoice_xml
from accounting.models import Account, JournalEntry, JournalEntryLine


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
    from django.db.models import Sum
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


@receiver(post_save, sender=Harvest)
def create_harvest_journal_entry(sender, instance, created, **kwargs):
    """
    عند الحصاد، يتم تحويل الأصل البيولوجي إلى مخزون منتج تام:
    من: ح/ مخزون منتج تام (مدين)
    إلى: ح/ الأصول البيولوجية (دائن)
    """
    if not created or instance.status != 'completed':
        return
    
    try:
        # الحصول على الحسابات
        finished_goods_account = get_or_create_account(
            '1160',
            'Finished Goods',
            'مخزون منتج تام',
            'asset'
        )
        
        biological_asset_account = get_or_create_account(
            '1310',
            'Active Batches',
            'الدفعات النشطة',
            'biological_asset'
        )
        
        # استخدام القيمة العادلة أو حساب التكلفة
        value = instance.fair_value if instance.fair_value > 0 else (instance.cost_per_kg * instance.quantity_kg)
        
        # إنشاء رقم القيد
        entry_number = f"HARV-{instance.id}-{instance.harvest_date.strftime('%Y%m%d')}"
        
        # إنشاء القيد
        create_journal_entry(
            entry_number=entry_number,
            entry_date=instance.harvest_date,
            description=f"حصاد {instance.quantity_kg} كجم من الدفعة {instance.batch.batch_number}",
            reference_type='harvest',
            reference_id=instance.id,
            lines=[
                {
                    'account': finished_goods_account,
                    'type': 'debit',
                    'amount': float(value),
                    'description': f"{instance.quantity_kg} كجم @ {instance.cost_per_kg} ريال/كجم",
                },
                {
                    'account': biological_asset_account,
                    'type': 'credit',
                    'amount': float(value),
                    'description': f"تحويل من أصل بيولوجي",
                },
            ],
            created_by=instance.created_by,
        )
        
        # تحديث حالة الدفعة
        if instance.batch.current_count <= instance.count:
            instance.batch.status = 'harvested'
            instance.batch.current_count = 0
            instance.batch.current_weight = Decimal('0.00')
            instance.batch.save(update_fields=['status', 'current_count', 'current_weight'])
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating journal entry for harvest {instance.id}: {str(e)}")


@receiver(post_save, sender=Invoice)
def generate_zatca_data(sender, instance, created, **kwargs):
    """
    توليد QR Code و XML عند إصدار الفاتورة
    """
    if not created or instance.status != 'issued':
        return
    
    try:
        # TODO: جلب بيانات البائع من إعدادات Tenant
        seller_name = "AquaERP Farm"  # يجب جلبها من إعدادات Tenant
        seller_vat_number = "123456789012345"  # يجب جلبها من إعدادات Tenant
        
        # توليد QR Code
        qr_code = generate_invoice_qr_code(instance, seller_name, seller_vat_number)
        instance.qr_code = qr_code
        
        # توليد XML
        xml_string = generate_invoice_xml(instance, seller_name, seller_vat_number)
        instance.signed_xml = xml_string
        
        # توليد UUID (يمكن استخدام UUID من ZATCA API لاحقاً)
        import uuid
        instance.uuid = str(uuid.uuid4())
        
        instance.save(update_fields=['qr_code', 'signed_xml', 'uuid'])
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"ZATCA data generated for invoice {instance.id}")
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error generating ZATCA data for invoice {instance.id}: {str(e)}")


@receiver(post_save, sender=Invoice)
def create_invoice_journal_entry(sender, instance, created, **kwargs):
    """
    عند إصدار فاتورة، يتم إنشاء قيد محاسبي:
    من: ح/ العملاء (مدين)
    إلى: ح/ إيرادات المبيعات (دائن)
    إلى: ح/ الضريبة المستحقة (دائن)
    """
    if not created or instance.status != 'issued':
        return
    
    try:
        # الحصول على الحسابات
        accounts_receivable = get_or_create_account(
            '1130',
            'Accounts Receivable',
            'العملاء',
            'asset'
        )
        
        sales_revenue = get_or_create_account(
            '4110',
            'Fish Sales',
            'مبيعات السمك',
            'revenue'
        )
        
        tax_payable = get_or_create_account(
            '2120',
            'Tax Payable',
            'الضرائب المستحقة',
            'liability'
        )
        
        cost_of_goods = get_or_create_account(
            '5100',
            'Cost of Goods Sold',
            'تكلفة البضاعة المباعة',
            'expense'
        )
        
        finished_goods = get_or_create_account(
            '1160',
            'Finished Goods',
            'مخزون منتج تام',
            'asset'
        )
        
        # إنشاء رقم القيد
        entry_number = f"INV-{instance.id}-{instance.invoice_date.strftime('%Y%m%d')}"
        
        # حساب تكلفة البضاعة المباعة
        sales_order = instance.sales_order
        total_cost = Decimal('0.00')
        
        for line in sales_order.lines.all():
            if line.harvest:
                cost = line.harvest.cost_per_kg * line.quantity_kg
                total_cost += cost
        
        lines = [
            {
                'account': accounts_receivable,
                'type': 'debit',
                'amount': float(instance.total_amount),
                'description': f"فاتورة {instance.invoice_number}",
            },
            {
                'account': sales_revenue,
                'type': 'credit',
                'amount': float(instance.subtotal),
                'description': f"مبيعات",
            },
            {
                'account': tax_payable,
                'type': 'credit',
                'amount': float(instance.vat_amount),
                'description': f"ضريبة القيمة المضافة",
            },
        ]
        
        # إضافة قيد تكلفة البضاعة المباعة إذا كان هناك حصاد
        if total_cost > 0:
            lines.extend([
                {
                    'account': cost_of_goods,
                    'type': 'debit',
                    'amount': float(total_cost),
                    'description': f"تكلفة البضاعة المباعة",
                },
                {
                    'account': finished_goods,
                    'type': 'credit',
                    'amount': float(total_cost),
                    'description': f"خصم من المخزون",
                },
            ])
        
        # إنشاء القيد
        create_journal_entry(
            entry_number=entry_number,
            entry_date=instance.invoice_date,
            description=f"فاتورة {instance.invoice_number} - {sales_order.customer_name}",
            reference_type='invoice',
            reference_id=instance.id,
            lines=lines,
            created_by=instance.created_by,
        )
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating journal entry for invoice {instance.id}: {str(e)}")

