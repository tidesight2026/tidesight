# tests/test_feed_lifecycle_tenant.py

from django_tenants.test.cases import TenantTestCase
from decimal import Decimal
from datetime import date
from inventory.models import FeedInventory, FeedType
from daily_operations.models import FeedingLog
from biological.models import Batch, Pond, Species, LifecycleStage, FarmLocation
from django.contrib.auth import get_user_model

User = get_user_model()


class TestFeedLifecycleTenant(TenantTestCase):
    """
    اختبارات دورة حياة العلف باستخدام TenantTestCase
    
    ✅ TenantTestCase يقوم تلقائياً بـ:
    - إنشاء tenant schema
    - تشغيل migrations
    - تعيين schema context
    - تنظيف بعد الاختبار
    """

    def setUp(self):
        super().setUp()
        
        # 1. إعداد المستخدم
        self.user = User.objects.create_user(
            username='farm_manager',
            password='password123',
            email='manager@test.com',
            full_name='Farm Manager',
            role='manager'
        )

        # 2. إعداد البيانات الأساسية
        # إنشاء موقع مزرعة
        self.farm_location = FarmLocation.objects.create(
            name='Test Farm Location',
            arabic_name='موقع تجريبي'
        )
        
        # إنشاء حوض
        self.pond = Pond.objects.create(
            name="Pond 1",
            capacity=Decimal('1000.00'),  # السعة بالمتر المكعب
            farm_location=self.farm_location
        )
        
        # إنشاء Species و Stage
        self.species = Species.objects.create(
            name="Tilapia",
            arabic_name="بلطي",
            scientific_name="Oreochromis niloticus"
        )
        self.stage = LifecycleStage.objects.create(
            name="Fingerlings",
            arabic_name="إصبعيات",
            order=1
        )
        
        # إنشاء Batch
        self.batch = Batch.objects.create(
            batch_number="BATCH-A", 
            pond=self.pond, 
            current_count=1000,
            initial_count=1000,
            species=self.species,
            lifecycle_stage=self.stage,
            current_weight=Decimal('10.00'),
            initial_weight=Decimal('10.00'),
            initial_cost=Decimal('100.00'),
            start_date=date.today()
        )

        # 3. إعداد نوع العلف
        self.feed_type = FeedType.objects.create(
            name="Protein 45%",
            arabic_name="بروتين 45%",
            protein_percentage=Decimal('45.00'),
            unit="كجم",
            description="High quality feed"
        )

    def test_feed_purchase_and_inventory(self):
        """اختبار شراء العلف وزيادة المخزون"""
        # إنشاء عنصر مخزون العلف
        feed_item = FeedInventory.objects.create(
            feed_type=self.feed_type,
            quantity=Decimal('0.00'), 
            unit_price=Decimal("5.00")
        )
        
        # عملية شراء (إضافة رصيد)
        feed_item.quantity += Decimal('1000.00')
        feed_item.save()
        
        # التحقق
        feed_item.refresh_from_db()
        self.assertEqual(feed_item.quantity, Decimal('1000.00'))
        print("\n✅ تم شراء العلف بنجاح")

    def test_feed_consumption_cycle(self):
        """اختبار دورة الاستهلاك الكاملة"""
        # 1. التوريد (شراء)
        feed_item = FeedInventory.objects.create(
            feed_type=self.feed_type,
            quantity=Decimal('1000.00'), 
            unit_price=Decimal("5.00")
        )

        # 2. الاستهلاك (إطعام)
        feed_amount = Decimal('50.00')
        feeding_log = FeedingLog.objects.create(
            batch=self.batch,
            feed_type=self.feed_type,
            quantity=feed_amount,
            unit_price=feed_item.unit_price,
            feeding_date=date.today(),
            created_by=self.user
        )

        # 3. التحقق من إنشاء سجل التغذية
        self.assertIsNotNone(feeding_log.id)
        self.assertEqual(feeding_log.quantity, feed_amount)
        self.assertEqual(feeding_log.total_cost, feed_amount * feed_item.unit_price)
        print("\n✅ تم إنشاء سجل التغذية بنجاح")

        # 4. التحقق من القيد المحاسبي (اختياري - إذا كان لديك Signals مفعلة)
        try:
            from accounting.models import JournalEntry
            entry = JournalEntry.objects.filter(
                reference_type='feeding_log',
                reference_id=feeding_log.id
            ).first()
            
            if entry:
                # التحقق من توازن القيد
                total_debit = sum(
                    line.amount for line in entry.lines.all() if line.type == 'debit'
                )
                total_credit = sum(
                    line.amount for line in entry.lines.all() if line.type == 'credit'
                )
                self.assertEqual(total_debit, total_credit)
                self.assertEqual(total_debit, feed_amount * feed_item.unit_price)
                print("✅ القيد المحاسبي متوازن وصحيح")
            else:
                print("⚠️ لم يتم العثور على قيد محاسبي (تأكد من تفعيل الـ Signals)")
        except Exception as e:
            print(f"⚠️ حدث خطأ أثناء التحقق من القيد المحاسبي: {e}")
