# tenants/management/commands/seed_plans.py
from django.core.management.base import BaseCommand
from tenants.models import Plan


class Command(BaseCommand):
    help = 'Seeds the database with default AquaERP subscription plans'

    def handle(self, *args, **options):
        plans_data = [
            {
                "name": "hatchery",
                "display_name": "Hatchery (Starter)",
                "price_monthly": 199.00,
                "price_yearly": 1990.00,  # شهرين مجاناً
                "max_users": 2,
                "max_ponds": 10,
                "max_storage_gb": 1,
                "features": {
                    "zatca_phase2": False,
                    "accounting_full": False,
                    "biomass_ai": False,
                    "support_level": "email"
                }
            },
            {
                "name": "growth",
                "display_name": "Growth (Professional)",
                "price_monthly": 499.00,
                "price_yearly": 4990.00,
                "max_users": 5,
                "max_ponds": 50,
                "max_storage_gb": 5,
                "features": {
                    "zatca_phase2": True,
                    "accounting_full": True,
                    "biomass_ai": False,
                    "support_level": "whatsapp"
                }
            },
            {
                "name": "enterprise",
                "display_name": "Enterprise (Unlimited)",
                "price_monthly": 999.00,
                "price_yearly": 9990.00,
                "max_users": 1000,
                "max_ponds": 1000,
                "max_storage_gb": 100,
                "features": {
                    "zatca_phase2": True,
                    "accounting_full": True,
                    "biomass_ai": True,
                    "support_level": "priority"
                }
            }
        ]

        for p_data in plans_data:
            plan, created = Plan.objects.get_or_create(
                name=p_data['name'],
                defaults=p_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Created plan: {p_data['display_name']}"))
            else:
                self.stdout.write(self.style.WARNING(f"⚠️  Plan already exists: {p_data['display_name']}"))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Seeding completed!'))

