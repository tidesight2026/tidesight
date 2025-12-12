"""
Management command لإضافة بيانات تجريبية للنماذج البيولوجية
"""
from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context
from biological.models import Species, Pond, Batch
from inventory.models import FeedType, FeedInventory, Medicine, MedicineInventory
from decimal import Decimal
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'إنشاء بيانات تجريبية للنماذج البيولوجية والمخزون'

    def add_arguments(self, parser):
        parser.add_argument(
            '--schema',
            type=str,
            default='farm1',
            help='Schema name (tenant name) - default: farm1',
        )

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='مسح البيانات الموجودة قبل الإضافة',
        )
        parser.add_argument(
            '--schema',
            type=str,
            default='farm1',
            help='Schema name (tenant name) - default: farm1',
        )

    def handle(self, *args, **options):
        schema_name = options.get('schema', 'farm1')
        
        self.stdout.write(f'استخدام schema: {schema_name}')
        
        with schema_context(schema_name):
            if options['clear']:
                self.stdout.write('مسح البيانات الموجودة...')
                Batch.objects.all().delete()
                Pond.objects.all().delete()
                Species.objects.all().delete()
                FeedInventory.objects.all().delete()
                FeedType.objects.all().delete()
                MedicineInventory.objects.all().delete()
                Medicine.objects.all().delete()
                self.stdout.write(self.style.SUCCESS('تم مسح البيانات'))

            self.stdout.write('بدء إضافة البيانات التجريبية...')

        # 1. إنشاء أنواع سمكية
        self.stdout.write('إضافة أنواع سمكية...')
        species_list = [
            {
                'name': 'Tilapia',
                'arabic_name': 'بلطي',
                'scientific_name': 'Oreochromis niloticus',
                'description': 'نوع شائع من الأسماك سريع النمو',
            },
            {
                'name': 'Carp',
                'arabic_name': 'كارب',
                'scientific_name': 'Cyprinus carpio',
                'description': 'نوع قوي ومقاوم للأمراض',
            },
            {
                'name': 'Sea Bass',
                'arabic_name': 'قاروص',
                'scientific_name': 'Dicentrarchus labrax',
                'description': 'نوع بحري عالي القيمة',
            },
        ]
        
        created_species = []
        for species_data in species_list:
            species, created = Species.objects.get_or_create(
                name=species_data['name'],
                defaults=species_data
            )
            created_species.append(species)
            if created:
                self.stdout.write(f'  ✓ تم إنشاء: {species.arabic_name}')
            else:
                self.stdout.write(f'  ⊙ موجود مسبقاً: {species.arabic_name}')

        # 2. إنشاء أحواض
        self.stdout.write('إضافة أحواض...')
        ponds_list = [
            {
                'name': 'حوض 1',
                'pond_type': 'concrete',
                'capacity': Decimal('100.00'),
                'location': 'المنطقة الشمالية',
                'status': 'active',
            },
            {
                'name': 'حوض 2',
                'pond_type': 'concrete',
                'capacity': Decimal('150.00'),
                'location': 'المنطقة الشمالية',
                'status': 'active',
            },
            {
                'name': 'حوض 3',
                'pond_type': 'earth',
                'capacity': Decimal('200.00'),
                'location': 'المنطقة الجنوبية',
                'status': 'empty',
            },
            {
                'name': 'حوض 4',
                'pond_type': 'fiberglass',
                'capacity': Decimal('50.00'),
                'location': 'المنطقة الوسطى',
                'status': 'active',
            },
            {
                'name': 'قفص 1',
                'pond_type': 'cage',
                'capacity': Decimal('75.00'),
                'location': 'البحيرة الرئيسية',
                'status': 'active',
            },
        ]
        
        created_ponds = []
        for pond_data in ponds_list:
            pond, created = Pond.objects.get_or_create(
                name=pond_data['name'],
                defaults=pond_data
            )
            created_ponds.append(pond)
            if created:
                self.stdout.write(f'  ✓ تم إنشاء: {pond.name}')
            else:
                self.stdout.write(f'  ⊙ موجود مسبقاً: {pond.name}')

        # 3. إنشاء دفعات
        self.stdout.write('إضافة دفعات...')
        batches_list = [
            {
                'batch_number': 'BATCH-2024-001',
                'pond': created_ponds[0],
                'species': created_species[0],  # بلطي
                'start_date': date.today() - timedelta(days=30),
                'initial_count': 5000,
                'initial_weight': Decimal('50.00'),
                'initial_cost': Decimal('5000.00'),
                'current_count': 4800,
                'status': 'active',
                'notes': 'دفعة بلطي جيدة النمو',
            },
            {
                'batch_number': 'BATCH-2024-002',
                'pond': created_ponds[1],
                'species': created_species[1],  # كارب
                'start_date': date.today() - timedelta(days=45),
                'initial_count': 3000,
                'initial_weight': Decimal('75.00'),
                'initial_cost': Decimal('6000.00'),
                'current_count': 2900,
                'status': 'active',
                'notes': 'دفعة كارب قوية',
            },
            {
                'batch_number': 'BATCH-2024-003',
                'pond': created_ponds[3],
                'species': created_species[2],  # قاروص
                'start_date': date.today() - timedelta(days=15),
                'initial_count': 2000,
                'initial_weight': Decimal('25.00'),
                'initial_cost': Decimal('8000.00'),
                'current_count': 1950,
                'status': 'active',
                'notes': 'دفعة قاروص حديثة',
            },
            {
                'batch_number': 'BATCH-2023-010',
                'pond': created_ponds[2],
                'species': created_species[0],  # بلطي
                'start_date': date.today() - timedelta(days=120),
                'initial_count': 4000,
                'initial_weight': Decimal('40.00'),
                'initial_cost': Decimal('4000.00'),
                'current_count': 0,
                'status': 'harvested',
                'notes': 'تم الحصاد',
            },
        ]
        
        created_batches = []
        for batch_data in batches_list:
            batch, created = Batch.objects.get_or_create(
                batch_number=batch_data['batch_number'],
                defaults=batch_data
            )
            created_batches.append(batch)
            if created:
                self.stdout.write(f'  ✓ تم إنشاء: {batch.batch_number}')
            else:
                self.stdout.write(f'  ⊙ موجود مسبقاً: {batch.batch_number}')

        # 4. إنشاء أنواع أعلاف
        self.stdout.write('إضافة أنواع أعلاف...')
        feed_types_list = [
            {
                'name': 'Starter Feed',
                'arabic_name': 'علف بداية',
                'protein_percentage': Decimal('40.00'),
                'unit': 'كجم',
                'description': 'علف للزريعة وبداية النمو',
            },
            {
                'name': 'Grower Feed',
                'arabic_name': 'علف نمو',
                'protein_percentage': Decimal('32.00'),
                'unit': 'كجم',
                'description': 'علف لمرحلة النمو',
            },
            {
                'name': 'Finisher Feed',
                'arabic_name': 'علف نهائي',
                'protein_percentage': Decimal('28.00'),
                'unit': 'كجم',
                'description': 'علف لمرحلة التسمين',
            },
        ]
        
        created_feed_types = []
        for feed_type_data in feed_types_list:
            feed_type, created = FeedType.objects.get_or_create(
                name=feed_type_data['name'],
                defaults=feed_type_data
            )
            created_feed_types.append(feed_type)
            if created:
                self.stdout.write(f'  ✓ تم إنشاء: {feed_type.arabic_name}')
            else:
                self.stdout.write(f'  ⊙ موجود مسبقاً: {feed_type.arabic_name}')

        # 5. إنشاء مخزون أعلاف
        self.stdout.write('إضافة مخزون أعلاف...')
        feed_inventory_list = [
            {
                'feed_type': created_feed_types[0],
                'quantity': Decimal('500.00'),
                'unit_price': Decimal('25.00'),
                'expiry_date': date.today() + timedelta(days=180),
                'location': 'المستودع 1',
                'notes': 'مخزون جيد',
            },
            {
                'feed_type': created_feed_types[1],
                'quantity': Decimal('1000.00'),
                'unit_price': Decimal('22.00'),
                'expiry_date': date.today() + timedelta(days=150),
                'location': 'المستودع 1',
                'notes': 'مخزون رئيسي',
            },
            {
                'feed_type': created_feed_types[2],
                'quantity': Decimal('750.00'),
                'unit_price': Decimal('20.00'),
                'expiry_date': date.today() + timedelta(days=200),
                'location': 'المستودع 2',
                'notes': 'مخزون كافي',
            },
        ]
        
        for feed_inv_data in feed_inventory_list:
            feed_inv, created = FeedInventory.objects.get_or_create(
                feed_type=feed_inv_data['feed_type'],
                location=feed_inv_data['location'],
                defaults=feed_inv_data
            )
            if created:
                self.stdout.write(f'  ✓ تم إنشاء مخزون: {feed_inv.feed_type.arabic_name}')
            else:
                self.stdout.write(f'  ⊙ موجود مسبقاً: {feed_inv.feed_type.arabic_name}')

        # 6. إنشاء أدوية
        self.stdout.write('إضافة أدوية...')
        medicines_list = [
            {
                'name': 'Oxytetracycline',
                'arabic_name': 'أوكسيتيتراسايكلين',
                'active_ingredient': 'Oxytetracycline HCl',
                'unit': 'جم',
                'description': 'مضاد حيوي واسع الطيف',
            },
            {
                'name': 'Formalin',
                'arabic_name': 'فورمالين',
                'active_ingredient': 'Formaldehyde',
                'unit': 'لتر',
                'description': 'مطهر ومبيد للطفيليات',
            },
            {
                'name': 'Vitamin C',
                'arabic_name': 'فيتامين سي',
                'active_ingredient': 'Ascorbic Acid',
                'unit': 'جم',
                'description': 'مكمل غذائي لتقوية المناعة',
            },
        ]
        
        created_medicines = []
        for medicine_data in medicines_list:
            medicine, created = Medicine.objects.get_or_create(
                name=medicine_data['name'],
                defaults=medicine_data
            )
            created_medicines.append(medicine)
            if created:
                self.stdout.write(f'  ✓ تم إنشاء: {medicine.arabic_name}')
            else:
                self.stdout.write(f'  ⊙ موجود مسبقاً: {medicine.arabic_name}')

        # 7. إنشاء مخزون أدوية
        self.stdout.write('إضافة مخزون أدوية...')
        medicine_inventory_list = [
            {
                'medicine': created_medicines[0],
                'quantity': Decimal('50.00'),
                'unit_price': Decimal('150.00'),
                'expiry_date': date.today() + timedelta(days=365),
                'location': 'صيدلية المزرعة',
                'notes': 'مخزون طارئ',
            },
            {
                'medicine': created_medicines[1],
                'quantity': Decimal('20.00'),
                'unit_price': Decimal('80.00'),
                'expiry_date': date.today() + timedelta(days=730),
                'location': 'صيدلية المزرعة',
                'notes': 'مطهر أساسي',
            },
            {
                'medicine': created_medicines[2],
                'quantity': Decimal('100.00'),
                'unit_price': Decimal('25.00'),
                'expiry_date': date.today() + timedelta(days=180),
                'location': 'صيدلية المزرعة',
                'notes': 'مكمل غذائي',
            },
        ]
        
        for med_inv_data in medicine_inventory_list:
            med_inv, created = MedicineInventory.objects.get_or_create(
                medicine=med_inv_data['medicine'],
                location=med_inv_data['location'],
                defaults=med_inv_data
            )
            if created:
                self.stdout.write(f'  ✓ تم إنشاء مخزون: {med_inv.medicine.arabic_name}')
            else:
                self.stdout.write(f'  ⊙ موجود مسبقاً: {med_inv.medicine.arabic_name}')

            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('✅ تم إضافة جميع البيانات التجريبية بنجاح!'))
            self.stdout.write('')
            self.stdout.write('📊 ملخص البيانات:')
            self.stdout.write(f'  - أنواع سمكية: {Species.objects.count()}')
            self.stdout.write(f'  - أحواض: {Pond.objects.count()}')
            self.stdout.write(f'  - دفعات: {Batch.objects.count()}')
            self.stdout.write(f'  - أنواع أعلاف: {FeedType.objects.count()}')
            self.stdout.write(f'  - مخزون أعلاف: {FeedInventory.objects.count()}')
            self.stdout.write(f'  - أدوية: {Medicine.objects.count()}')
            self.stdout.write(f'  - مخزون أدوية: {MedicineInventory.objects.count()}')

