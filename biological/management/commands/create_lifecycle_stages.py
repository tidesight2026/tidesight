"""
Management Command لإنشاء مراحل النمو الافتراضية
"""
from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context
from biological.models import LifecycleStage


class Command(BaseCommand):
    help = 'إنشاء مراحل النمو الافتراضية'

    def add_arguments(self, parser):
        parser.add_argument(
            '--schema',
            type=str,
            default='farm1',
            help='Schema name (tenant name) - default: farm1'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing stages before creating new ones'
        )

    def handle(self, *args, **options):
        schema_name = options['schema']
        clear_existing = options['clear']
        
        with schema_context(schema_name):
            if clear_existing:
                self.stdout.write('مسح المراحل الموجودة...')
                LifecycleStage.objects.all().delete()
            
            stages = [
                {
                    'name': 'Fry',
                    'arabic_name': 'زريعة',
                    'description': 'المرحلة الأولى - الزريعة الصغيرة',
                    'min_days': 0,
                    'max_days': 30,
                    'order': 1
                },
                {
                    'name': 'Fingerling',
                    'arabic_name': 'إصبعي',
                    'description': 'المرحلة الثانية - الإصبعي',
                    'min_days': 31,
                    'max_days': 60,
                    'order': 2
                },
                {
                    'name': 'Juvenile',
                    'arabic_name': 'صغير',
                    'description': 'المرحلة الثالثة - صغير',
                    'min_days': 61,
                    'max_days': 120,
                    'order': 3
                },
                {
                    'name': 'Sub-adult',
                    'arabic_name': 'تحت بالغ',
                    'description': 'المرحلة الرابعة - تحت بالغ',
                    'min_days': 121,
                    'max_days': 180,
                    'order': 4
                },
                {
                    'name': 'Adult',
                    'arabic_name': 'بالغ',
                    'description': 'المرحلة الخامسة - بالغ جاهز للحصاد',
                    'min_days': 181,
                    'max_days': None,
                    'order': 5
                }
            ]
            
            self.stdout.write(f'إنشاء مراحل النمو في schema: {schema_name}...')
            for stage_data in stages:
                stage, created = LifecycleStage.objects.get_or_create(
                    name=stage_data['name'],
                    defaults=stage_data
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'  ✓ تم إنشاء: {stage.arabic_name}'))
                else:
                    self.stdout.write(f'  - موجود مسبقاً: {stage.arabic_name}')
            
            self.stdout.write(self.style.SUCCESS(f'\n✅ تم إنشاء {LifecycleStage.objects.count()} مرحلة نمو!'))

