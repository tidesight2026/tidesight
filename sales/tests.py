"""
Unit Tests للمبيعات
"""
import pytest
from decimal import Decimal
from datetime import date
from biological.models import Species, Pond, Batch
from sales.models import Harvest, SalesOrder, SalesOrderLine, Invoice


@pytest.mark.django_db
@pytest.mark.unit
class TestHarvestModel:
    """اختبارات نموذج الحصاد"""
    
    def test_create_harvest(self):
        """اختبار إنشاء حصاد"""
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
        
        harvest = Harvest.objects.create(
            batch=batch,
            harvest_date=date.today(),
            quantity_kg=Decimal('500.00'),
            fair_value=Decimal('12500.00'),
            status='completed'
        )
        
        assert harvest.batch == batch
        assert harvest.quantity_kg == Decimal('500.00')
        assert harvest.status == 'completed'


@pytest.mark.django_db
@pytest.mark.unit
class TestSalesOrderModel:
    """اختبارات نموذج طلب البيع"""
    
    def test_create_sales_order(self):
        """اختبار إنشاء طلب بيع"""
        order = SalesOrder.objects.create(
            order_number='SO-001',
            order_date=date.today(),
            customer_name='عميل تجريبي',
            customer_phone='0501234567',
            vat_rate=Decimal('0.15')
        )
        
        assert order.order_number == 'SO-001'
        assert order.status == 'draft'
        assert order.vat_rate == Decimal('0.15')
    
    def test_sales_order_total(self):
        """اختبار حساب إجمالي طلب البيع"""
        order = SalesOrder.objects.create(
            order_number='SO-001',
            order_date=date.today(),
            customer_name='عميل تجريبي',
            vat_rate=Decimal('0.15')
        )
        
        # إضافة حصاد
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
        
        harvest = Harvest.objects.create(
            batch=batch,
            harvest_date=date.today(),
            quantity_kg=Decimal('100.00'),
            fair_value=Decimal('2500.00'),
            status='completed'
        )
        
        # إضافة بند
        line = SalesOrderLine.objects.create(
            sales_order=order,
            harvest=harvest,
            quantity_kg=Decimal('100.00'),
            unit_price=Decimal('25.00')
        )
        
        # حساب الإجمالي
        subtotal = order.subtotal
        vat_amount = order.vat_amount
        total = order.total_amount
        
        assert subtotal == Decimal('2500.00')
        assert vat_amount == Decimal('375.00')  # 2500 * 0.15
        assert total == Decimal('2875.00')


@pytest.mark.django_db
@pytest.mark.unit
class TestInvoiceModel:
    """اختبارات نموذج الفاتورة"""
    
    def test_create_invoice(self):
        """اختبار إنشاء فاتورة"""
        order = SalesOrder.objects.create(
            order_number='SO-001',
            order_date=date.today(),
            customer_name='عميل تجريبي',
            vat_rate=Decimal('0.15')
        )
        
        invoice = Invoice.objects.create(
            sales_order=order,
            invoice_date=date.today(),
            invoice_number='INV-001'
        )
        
        assert invoice.sales_order == order
        assert invoice.invoice_number == 'INV-001'
        assert invoice.status == 'draft'
        assert invoice.total_amount == order.total_amount
