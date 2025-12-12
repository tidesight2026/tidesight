"""
Management Command لإنشاء دليل الحسابات الموحد للمزارع السمكية
"""
from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context
from accounting.models import Account, AccountType


class Command(BaseCommand):
    help = 'إنشاء دليل الحسابات الموحد للمزارع السمكية'

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
            help='Clear existing accounts before creating new ones'
        )

    def handle(self, *args, **options):
        schema_name = options['schema']
        clear_existing = options['clear']
        
        with schema_context(schema_name):
            if clear_existing:
                self.stdout.write('مسح الحسابات الموجودة...')
                Account.objects.all().delete()
            
            accounts = [
                # الأصول
                {'code': '1000', 'name': 'Assets', 'arabic_name': 'الأصول', 'type': AccountType.ASSET, 'parent': None},
                
                # الأصول المتداولة
                {'code': '1100', 'name': 'Current Assets', 'arabic_name': 'الأصول المتداولة', 'type': AccountType.ASSET, 'parent_code': '1000'},
                {'code': '1110', 'name': 'Cash', 'arabic_name': 'النقدية', 'type': AccountType.ASSET, 'parent_code': '1100'},
                {'code': '1120', 'name': 'Bank', 'arabic_name': 'البنك', 'type': AccountType.ASSET, 'parent_code': '1100'},
                {'code': '1130', 'name': 'Accounts Receivable', 'arabic_name': 'العملاء', 'type': AccountType.ASSET, 'parent_code': '1100'},
                {'code': '1140', 'name': 'Feed Inventory', 'arabic_name': 'مخزون الأعلاف', 'type': AccountType.ASSET, 'parent_code': '1100'},
                {'code': '1150', 'name': 'Medicine Inventory', 'arabic_name': 'مخزون الأدوية', 'type': AccountType.ASSET, 'parent_code': '1100'},
                {'code': '1160', 'name': 'Finished Goods', 'arabic_name': 'مخزون منتج تام', 'type': AccountType.ASSET, 'parent_code': '1100'},
                
                # الأصول الثابتة
                {'code': '1200', 'name': 'Fixed Assets', 'arabic_name': 'الأصول الثابتة', 'type': AccountType.ASSET, 'parent_code': '1000'},
                {'code': '1210', 'name': 'Land', 'arabic_name': 'الأرض', 'type': AccountType.ASSET, 'parent_code': '1200'},
                {'code': '1220', 'name': 'Buildings', 'arabic_name': 'المباني', 'type': AccountType.ASSET, 'parent_code': '1200'},
                {'code': '1230', 'name': 'Ponds & Tanks', 'arabic_name': 'الأحواض والخزانات', 'type': AccountType.ASSET, 'parent_code': '1200'},
                {'code': '1240', 'name': 'Equipment', 'arabic_name': 'المعدات', 'type': AccountType.ASSET, 'parent_code': '1200'},
                
                # الأصول البيولوجية
                {'code': '1300', 'name': 'Biological Assets', 'arabic_name': 'الأصول البيولوجية', 'type': AccountType.BIOLOGICAL_ASSET, 'parent_code': '1000'},
                {'code': '1310', 'name': 'Active Batches', 'arabic_name': 'الدفعات النشطة', 'type': AccountType.BIOLOGICAL_ASSET, 'parent_code': '1300'},
                {'code': '1320', 'name': 'Biological Asset Revaluation', 'arabic_name': 'إعادة تقييم الأصول البيولوجية', 'type': AccountType.BIOLOGICAL_ASSET, 'parent_code': '1300'},
                
                # الخصوم
                {'code': '2000', 'name': 'Liabilities', 'arabic_name': 'الخصوم', 'type': AccountType.LIABILITY, 'parent': None},
                {'code': '2100', 'name': 'Current Liabilities', 'arabic_name': 'الخصوم المتداولة', 'type': AccountType.LIABILITY, 'parent_code': '2000'},
                {'code': '2110', 'name': 'Accounts Payable', 'arabic_name': 'الموردون', 'type': AccountType.LIABILITY, 'parent_code': '2100'},
                {'code': '2120', 'name': 'Tax Payable', 'arabic_name': 'الضرائب المستحقة', 'type': AccountType.LIABILITY, 'parent_code': '2100'},
                
                # حقوق الملكية
                {'code': '3000', 'name': 'Equity', 'arabic_name': 'حقوق الملكية', 'type': AccountType.EQUITY, 'parent': None},
                {'code': '3100', 'name': 'Capital', 'arabic_name': 'رأس المال', 'type': AccountType.EQUITY, 'parent_code': '3000'},
                {'code': '3200', 'name': 'Retained Earnings', 'arabic_name': 'الأرباح المحتجزة', 'type': AccountType.EQUITY, 'parent_code': '3000'},
                
                # الإيرادات
                {'code': '4000', 'name': 'Revenue', 'arabic_name': 'الإيرادات', 'type': AccountType.REVENUE, 'parent': None},
                {'code': '4100', 'name': 'Sales Revenue', 'arabic_name': 'إيرادات المبيعات', 'type': AccountType.REVENUE, 'parent_code': '4000'},
                {'code': '4110', 'name': 'Fish Sales', 'arabic_name': 'مبيعات السمك', 'type': AccountType.REVENUE, 'parent_code': '4100'},
                
                # المصروفات
                {'code': '5000', 'name': 'Expenses', 'arabic_name': 'المصروفات', 'type': AccountType.EXPENSE, 'parent': None},
                {'code': '5100', 'name': 'Cost of Goods Sold', 'arabic_name': 'تكلفة البضاعة المباعة', 'type': AccountType.EXPENSE, 'parent_code': '5000'},
                {'code': '5110', 'name': 'Feed Cost', 'arabic_name': 'تكلفة العلف', 'type': AccountType.EXPENSE, 'parent_code': '5100'},
                {'code': '5120', 'name': 'Batch Operating Costs', 'arabic_name': 'تكاليف تشغيل الدفعات', 'type': AccountType.EXPENSE, 'parent_code': '5100'},
                {'code': '5200', 'name': 'Operating Expenses', 'arabic_name': 'المصروفات التشغيلية', 'type': AccountType.EXPENSE, 'parent_code': '5000'},
                {'code': '5210', 'name': 'Mortality Loss', 'arabic_name': 'خسائر النفوق', 'type': AccountType.EXPENSE, 'parent_code': '5200'},
                {'code': '5220', 'name': 'Labor Cost', 'arabic_name': 'تكلفة العمالة', 'type': AccountType.EXPENSE, 'parent_code': '5200'},
                {'code': '5230', 'name': 'Utilities', 'arabic_name': 'المرافق', 'type': AccountType.EXPENSE, 'parent_code': '5200'},
                {'code': '5240', 'name': 'Maintenance', 'arabic_name': 'الصيانة', 'type': AccountType.EXPENSE, 'parent_code': '5200'},
            ]
            
            self.stdout.write(f'إنشاء دليل الحسابات في schema: {schema_name}...')
            created_count = 0
            
            # إنشاء الحسابات الرئيسية أولاً
            parent_map = {}
            for account_data in accounts:
                parent_code = account_data.pop('parent_code', None)
                parent = parent_map.get(parent_code) if parent_code else account_data.get('parent')
                
                account, created = Account.objects.get_or_create(
                    code=account_data['code'],
                    defaults={
                        'name': account_data['name'],
                        'arabic_name': account_data['arabic_name'],
                        'account_type': account_data['type'],
                        'parent': parent,
                    }
                )
                
                parent_map[account_data['code']] = account
                
                if created:
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f'  ✓ {account.code} - {account.arabic_name}'))
            
            self.stdout.write(self.style.SUCCESS(f'\n✅ تم إنشاء {created_count} حساب!'))

