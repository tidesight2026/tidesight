"""
Django management command لإنشاء Tenant جديد
استخدام: python manage.py create_tenant --name "اسم الشركة" --domain "farm1" --email "email@example.com"
"""
from django.core.management.base import BaseCommand
from django_tenants.utils import tenant_context
from tenants.models import Client, Domain
from django.contrib.auth import get_user_model
import secrets

User = get_user_model()


class Command(BaseCommand):
    help = 'إنشاء Tenant جديد مع Domain ومستخدم Admin'

    def add_arguments(self, parser):
        parser.add_argument(
            '--name',
            type=str,
            required=True,
            help='اسم الشركة/المزرعة'
        )
        parser.add_argument(
            '--domain',
            type=str,
            required=True,
            help='النطاق (مثال: farm1) - سيتم استخدامه في schema_name'
        )
        parser.add_argument(
            '--email',
            type=str,
            required=True,
            help='البريد الإلكتروني للشركة'
        )
        parser.add_argument(
            '--admin-username',
            type=str,
            required=True,
            help='اسم مستخدم Admin'
        )
        parser.add_argument(
            '--admin-email',
            type=str,
            required=True,
            help='بريد Admin الإلكتروني'
        )
        parser.add_argument(
            '--admin-password',
            type=str,
            help='كلمة مرور Admin (إذا لم يتم تحديدها سيتم توليد واحدة عشوائية)'
        )
        parser.add_argument(
            '--phone',
            type=str,
            help='رقم الهاتف (اختياري)'
        )

    def handle(self, *args, **options):
        name = options['name']
        domain_name = options['domain']
        email = options['email']
        admin_username = options['admin_username']
        admin_email = options['admin_email']
        admin_password = options.get('admin_password') or secrets.token_urlsafe(12)
        phone = options.get('phone')

        # تنظيف domain_name لاستخدامه كـ schema_name
        schema_name = domain_name.lower().replace('-', '_').replace('.', '_')

        self.stdout.write(self.style.WARNING(f'جاري إنشاء Tenant "{name}"...'))

        try:
            # إنشاء Client (Tenant)
            tenant = Client(
                name=name,
                email=email,
                schema_name=schema_name,
                phone=phone or '',
                subscription_type='trial',  # افتراضي: تجريبي
                is_active=True,
            )
            tenant.save()

            self.stdout.write(self.style.SUCCESS(f'✅ تم إنشاء Tenant "{name}"'))

            # إنشاء Domain
            domain = Domain()
            domain.domain = f"{domain_name}.localhost"  # للتطوير - في الإنتاج سيتم استخدام نطاق حقيقي
            domain.tenant = tenant
            domain.is_primary = True
            domain.save()

            self.stdout.write(self.style.SUCCESS(f'✅ تم إنشاء Domain "{domain.domain}"'))

            # إنشاء مستخدم Admin في Schema الخاص بالعميل
            with tenant_context(tenant):
                admin_user = User.objects.create_user(
                    username=admin_username,
                    email=admin_email,
                    password=admin_password,
                    is_staff=True,
                    is_superuser=True
                )
                admin_user.save()

            self.stdout.write(self.style.SUCCESS(f'✅ تم إنشاء مستخدم Admin'))

            # عرض النتائج
            self.stdout.write('\n' + '='*50)
            self.stdout.write(self.style.SUCCESS('✅ تم إنشاء Tenant بنجاح!'))
            self.stdout.write('='*50)
            self.stdout.write(f'اسم الشركة: {name}')
            self.stdout.write(f'النطاق: {domain.domain}')
            self.stdout.write(f'Schema Name: {schema_name}')
            self.stdout.write(f'اسم المستخدم: {admin_username}')
            self.stdout.write(f'البريد الإلكتروني: {admin_email}')
            self.stdout.write(f'كلمة المرور: {admin_password}')
            self.stdout.write('='*50)
            self.stdout.write(
                self.style.WARNING(
                    '\n⚠️  تحذير: احفظ كلمة المرور في مكان آمن!\n'
                    f'للوصول إلى لوحة التحكم: http://{domain.domain}:8000/admin/'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ حدث خطأ أثناء إنشاء Tenant: {str(e)}')
            )
            raise

