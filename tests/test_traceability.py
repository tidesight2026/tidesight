"""
اختبارات Traceability APIs
"""
import pytest
from decimal import Decimal
from datetime import date, timedelta
from django.test import Client
from ninja.testing import TestClient

from biological.models import Batch, Species, Pond
from daily_operations.models import FeedingLog, MortalityLog
from inventory.models import FeedType
from sales.models import Harvest, SalesOrder, SalesOrderLine, Invoice
from accounts.models import User
from api.traceability import router


@pytest.mark.django_db
class TestTraceability:
    """اختبارات Traceability APIs"""
    
    def setup_method(self):
        """إعداد البيانات للاختبار"""
        # إنشاء أنواع وأحواض
        self.species = Species.objects.create(
            name='Tilapia',
            arabic_name='سمك البلطي'
        )
        self.pond = Pond.objects.create(
            name='حوض 1',
            pond_type='concrete',
            capacity=Decimal('1000.00')
        )
        
        # إنشاء دفعة
        self.batch = Batch.objects.create(
            pond=self.pond,
            species=self.species,
            batch_number='BATCH-001',
            start_date=date.today() - timedelta(days=60),
            initial_count=1000,
            initial_weight=Decimal('100.00'),
            initial_cost=Decimal('5000.00'),
            current_count=950,
            current_weight=Decimal('500.00')
        )
        
        # إنشاء نوع علف
        self.feed_type = FeedType.objects.create(
            name='علف',
            arabic_name='علف',
            unit='kg'
        )
        
        # إنشاء سجلات تغذية
        self.feeding_log1 = FeedingLog.objects.create(
            batch=self.batch,
            feed_type=self.feed_type,
            feeding_date=date.today() - timedelta(days=30),
            quantity=Decimal('50.00'),
            unit_price=Decimal('5.00')
        )
        
        self.feeding_log2 = FeedingLog.objects.create(
            batch=self.batch,
            feed_type=self.feed_type,
            feeding_date=date.today() - timedelta(days=15),
            quantity=Decimal('75.00'),
            unit_price=Decimal('5.00')
        )
        
        # إنشاء سجل نفوق
        self.mortality_log = MortalityLog.objects.create(
            batch=self.batch,
            mortality_date=date.today() - timedelta(days=20),
            count=50,
            cause='مرض'
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
            status='completed'
        )
        
        # إنشاء طلب بيع
        self.sales_order = SalesOrder.objects.create(
            order_number='SO-001',
            order_date=date.today() - timedelta(days=3),
            customer_name='عميل تجريبي',
            customer_phone='0501234567',
            subtotal=Decimal('3000.00'),
            vat_rate=Decimal('15.00'),
            vat_amount=Decimal('450.00'),
            total_amount=Decimal('3450.00'),
            status='confirmed'
        )
        
        # إنشاء بند طلب بيع
        self.sales_order_line = SalesOrderLine.objects.create(
            sales_order=self.sales_order,
            harvest=self.harvest,
            quantity_kg=Decimal('200.00'),
            unit_price=Decimal('15.00'),
            line_total=Decimal('3000.00')
        )
        
        # إنشاء فاتورة
        self.invoice = Invoice.objects.create(
            invoice_number='INV-001',
            sales_order=self.sales_order,
            invoice_date=date.today() - timedelta(days=2),
            subtotal=Decimal('3000.00'),
            vat_amount=Decimal('450.00'),
            total_amount=Decimal('3450.00'),
            status='issued'
        )
    
    def test_traceability_by_invoice(self):
        """اختبار استرجاع التتبع من الفاتورة"""
        from api.auth import TokenAuth
        
        # إنشاء مستخدم للاختبار
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='admin'
        )
        
        # إنشاء client للاختبار
        client = TestClient(router)
        
        # محاكاة request مع authentication
        # ملاحظة: في بيئة الاختبار الفعلية، قد تحتاج لتعديل هذا
        response = client.get(f'/by-invoice/{self.invoice.id}')
        
        # التحقق من الاستجابة
        assert response.status_code == 200
        data = response.json()
        
        # التحقق من وجود الفاتورة
        assert data['invoice']['invoice_number'] == 'INV-001'
        
        # التحقق من وجود طلب البيع
        assert data['sales_order']['order_number'] == 'SO-001'
        
        # التحقق من وجود الحصاد
        assert len(data['harvests']) > 0
        assert data['harvests'][0]['id'] == self.harvest.id
        
        # التحقق من وجود الدفعة
        assert len(data['batches']) > 0
        assert data['batches'][0]['batch_number'] == 'BATCH-001'
        
        # التحقق من وجود سجلات التغذية
        assert len(data['feeding_logs']) >= 2
        
        # التحقق من وجود سجلات النفوق
        assert len(data['mortality_logs']) >= 1
    
    def test_traceability_by_batch(self):
        """اختبار استرجاع التتبع من الدفعة"""
        from api.auth import TokenAuth
        
        # إنشاء مستخدم للاختبار
        user = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123',
            role='admin'
        )
        
        # إنشاء client للاختبار
        client = TestClient(router)
        
        # محاكاة request
        response = client.get(f'/by-batch/{self.batch.id}')
        
        # التحقق من الاستجابة
        assert response.status_code == 200
        data = response.json()
        
        # التحقق من وجود الدفعة
        assert data['batch']['batch_number'] == 'BATCH-001'
        
        # التحقق من وجود الحصاد
        assert len(data['harvests']) > 0
        assert data['harvests'][0]['id'] == self.harvest.id
        
        # التحقق من وجود طلبات البيع
        assert len(data['sales_orders']) > 0
        assert data['sales_orders'][0]['order_number'] == 'SO-001'
        
        # التحقق من وجود الفواتير
        assert len(data['invoices']) > 0
        assert data['invoices'][0]['invoice_number'] == 'INV-001'
        
        # التحقق من وجود سجلات التغذية
        assert len(data['feeding_logs']) >= 2
        
        # التحقق من وجود سجلات النفوق
        assert len(data['mortality_logs']) >= 1
    
    def test_traceability_by_invoice_not_found(self):
        """اختبار حالة عدم وجود الفاتورة"""
        client = TestClient(router)
        
        response = client.get('/by-invoice/99999')
        
        assert response.status_code == 404
    
    def test_traceability_by_batch_not_found(self):
        """اختبار حالة عدم وجود الدفعة"""
        client = TestClient(router)
        
        response = client.get('/by-batch/99999')
        
        assert response.status_code == 404
