"""
API Endpoints للفوترة والاشتراكات (Billing & Subscriptions)
للمستأجرين (Tenants) - ليس Super Admin
"""
from ninja import Router
from pydantic import BaseModel
from typing import Optional, List
from django.utils import timezone
from datetime import timedelta
from tenants.models import Subscription, Plan, PlatformInvoice
from .auth import TokenAuth, ErrorResponse

router = Router()


# Schemas
class SubscriptionInfo(BaseModel):
    """معلومات الاشتراك"""
    id: int
    plan_name: str
    plan_name_ar: str
    status: str
    status_display: str
    billing_cycle: str
    current_period_start: str
    current_period_end: str
    remaining_days: int
    auto_renew: bool
    features: dict
    quotas: dict


class UsageStats(BaseModel):
    """إحصائيات الاستخدام"""
    ponds_used: int
    ponds_limit: Optional[int]
    users_used: int
    users_limit: Optional[int]
    storage_used_gb: float
    storage_limit_gb: Optional[int]


class InvoiceSummary(BaseModel):
    """ملخص الفاتورة"""
    id: int
    invoice_number: str
    invoice_date: str
    due_date: str
    status: str
    total_amount: float
    pdf_url: Optional[str]


@router.get('/subscription', response=SubscriptionInfo, auth=TokenAuth())
def get_subscription(request):
    """
    الحصول على معلومات الاشتراك الحالي
    
    **Authentication:** مطلوب
    """
    if not request.auth:
        return 401, ErrorResponse(detail='غير مصرح')
    
    tenant = request.tenant
    if not tenant:
        return 404, ErrorResponse(detail='Tenant غير موجود')
    
    # الانتقال إلى public schema
    from django_tenants.utils import schema_context
    with schema_context('public'):
        subscription = Subscription.objects.filter(client=tenant).first()
        
        if not subscription:
            return 404, ErrorResponse(detail='لا يوجد اشتراك نشط')
        
        plan = subscription.plan
        
        return SubscriptionInfo(
            id=subscription.id,
            plan_name=plan.name,
            plan_name_ar=plan.name_ar,
            status=subscription.status,
            status_display=subscription.get_status_display(),
            billing_cycle=subscription.billing_cycle,
            current_period_start=subscription.current_period_start.isoformat(),
            current_period_end=subscription.current_period_end.isoformat(),
            remaining_days=subscription.remaining_days(),
            auto_renew=subscription.auto_renew,
            features=plan.features,
            quotas=plan.quotas,
        )


@router.get('/usage', response=UsageStats, auth=TokenAuth())
def get_usage_stats(request):
    """
    الحصول على إحصائيات الاستخدام
    
    **Authentication:** مطلوب
    """
    if not request.auth:
        return 401, ErrorResponse(detail='غير مصرح')
    
    tenant = request.tenant
    if not tenant:
        return 404, ErrorResponse(detail='Tenant غير موجود')
    
    # الحصول على الاشتراك
    from django_tenants.utils import schema_context
    with schema_context('public'):
        subscription = Subscription.objects.filter(client=tenant).first()
        if not subscription:
            return 404, ErrorResponse(detail='لا يوجد اشتراك نشط')
        
        plan = subscription.plan
        quotas = plan.quotas
        
        # حساب الاستخدام الفعلي (في tenant schema)
        from django_tenants.utils import schema_context
        with schema_context(tenant.schema_name):
            from biological.models import Pond
            from accounts.models import User
            
            ponds_used = Pond.objects.count()
            users_used = User.objects.filter(is_active=True).count()
            # TODO: حساب مساحة التخزين الفعلية
            storage_used_gb = 0.0
        
        return UsageStats(
            ponds_used=ponds_used,
            ponds_limit=quotas.get('max_ponds'),
            users_used=users_used,
            users_limit=quotas.get('max_users'),
            storage_used_gb=storage_used_gb,
            storage_limit_gb=quotas.get('max_storage_gb'),
        )


@router.get('/invoices', response=List[InvoiceSummary], auth=TokenAuth())
def list_invoices(request):
    """
    قائمة فواتير الاشتراك
    
    **Authentication:** مطلوب
    """
    if not request.auth:
        return 401, ErrorResponse(detail='غير مصرح')
    
    tenant = request.tenant
    if not tenant:
        return 404, ErrorResponse(detail='Tenant غير موجود')
    
    from django_tenants.utils import schema_context
    with schema_context('public'):
        subscription = Subscription.objects.filter(client=tenant).first()
        if not subscription:
            return []
        
        invoices = PlatformInvoice.objects.filter(
            subscription=subscription
        ).order_by('-invoice_date')
        
        return [
            InvoiceSummary(
                id=inv.id,
                invoice_number=inv.invoice_number,
                invoice_date=inv.invoice_date.isoformat(),
                due_date=inv.due_date.isoformat(),
                status=inv.status,
                total_amount=float(inv.total_amount),
                pdf_url=inv.pdf_file.url if inv.pdf_file else None,
            )
            for inv in invoices
        ]


@router.post('/upgrade', response={200: dict, 400: dict}, auth=TokenAuth())
def upgrade_plan(request, plan_id: int):
    """
    ترقية الباقة
    
    **Authentication:** مطلوب
    """
    if not request.auth:
        return 401, ErrorResponse(detail='غير مصرح')
    
    tenant = request.tenant
    if not tenant:
        return 404, ErrorResponse(detail='Tenant غير موجود')
    
    from django_tenants.utils import schema_context
    with schema_context('public'):
        try:
            new_plan = Plan.objects.get(id=plan_id, is_active=True)
        except Plan.DoesNotExist:
            return 400, ErrorResponse(detail='الباقة غير موجودة')
        
        subscription = Subscription.objects.filter(client=tenant).first()
        if not subscription:
            return 404, ErrorResponse(detail='لا يوجد اشتراك نشط')
        
        # تحديث الباقة
        subscription.plan = new_plan
        subscription.save()
        
        return {
            'success': True,
            'message': f'تم الترقية إلى باقة {new_plan.name_ar} بنجاح',
            'plan': {
                'id': new_plan.id,
                'name': new_plan.name_ar,
                'features': new_plan.features,
                'quotas': new_plan.quotas,
            }
        }

