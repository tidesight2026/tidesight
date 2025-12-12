#!/usr/bin/env python
"""
سكريبت مباشر لإضافة بيانات تجريبية في tenant schema
"""
import os
import sys
import django

# إعداد Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tenants.aqua_core.settings')
django.setup()

from django_tenants.utils import schema_context
from biological.models import Species, Pond, Batch
from inventory.models import FeedType, FeedInventory, Medicine, MedicineInventory
from decimal import Decimal
from datetime import date, timedelta

def create_sample_data(schema_name='farm1', clear=False):
    """إنشاء بيانات تجريبية"""
    
    print(f'استخدام schema: {schema_name}')
    
    with schema_context(schema_name):
        if clear:
            print('مسح البيانات الموجودة...')
            Batch.objects.all().delete()
            Pond.objects.all().delete()
            Species.objects.all().delete()
            FeedInventory.objects.all().delete()
            FeedType.objects.all().delete()
            MedicineInventory.objects.all().delete()
            Medicine.objects.all().delete()
            print('✅ تم مسح البيانات')

        print('بدء إضافة البيانات التجريبية...')

        # 1. أنواع سمكية
        print('إضافة أنواع سمكية...')
        species_list = [
            {'name': 'Tilapia', 'arabic_name': 'بلطي', 'scientific_name': 'Oreochromis niloticus', 'description': 'نوع شائع سريع النمو'},
            {'name': 'Carp', 'arabic_name': 'كارب', 'scientific_name': 'Cyprinus carpio', 'description': 'نوع قوي ومقاوم'},
            {'name': 'Sea Bass', 'arabic_name': 'قاروص', 'scientific_name': 'Dicentrarchus labrax', 'description': 'نوع بحري عالي القيمة'},
        ]
        
        created_species = []
        for data in species_list:
            species, created = Species.objects.get_or_create(name=data['name'], defaults=data)
            created_species.append(species)
            print(f'  {"✓" if created else "⊙"} {species.arabic_name}')

        # 2. أحواض
        print('إضافة أحواض...')
        ponds_list = [
            {'name': 'حوض 1', 'pond_type': 'concrete', 'capacity': Decimal('100.00'), 'location': 'المنطقة الشمالية', 'status': 'active'},
            {'name': 'حوض 2', 'pond_type': 'concrete', 'capacity': Decimal('150.00'), 'location': 'المنطقة الشمالية', 'status': 'active'},
            {'name': 'حوض 3', 'pond_type': 'earth', 'capacity': Decimal('200.00'), 'location': 'المنطقة الجنوبية', 'status': 'empty'},
            {'name': 'حوض 4', 'pond_type': 'fiberglass', 'capacity': Decimal('50.00'), 'location': 'المنطقة الوسطى', 'status': 'active'},
            {'name': 'قفص 1', 'pond_type': 'cage', 'capacity': Decimal('75.00'), 'location': 'البحيرة الرئيسية', 'status': 'active'},
        ]
        
        created_ponds = []
        for data in ponds_list:
            pond, created = Pond.objects.get_or_create(name=data['name'], defaults=data)
            created_ponds.append(pond)
            print(f'  {"✓" if created else "⊙"} {pond.name}')

        # 3. دفعات
        print('إضافة دفعات...')
        batches_list = [
            {'batch_number': 'BATCH-2024-001', 'pond': created_ponds[0], 'species': created_species[0], 'start_date': date.today() - timedelta(days=30), 'initial_count': 5000, 'initial_weight': Decimal('50.00'), 'initial_cost': Decimal('5000.00'), 'current_count': 4800, 'status': 'active', 'notes': 'دفعة بلطي جيدة'},
            {'batch_number': 'BATCH-2024-002', 'pond': created_ponds[1], 'species': created_species[1], 'start_date': date.today() - timedelta(days=45), 'initial_count': 3000, 'initial_weight': Decimal('75.00'), 'initial_cost': Decimal('6000.00'), 'current_count': 2900, 'status': 'active', 'notes': 'دفعة كارب قوية'},
            {'batch_number': 'BATCH-2024-003', 'pond': created_ponds[3], 'species': created_species[2], 'start_date': date.today() - timedelta(days=15), 'initial_count': 2000, 'initial_weight': Decimal('25.00'), 'initial_cost': Decimal('8000.00'), 'current_count': 1950, 'status': 'active', 'notes': 'دفعة قاروص حديثة'},
            {'batch_number': 'BATCH-2023-010', 'pond': created_ponds[2], 'species': created_species[0], 'start_date': date.today() - timedelta(days=120), 'initial_count': 4000, 'initial_weight': Decimal('40.00'), 'initial_cost': Decimal('4000.00'), 'current_count': 0, 'status': 'harvested', 'notes': 'تم الحصاد'},
        ]
        
        for data in batches_list:
            batch, created = Batch.objects.get_or_create(batch_number=data['batch_number'], defaults=data)
            print(f'  {"✓" if created else "⊙"} {batch.batch_number}')

        # 4. أنواع أعلاف
        print('إضافة أنواع أعلاف...')
        feed_types_list = [
            {'name': 'Starter Feed', 'arabic_name': 'علف بداية', 'protein_percentage': Decimal('40.00'), 'unit': 'كجم', 'description': 'علف للزريعة'},
            {'name': 'Grower Feed', 'arabic_name': 'علف نمو', 'protein_percentage': Decimal('32.00'), 'unit': 'كجم', 'description': 'علف للنمو'},
            {'name': 'Finisher Feed', 'arabic_name': 'علف نهائي', 'protein_percentage': Decimal('28.00'), 'unit': 'كجم', 'description': 'علف للتسمين'},
        ]
        
        created_feed_types = []
        for data in feed_types_list:
            feed_type, created = FeedType.objects.get_or_create(name=data['name'], defaults=data)
            created_feed_types.append(feed_type)
            print(f'  {"✓" if created else "⊙"} {feed_type.arabic_name}')

        # 5. مخزون أعلاف
        print('إضافة مخزون أعلاف...')
        feed_inv_list = [
            {'feed_type': created_feed_types[0], 'quantity': Decimal('500.00'), 'unit_price': Decimal('25.00'), 'expiry_date': date.today() + timedelta(days=180), 'location': 'المستودع 1'},
            {'feed_type': created_feed_types[1], 'quantity': Decimal('1000.00'), 'unit_price': Decimal('22.00'), 'expiry_date': date.today() + timedelta(days=150), 'location': 'المستودع 1'},
            {'feed_type': created_feed_types[2], 'quantity': Decimal('750.00'), 'unit_price': Decimal('20.00'), 'expiry_date': date.today() + timedelta(days=200), 'location': 'المستودع 2'},
        ]
        
        for data in feed_inv_list:
            feed_inv, created = FeedInventory.objects.get_or_create(feed_type=data['feed_type'], location=data['location'], defaults=data)
            print(f'  {"✓" if created else "⊙"} مخزون {feed_inv.feed_type.arabic_name}')

        # 6. أدوية
        print('إضافة أدوية...')
        medicines_list = [
            {'name': 'Oxytetracycline', 'arabic_name': 'أوكسيتيتراسايكلين', 'active_ingredient': 'Oxytetracycline HCl', 'unit': 'جم', 'description': 'مضاد حيوي'},
            {'name': 'Formalin', 'arabic_name': 'فورمالين', 'active_ingredient': 'Formaldehyde', 'unit': 'لتر', 'description': 'مطهر'},
            {'name': 'Vitamin C', 'arabic_name': 'فيتامين سي', 'active_ingredient': 'Ascorbic Acid', 'unit': 'جم', 'description': 'مكمل غذائي'},
        ]
        
        created_medicines = []
        for data in medicines_list:
            medicine, created = Medicine.objects.get_or_create(name=data['name'], defaults=data)
            created_medicines.append(medicine)
            print(f'  {"✓" if created else "⊙"} {medicine.arabic_name}')

        # 7. مخزون أدوية
        print('إضافة مخزون أدوية...')
        med_inv_list = [
            {'medicine': created_medicines[0], 'quantity': Decimal('50.00'), 'unit_price': Decimal('150.00'), 'expiry_date': date.today() + timedelta(days=365), 'location': 'صيدلية المزرعة'},
            {'medicine': created_medicines[1], 'quantity': Decimal('20.00'), 'unit_price': Decimal('80.00'), 'expiry_date': date.today() + timedelta(days=730), 'location': 'صيدلية المزرعة'},
            {'medicine': created_medicines[2], 'quantity': Decimal('100.00'), 'unit_price': Decimal('25.00'), 'expiry_date': date.today() + timedelta(days=180), 'location': 'صيدلية المزرعة'},
        ]
        
        for data in med_inv_list:
            med_inv, created = MedicineInventory.objects.get_or_create(medicine=data['medicine'], location=data['location'], defaults=data)
            print(f'  {"✓" if created else "⊙"} مخزون {med_inv.medicine.arabic_name}')

        print('')
        print('✅ تم إضافة جميع البيانات التجريبية بنجاح!')
        print('')
        print('📊 ملخص البيانات:')
        print(f'  - أنواع سمكية: {Species.objects.count()}')
        print(f'  - أحواض: {Pond.objects.count()}')
        print(f'  - دفعات: {Batch.objects.count()}')
        print(f'  - أنواع أعلاف: {FeedType.objects.count()}')
        print(f'  - مخزون أعلاف: {FeedInventory.objects.count()}')
        print(f'  - أدوية: {Medicine.objects.count()}')
        print(f'  - مخزون أدوية: {MedicineInventory.objects.count()}')

if __name__ == '__main__':
    import sys
    clear = '--clear' in sys.argv
    create_sample_data('farm1', clear=clear)

