"""
اختبارات دورة حياة السمكة - باستخدام TenantTestCase
"""

from django.test import TestCase
from django_tenants.test.cases import TenantTestCase
from decimal import Decimal
from django.utils import timezone
from datetime import date, timedelta

from biological.models import Species, FarmLocation, Pond, Batch, LifecycleStage
from daily_operations.models import FeedingLog, MortalityLog
from accounting.models import Account, JournalEntry, AccountType, BiologicalAssetRevaluation
from inventory.models import FeedType, FeedInventory
from sales.models import Harvest, SalesOrder, SalesOrderLine, Invoice
from accounts.models import User


class TestFishLifecycleTenant(TenantTestCase):
    """
    اختبارات دورة حياة السمكة - باستخدام TenantTestCase
    
    TenantTestCase يقوم تلقائياً بـ:
    1. إنشاء tenant schema
    2. تشغيل migrations على tenant schema
    3. تفعيل tenant context لكل اختبار
    """
    
    def setUp(self):
        """إعداد البيانات الأولية لكل اختبار"""
        super().setUp()
        
        # إنشاء نوع سمكي
        self.species = Species.objects.create(
            name="Tilapia",
            arabic_name="بلطي",
            scientific_name="Oreochromis niloticus",
            is_active=True
        )
        
        # إنشاء مرحلة دورة حياة
        self.lifecycle_stage = LifecycleStage.objects.create(
            name="Fingerling",
            arabic_name="إصبعيات",
            order=1,
            is_active=True
        )
        
        # إنشاء موقع مزرعة
        self.farm_location = FarmLocation.objects.create(
            name="المزرعة الرئيسية",
            arabic_name="المزرعة الرئيسية",
            is_active=True
        )
        
        # إنشاء حوض
        self.pond = Pond.objects.create(
            name="حوض 1",
            farm_location=self.farm_location,
            capacity=Decimal('10000.00'),
            is_active=True
        )
        
        # إنشاء نوع علف
        self.feed_type = FeedType.objects.create(
            name="Grower Feed",
            arabic_name="علف تسمين",
            protein_percentage=Decimal('40.00'),
            unit="كجم",
            is_active=True
        )
        
        # إنشاء مخزون علف
        self.feed_inventory = FeedInventory.objects.create(
            feed_type=self.feed_type,
            quantity=Decimal('5000.00'),
            unit_price=Decimal('4.50'),
            expiry_date=timezone.now().date() + timedelta(days=90),
            location="المخزن الرئيسي"
        )
        
        # إنشاء حسابات محاسبية
        self.biological_asset_account = Account.objects.create(
            code="1400",
            name="Biological Assets",
            arabic_name="أصول بيولوجية",
            account_type=AccountType.BIOLOGICAL_ASSET,
            is_active=True
        )
        
        self.finished_goods_account = Account.objects.create(
            code="1600",
            name="Finished Goods Inventory",
            arabic_name="مخزون منتج تام",
            account_type=AccountType.ASSET,
            is_active=True
        )
        
        # إنشاء دفعة
        self.batch = Batch.objects.create(
            batch_number="BATCH-001",
            species=self.species,
            pond=self.pond,
            start_date=date.today() - timedelta(days=30),
            initial_count=1000,
            initial_weight=Decimal('50.00'),  # 50 kg total
            initial_cost=Decimal('1000.00'),
            current_count=1000,
            current_weight=Decimal('50.00'),
            lifecycle_stage=self.lifecycle_stage,
            status='active'
        )
        
        # إنشاء مستخدم
        self.user = User.objects.create_user(
            username="test_user",
            email="test@example.com",
            password="testpass123",
            full_name="مستخدم اختبار",
            role="worker"
        )
    
    def test_batch_initial_state(self):
        """اختبار الحالة الأولية للدفعة"""
        self.assertEqual(self.batch.initial_count, 1000)
        self.assertEqual(self.batch.current_count, 1000)
        self.assertEqual(self.batch.initial_weight, Decimal('50.00'))
        self.assertEqual(self.batch.current_weight, Decimal('50.00'))
        self.assertEqual(self.batch.status, 'active')
    
    def test_feeding_and_growth(self):
        """اختبار التغذية والنمو"""
        initial_feed_quantity = self.feed_inventory.quantity
        initial_batch_weight = self.batch.current_weight
        
        # تسجيل تغذية
        feeding_log = FeedingLog.objects.create(
            batch=self.batch,
            feed_type=self.feed_type,
            feeding_date=date.today(),
            quantity=Decimal('100.00'),
            unit_price=self.feed_inventory.unit_price,
            created_by=self.user
        )
        
        # تحديث المخزون
        self.feed_inventory.quantity -= Decimal('100.00')
        self.feed_inventory.save()
        
        # التحقق من خصم العلف من المخزون
        self.feed_inventory.refresh_from_db()
        self.assertEqual(self.feed_inventory.quantity, initial_feed_quantity - Decimal('100.00'))
        
        # التحقق من أن التغذية تم تسجيلها
        self.assertIsNotNone(feeding_log.id)
        self.assertEqual(feeding_log.quantity, Decimal('100.00'))
    
    def test_mortality_log(self):
        """اختبار تسجيل النفوق"""
        initial_count = self.batch.current_count
        initial_weight = self.batch.current_weight
        
        # تسجيل نفوق
        # حساب متوسط الوزن
        avg_weight = self.batch.current_weight / self.batch.current_count if self.batch.current_count > 0 else Decimal('0.00')
        mortality_log = MortalityLog.objects.create(
            batch=self.batch,
            mortality_date=date.today(),
            count=50,
            average_weight=avg_weight,
            cause="Disease",
            created_by=self.user
        )
        
        # تحديث الدفعة
        self.batch.current_count -= 50
        self.batch.save()
        
        # التحقق من تحديث العدد
        self.batch.refresh_from_db()
        self.assertEqual(self.batch.current_count, initial_count - 50)
        
        # التحقق من تسجيل النفوق
        self.assertIsNotNone(mortality_log.id)
        self.assertEqual(mortality_log.count, 50)
    
    def test_ias41_revaluation(self):
        """اختبار إعادة تقييم IAS 41"""
        # محاكاة النمو
        self.batch.current_weight = Decimal('200.00')
        self.batch.save()
        
        # حساب التكلفة التراكمية (initial_cost فقط في هذا المثال)
        # في الواقع، يجب حساب التكلفة من FeedingLog و MortalityLog
        carrying_amount = self.batch.initial_cost  # التكلفة الأولية
        current_weight = self.batch.current_weight
        market_price = Decimal('15.00')
        fair_value = current_weight * market_price
        
        # إنشاء إعادة تقييم
        revaluation = BiologicalAssetRevaluation.objects.create(
            batch=self.batch,
            revaluation_date=date.today(),
            carrying_amount=carrying_amount,
            fair_value=fair_value,
            market_price_per_kg=market_price,
            current_weight_kg=current_weight,
            current_count=self.batch.current_count,
            unrealized_gain_loss=fair_value - carrying_amount,
            created_by=self.user
        )
        
        # التحقق من إنشاء إعادة التقييم
        self.assertIsNotNone(revaluation.id)
        self.assertEqual(revaluation.unrealized_gain_loss, fair_value - carrying_amount)
        self.assertEqual(revaluation.fair_value, fair_value)
        self.assertEqual(revaluation.carrying_amount, carrying_amount)
    
    def test_harvest_creation(self):
        """اختبار إنشاء حصاد"""
        # التأكد من أن الدفعة لديها وزن وعدد
        self.batch.current_count = 800
        self.batch.current_weight = Decimal('300.00')
        self.batch.save()
        
        harvest_quantity_kg = Decimal('250.00')
        harvest_count = 500  # حصاد 500 سمكة
        market_price = Decimal('18.00')
        
        # إنشاء حصاد
        harvest = Harvest.objects.create(
            batch=self.batch,
            harvest_date=date.today(),
            quantity_kg=harvest_quantity_kg,
            count=harvest_count,
            average_weight=harvest_quantity_kg / harvest_count,
            fair_value=harvest_quantity_kg * market_price,
            created_by=self.user
        )
        
        # التحقق من إنشاء الحصاد
        self.assertIsNotNone(harvest.id)
        self.assertEqual(harvest.status, 'pending')
        self.assertEqual(harvest.quantity_kg, harvest_quantity_kg)
        self.assertEqual(harvest.count, harvest_count)
        
        # تحديث الدفعة
        self.batch.current_count -= harvest_count
        self.batch.current_weight -= harvest_quantity_kg
        self.batch.save()
        
        self.batch.refresh_from_db()
        self.assertEqual(self.batch.current_count, 800 - harvest_count)
    
    def test_sales_order_creation(self):
        """اختبار إنشاء طلب بيع"""
        # إنشاء حصاد أولاً
        harvest = Harvest.objects.create(
            batch=self.batch,
            harvest_date=date.today(),
            quantity_kg=Decimal('100.00'),
            count=300,
            average_weight=Decimal('0.33'),
            fair_value=Decimal('100.00') * Decimal('18.00'),
            created_by=self.user
        )
        
        customer_name = "Local Restaurant"
        order_quantity = Decimal('100.00')
        unit_price = Decimal('20.00')
        
        # إنشاء طلب بيع
        sales_order = SalesOrder.objects.create(
            customer_name=customer_name,
            order_date=date.today(),
            status='draft',
            vat_rate=Decimal('15.00'),
            created_by=self.user
        )
        
        SalesOrderLine.objects.create(
            sales_order=sales_order,
            harvest=harvest,
            quantity_kg=order_quantity,
            unit_price=unit_price
        )
        
        # إعادة حساب الإجمالي
        sales_order.save()
        
        # التحقق من طلب البيع
        self.assertIsNotNone(sales_order.id)
        self.assertEqual(sales_order.subtotal, order_quantity * unit_price)
        self.assertEqual(sales_order.vat_amount, (sales_order.subtotal * Decimal('0.15')))
        self.assertEqual(sales_order.total_amount, sales_order.subtotal + sales_order.vat_amount)
        self.assertEqual(sales_order.status, 'draft')
    
    def test_invoice_creation(self):
        """اختبار إنشاء فاتورة"""
        # إنشاء حصاد
        harvest = Harvest.objects.create(
            batch=self.batch,
            harvest_date=date.today(),
            quantity_kg=Decimal('100.00'),
            count=300,
            average_weight=Decimal('0.33'),
            fair_value=Decimal('100.00') * Decimal('18.00'),
            created_by=self.user
        )
        
        # إنشاء طلب بيع
        sales_order = SalesOrder.objects.create(
            customer_name="Big Buyer Inc.",
            order_date=date.today(),
            status='confirmed',
            vat_rate=Decimal('15.00'),
            created_by=self.user
        )
        
        SalesOrderLine.objects.create(
            sales_order=sales_order,
            harvest=harvest,
            quantity_kg=Decimal('100.00'),
            unit_price=Decimal('20.00')
        )
        sales_order.save()
        
        # إنشاء فاتورة
        invoice = Invoice.objects.create(
            sales_order=sales_order,
            invoice_number="INV-001",
            invoice_date=date.today(),
            subtotal=sales_order.subtotal,
            vat_amount=sales_order.vat_amount,
            total_amount=sales_order.total_amount,
            created_by=self.user
        )
        
        # التحقق من إنشاء الفاتورة
        self.assertIsNotNone(invoice.id)
        self.assertEqual(invoice.status, 'issued')  # الحالة الافتراضية
        self.assertEqual(invoice.total_amount, sales_order.total_amount)

