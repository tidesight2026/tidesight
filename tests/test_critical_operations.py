"""
اختبارات العمليات الحرجة - تغذية، نفوق، حصاد، فواتير
"""
import pytest
from decimal import Decimal
from datetime import date, timedelta
from django.test import TestCase

from biological.models import Batch, Species, Pond
from daily_operations.models import FeedingLog, MortalityLog
from inventory.models import FeedType
from sales.models import Harvest, SalesOrder, SalesOrderLine, Invoice
from accounts.models import User


@pytest.mark.django_db
class TestFeedingOperation:
    """اختبارات تسجيل التغذية"""
    
    def setup_method(self):
        """إعداد البيانات للاختبار"""
        self.species = Species.objects.create(
            name='Tilapia',
            arabic_name='سمك البلطي'
        )
        self.pond = Pond.objects.create(
            name='حوض 1',
            pond_type='concrete',
            capacity=Decimal('1000.00')
        )
        self.batch = Batch.objects.create(
            pond=self.pond,
            species=self.species,
            batch_number='BATCH-TEST-001',
            start_date=date.today() - timedelta(days=30),
            initial_count=1000,
            initial_weight=Decimal('100.00'),
            initial_cost=Decimal('5000.00'),
            current_count=1000,
            current_weight=Decimal('100.00')
        )
        self.feed_type = FeedType.objects.create(
            name='Feed',
            arabic_name='علف',
            unit='kg'
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_feeding_log(self):
        """اختبار إنشاء سجل تغذية"""
        feeding_log = FeedingLog.objects.create(
            batch=self.batch,
            feed_type=self.feed_type,
            feeding_date=date.today(),
            quantity=Decimal('50.00'),
            unit_price=Decimal('5.00'),
            created_by=self.user
        )
        
        assert feeding_log.id is not None
        assert feeding_log.total_cost == Decimal('250.00')  # 50 * 5
        assert feeding_log.batch == self.batch
        assert feeding_log.feed_type == self.feed_type
    
    def test_feeding_log_updates_batch(self):
        """اختبار أن سجل التغذية يؤثر على الدفعة"""
        initial_weight = self.batch.current_weight
        
        FeedingLog.objects.create(
            batch=self.batch,
            feed_type=self.feed_type,
            feeding_date=date.today(),
            quantity=Decimal('50.00'),
            unit_price=Decimal('5.00'),
            created_by=self.user
        )
        
        # التحقق من أن السجل تم إنشاؤه
        assert FeedingLog.objects.filter(batch=self.batch).count() == 1


@pytest.mark.django_db
class TestMortalityOperation:
    """اختبارات تسجيل النفوق"""
    
    def setup_method(self):
        """إعداد البيانات للاختبار"""
        self.species = Species.objects.create(
            name='Tilapia',
            arabic_name='سمك البلطي'
        )
        self.pond = Pond.objects.create(
            name='حوض 1',
            pond_type='concrete',
            capacity=Decimal('1000.00')
        )
        self.batch = Batch.objects.create(
            pond=self.pond,
            species=self.species,
            batch_number='BATCH-TEST-002',
            start_date=date.today() - timedelta(days=30),
            initial_count=1000,
            initial_weight=Decimal('100.00'),
            initial_cost=Decimal('5000.00'),
            current_count=1000,
            current_weight=Decimal('100.00')
        )
        self.user = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
    
    def test_create_mortality_log(self):
        """اختبار إنشاء سجل نفوق"""
        mortality_log = MortalityLog.objects.create(
            batch=self.batch,
            mortality_date=date.today(),
            count=50,
            cause='مرض',
            created_by=self.user
        )
        
        assert mortality_log.id is not None
        assert mortality_log.batch == self.batch
        assert mortality_log.count == 50
        assert mortality_log.cause == 'مرض'
    
    def test_mortality_log_updates_batch(self):
        """اختبار أن سجل النفوق يؤثر على الدفعة"""
        initial_count = self.batch.current_count
        
        MortalityLog.objects.create(
            batch=self.batch,
            mortality_date=date.today(),
            count=50,
            created_by=self.user
        )
        
        # التحقق من أن السجل تم إنشاؤه
        assert MortalityLog.objects.filter(batch=self.batch).count() == 1


@pytest.mark.django_db
class TestHarvestOperation:
    """اختبارات تسجيل الحصاد"""
    
    def setup_method(self):
        """إعداد البيانات للاختبار"""
        self.species = Species.objects.create(
            name='Tilapia',
            arabic_name='سمك البلطي'
        )
        self.pond = Pond.objects.create(
            name='حوض 1',
            pond_type='concrete',
            capacity=Decimal('1000.00')
        )
        self.batch = Batch.objects.create(
            pond=self.pond,
            species=self.species,
            batch_number='BATCH-TEST-003',
            start_date=date.today() - timedelta(days=120),
            initial_count=1000,
            initial_weight=Decimal('100.00'),
            initial_cost=Decimal('5000.00'),
            current_count=950,
            current_weight=Decimal('500.00')
        )
        self.user = User.objects.create_user(
            username='testuser3',
            email='test3@example.com',
            password='testpass123'
        )
    
    def test_create_harvest(self):
        """اختبار إنشاء حصاد"""
        harvest = Harvest.objects.create(
            batch=self.batch,
            harvest_date=date.today(),
            quantity_kg=Decimal('200.00'),
            count=200,
            average_weight=Decimal('1.00'),
            fair_value=Decimal('3000.00'),
            cost_per_kg=Decimal('15.00'),
            status='completed',
            created_by=self.user
        )
        
        assert harvest.id is not None
        assert harvest.batch == self.batch
        assert harvest.quantity_kg == Decimal('200.00')
        assert harvest.status == 'completed'
    
    def test_harvest_links_to_batch(self):
        """اختبار ربط الحصاد بالدفعة"""
        harvest = Harvest.objects.create(
            batch=self.batch,
            harvest_date=date.today(),
            quantity_kg=Decimal('200.00'),
            count=200,
            average_weight=Decimal('1.00'),
            fair_value=Decimal('3000.00'),
            cost_per_kg=Decimal('15.00'),
            status='completed',
            created_by=self.user
        )
        
        # التحقق من الربط
        assert harvest.batch == self.batch
        assert harvest in self.batch.harvests.all()


@pytest.mark.django_db
class TestInvoiceOperation:
    """اختبارات إنشاء فاتورة مرتبطة بدفعة"""
    
    def setup_method(self):
        """إعداد البيانات للاختبار"""
        self.species = Species.objects.create(
            name='Tilapia',
            arabic_name='سمك البلطي'
        )
        self.pond = Pond.objects.create(
            name='حوض 1',
            pond_type='concrete',
            capacity=Decimal('1000.00')
        )
        self.batch = Batch.objects.create(
            pond=self.pond,
            species=self.species,
            batch_number='BATCH-TEST-004',
            start_date=date.today() - timedelta(days=120),
            initial_count=1000,
            initial_weight=Decimal('100.00'),
            initial_cost=Decimal('5000.00'),
            current_count=750,
            current_weight=Decimal('300.00')
        )
        self.user = User.objects.create_user(
            username='testuser4',
            email='test4@example.com',
            password='testpass123'
        )
        
        # إنشاء حصاد
        self.harvest = Harvest.objects.create(
            batch=self.batch,
            harvest_date=date.today() - timedelta(days=5),
            quantity_kg=Decimal('200.00'),
            count=200,
            average_weight=Decimal('1.00'),
            fair_value=Decimal('3000.00'),
            cost_per_kg=Decimal('15.00'),
            status='completed',
            created_by=self.user
        )
        
        # إنشاء طلب بيع
        self.sales_order = SalesOrder.objects.create(
            order_number='SO-TEST-001',
            order_date=date.today() - timedelta(days=3),
            customer_name='عميل تجريبي',
            customer_phone='0501234567',
            subtotal=Decimal('3000.00'),
            vat_rate=Decimal('15.00'),
            vat_amount=Decimal('450.00'),
            total_amount=Decimal('3450.00'),
            status='confirmed',
            created_by=self.user
        )
        
        # إنشاء بند طلب بيع
        self.sales_order_line = SalesOrderLine.objects.create(
            sales_order=self.sales_order,
            harvest=self.harvest,
            quantity_kg=Decimal('200.00'),
            unit_price=Decimal('15.00'),
            line_total=Decimal('3000.00')
        )
    
    def test_create_invoice_linked_to_batch(self):
        """اختبار إنشاء فاتورة مرتبطة بدفعة"""
        invoice = Invoice.objects.create(
            invoice_number='INV-TEST-001',
            sales_order=self.sales_order,
            invoice_date=date.today() - timedelta(days=2),
            subtotal=Decimal('3000.00'),
            vat_amount=Decimal('450.00'),
            total_amount=Decimal('3450.00'),
            status='issued',
            created_by=self.user
        )
        
        assert invoice.id is not None
        assert invoice.sales_order == self.sales_order
        
        # التحقق من الربط بالدفعة عبر الحصاد
        assert invoice.sales_order.lines.first().harvest.batch == self.batch
    
    def test_traceability_from_invoice_to_batch(self):
        """اختبار التتبع من الفاتورة إلى الدفعة"""
        invoice = Invoice.objects.create(
            invoice_number='INV-TEST-002',
            sales_order=self.sales_order,
            invoice_date=date.today() - timedelta(days=2),
            subtotal=Decimal('3000.00'),
            vat_amount=Decimal('450.00'),
            total_amount=Decimal('3450.00'),
            status='issued',
            created_by=self.user
        )
        
        # التتبع: Invoice -> SalesOrder -> SalesOrderLine -> Harvest -> Batch
        batch_from_invoice = invoice.sales_order.lines.first().harvest.batch
        
        assert batch_from_invoice == self.batch
        assert batch_from_invoice.batch_number == 'BATCH-TEST-004'


@pytest.mark.django_db
class TestTraceabilityRetrieval:
    """اختبارات استرجاع بيانات Traceability"""
    
    def setup_method(self):
        """إعداد البيانات للاختبار"""
        self.species = Species.objects.create(
            name='Tilapia',
            arabic_name='سمك البلطي'
        )
        self.pond = Pond.objects.create(
            name='حوض 1',
            pond_type='concrete',
            capacity=Decimal('1000.00')
        )
        self.batch = Batch.objects.create(
            pond=self.pond,
            species=self.species,
            batch_number='BATCH-TEST-005',
            start_date=date.today() - timedelta(days=120),
            initial_count=1000,
            initial_weight=Decimal('100.00'),
            initial_cost=Decimal('5000.00'),
            current_count=750,
            current_weight=Decimal('300.00')
        )
        self.user = User.objects.create_user(
            username='testuser5',
            email='test5@example.com',
            password='testpass123'
        )
        
        self.harvest = Harvest.objects.create(
            batch=self.batch,
            harvest_date=date.today() - timedelta(days=5),
            quantity_kg=Decimal('200.00'),
            count=200,
            average_weight=Decimal('1.00'),
            fair_value=Decimal('3000.00'),
            cost_per_kg=Decimal('15.00'),
            status='completed',
            created_by=self.user
        )
        
        self.sales_order = SalesOrder.objects.create(
            order_number='SO-TEST-002',
            order_date=date.today() - timedelta(days=3),
            customer_name='عميل تجريبي',
            subtotal=Decimal('3000.00'),
            vat_rate=Decimal('15.00'),
            vat_amount=Decimal('450.00'),
            total_amount=Decimal('3450.00'),
            status='confirmed',
            created_by=self.user
        )
        
        self.sales_order_line = SalesOrderLine.objects.create(
            sales_order=self.sales_order,
            harvest=self.harvest,
            quantity_kg=Decimal('200.00'),
            unit_price=Decimal('15.00'),
            line_total=Decimal('3000.00')
        )
        
        self.invoice = Invoice.objects.create(
            invoice_number='INV-TEST-003',
            sales_order=self.sales_order,
            invoice_date=date.today() - timedelta(days=2),
            subtotal=Decimal('3000.00'),
            vat_amount=Decimal('450.00'),
            total_amount=Decimal('3450.00'),
            status='issued',
            created_by=self.user
        )
    
    def test_traceability_by_invoice(self):
        """اختبار التتبع من الفاتورة"""
        # التتبع: Invoice -> SalesOrder -> SalesOrderLine -> Harvest -> Batch
        batch = self.invoice.sales_order.lines.first().harvest.batch
        
        assert batch == self.batch
        assert batch.batch_number == 'BATCH-TEST-005'
    
    def test_traceability_by_batch(self):
        """اختبار التتبع من الدفعة"""
        # التتبع: Batch -> Harvest -> SalesOrderLine -> SalesOrder -> Invoice
        harvests = self.batch.harvests.all()
        assert len(harvests) > 0
        
        sales_orders = []
        invoices = []
        
        for harvest in harvests:
            for line in harvest.sales_order_lines.all():
                if line.sales_order not in sales_orders:
                    sales_orders.append(line.sales_order)
                if hasattr(line.sales_order, 'invoice') and line.sales_order.invoice:
                    if line.sales_order.invoice not in invoices:
                        invoices.append(line.sales_order.invoice)
        
        assert len(sales_orders) > 0
        assert len(invoices) > 0
        assert self.invoice in invoices
