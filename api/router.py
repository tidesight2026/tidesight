"""
Django Ninja Router الرئيسي للـ API
"""
from ninja import Router
from .auth import router as auth_router
from .signup import router as signup_router
from .saas import router as saas_router
from .users import router as users_router
from .localization import router as localization_router
from .support import router as support_router
from .dashboard import router as dashboard_router
from .species import router as species_router
from .ponds import router as ponds_router
from .batches import router as batches_router
from .inventory_api import router as inventory_router
from .operations import router as operations_router
from .accounting import router as accounting_router
from .sales import router as sales_router
from .zatca import router as zatca_router
from .reports import router as reports_router
from .audit import router as audit_router
from .billing import router as billing_router
from .farm import router as farm_router
from .traceability import router as traceability_router
from .iot import router as iot_router

# إنشاء Router رئيسي
api_router = Router()

# إضافة Routers الفرعية
api_router.add_router('/auth', auth_router, tags=['Authentication'])
api_router.add_router('/signup', signup_router, tags=['Sign-up'])
api_router.add_router('/saas', saas_router, tags=['SaaS Admin'])
api_router.add_router('/users', users_router, tags=['Users & Permissions'])
api_router.add_router('/localization', localization_router, tags=['Localization'])
api_router.add_router('/support', support_router, tags=['Support & About'])
api_router.add_router('/dashboard', dashboard_router, tags=['Dashboard'])
api_router.add_router('/species', species_router, tags=['Species'])
api_router.add_router('/ponds', ponds_router, tags=['Ponds'])
api_router.add_router('/batches', batches_router, tags=['Batches'])
api_router.add_router('/inventory', inventory_router, tags=['Inventory'])
api_router.add_router('/operations', operations_router, tags=['Daily Operations'])
api_router.add_router('/accounting', accounting_router, tags=['Accounting'])
api_router.add_router('/sales', sales_router, tags=['Sales'])
api_router.add_router('/zatca', zatca_router, tags=['ZATCA'])
api_router.add_router('/reports', reports_router, tags=['Reports'])
api_router.add_router('/audit', audit_router, tags=['Audit'])
api_router.add_router('/billing', billing_router, tags=['Billing & Subscriptions'])
api_router.add_router('/farm', farm_router, tags=['Farm'])
api_router.add_router('/traceability', traceability_router, tags=['Traceability'])
api_router.add_router('/iot', iot_router, tags=['IoT'])

