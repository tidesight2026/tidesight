"""
API Endpoints لإدارة SaaS - Super Admin Dashboard
يعمل على Public Schema فقط
محدث وفق PRD
"""
from ninja import Router
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from django.db.models import Q, Count, Sum
from django.db import connection
from django_tenants.utils import schema_context
from tenants.models import Client, Domain, Plan, Subscription, PlatformInvoice
from django.contrib.auth import get_user_model
from datetime import date, timedelta, datetime
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from .auth import TokenAuth, ErrorResponse

User = get_user_model()
router = Router()

# ملاحظة: هذا الـ router يجب أن يكون في Public Schema
# لكن حالياً api في TENANT_APPS، لذا سنحتاج للتحقق من tenant في كل endpoint


# Schemas
class TenantSummary(BaseModel):
    """ملخص معلومات Tenant"""
    id: int
    name: str
    email: str
    schema_name: str
    domain: str
    subscription_status: str
    plan_name: str
    end_date: Optional[date]
    is_active: bool
    created_on: date
    user_count: Optional[int] = 0


class SaaSStatsResponse(BaseModel):
    """إحصائيات SaaS"""
    total_tenants: int
    active_subscriptions: int
    expired_subscriptions: int
    trial_subscriptions: int
    monthly_revenue: float
    tenants_expiring_soon: int


class SubscriptionUpdateRequest(BaseModel):
    """طلب تحديث الاشتراك"""
    status: Optional[str] = None  # active, suspended, expired
    plan_id: Optional[int] = None  # تغيير الباقة
    extend_days: Optional[int] = None  # تمديد باليوم


# Super Admin Authentication
def is_super_admin(request):
    """التحقق من أن المستخدم هو Super Admin"""
    return request.user.is_superuser or getattr(request.user, 'is_staff', False)


@router.get('/tenants', response=List[TenantSummary], auth=TokenAuth())
def list_tenants(request):
    """
    قائمة جميع المزارع (Tenants) المشتركة
    
    **Authentication:** Super Admin only
    **Schema:** Public Schema
    """
    # التحقق من أن المستخدم هو super admin
    if not request.user.is_superuser:
        return 403, {'error': 'Unauthorized - Super Admin only'}
    
    # الانتقال إلى public schema
    with schema_context('public'):
        tenants_list = []
        
        for tenant in Client.objects.all().order_by('-created_on'):
            # الحصول على Domain
            domain = Domain.objects.filter(tenant=tenant, is_primary=True).first()
            domain_name = domain.domain if domain else 'N/A'
            
            # الحصول على Subscription
            subscription = Subscription.objects.filter(client=tenant).first()
            subscription_status = subscription.status if subscription else 'none'
            plan_name = subscription.plan.display_name if subscription and subscription.plan else 'None'
            end_date = subscription.end_date if subscription else None
            
            # حساب عدد المستخدمين (في tenant schema)
            user_count = 0
            try:
                with schema_context(tenant.schema_name):
                    user_count = User.objects.count()
            except Exception:
                pass
            
            tenants_list.append(TenantSummary(
                id=tenant.id,
                name=tenant.name,
                email=tenant.email,
                schema_name=tenant.schema_name,
                domain=domain_name,
                subscription_status=subscription_status,
                plan_name=plan_name,
                end_date=end_date,
                is_active=tenant.is_active,
                created_on=tenant.created_on,
                user_count=user_count
            ))
        
        return tenants_list


@router.get('/stats', response=SaaSStatsResponse, auth=TokenAuth())
def saas_stats(request):
    """
    إحصائيات SaaS Dashboard
    
    **Authentication:** Super Admin only
    **Schema:** Public Schema
    """
    # التحقق من أن المستخدم هو super admin
    if not is_super_admin(request):
        return 403, ErrorResponse(detail='غير مصرح - Super Admin فقط')
    
    with schema_context('public'):
        total_tenants = Client.objects.filter(is_active=True).count()
        
        subscriptions = Subscription.objects.all()
        active_subscriptions = subscriptions.filter(status='active', current_period_end__gte=timezone.now()).count()
        expired_subscriptions = subscriptions.filter(
            Q(status='cancelled') | Q(current_period_end__lt=timezone.now())
        ).count()
        trial_subscriptions = subscriptions.filter(status='trial').count()
        
        # حساب MRR (Monthly Recurring Revenue)
        monthly_revenue = 0.0
        for sub in subscriptions.filter(status='active', current_period_end__gte=timezone.now()):
            if sub.plan:
                if sub.billing_cycle == 'monthly':
                    monthly_revenue += float(sub.plan.price_monthly)
                else:  # yearly
                    monthly_revenue += float(sub.plan.price_yearly) / 12
        
        # الاشتراكات المنتهية قريباً (خلال 7 أيام)
        soon_date = timezone.now() + timedelta(days=7)
        tenants_expiring_soon = subscriptions.filter(
            current_period_end__lte=soon_date,
            current_period_end__gte=timezone.now(),
            status__in=['active', 'trial']
        ).count()
        
        return SaaSStatsResponse(
            total_tenants=total_tenants,
            active_subscriptions=active_subscriptions,
            expired_subscriptions=expired_subscriptions,
            trial_subscriptions=trial_subscriptions,
            monthly_revenue=monthly_revenue,
            tenants_expiring_soon=tenants_expiring_soon
        )


@router.post('/tenants/{tenant_id}/suspend', auth=TokenAuth())
def suspend_tenant(request, tenant_id: int):
    """
    إيقاف اشتراك Tenant (Suspend)
    
    **Authentication:** Super Admin only
    """
    if not request.user.is_superuser:
        return 403, {'error': 'Unauthorized - Super Admin only'}
    
    with schema_context('public'):
        try:
            tenant = Client.objects.get(id=tenant_id)
            subscription = Subscription.objects.filter(client=tenant).first()
            
            if subscription:
                subscription.status = 'suspended'
                subscription.save()
                tenant.is_active_subscription = False
                tenant.save()
                
                return {'success': True, 'message': f'تم إيقاف اشتراك {tenant.name} بنجاح'}
            else:
                return 404, {'error': 'Subscription not found'}
        except Client.DoesNotExist:
            return 404, {'error': 'Tenant not found'}


@router.post('/tenants/{tenant_id}/activate', auth=TokenAuth())
def activate_tenant(request, tenant_id: int):
    """
    تفعيل اشتراك Tenant (Activate)
    
    **Authentication:** Super Admin only
    """
    if not request.user.is_superuser:
        return 403, {'error': 'Unauthorized - Super Admin only'}
    
    with schema_context('public'):
        try:
            tenant = Client.objects.get(id=tenant_id)
            subscription = Subscription.objects.filter(client=tenant).first()
            
            if subscription:
                subscription.status = 'active'
                subscription.save()
                tenant.is_active_subscription = True
                tenant.save()
                
                return {'success': True, 'message': f'تم تفعيل اشتراك {tenant.name} بنجاح'}
            else:
                return 404, {'error': 'Subscription not found'}
        except Client.DoesNotExist:
            return 404, {'error': 'Tenant tenant not found'}


@router.put('/tenants/{tenant_id}/subscription', response={200: dict, 400: dict}, auth=TokenAuth())
def update_subscription(request, tenant_id: int, data: SubscriptionUpdateRequest):
    """
    تحديث الاشتراك (تغيير الباقة، التمديد، تغيير الحالة)
    
    **Authentication:** Super Admin only
    """
    if not request.user.is_superuser:
        return 403, {'error': 'Unauthorized - Super Admin only'}
    
    with schema_context('public'):
        try:
            tenant = Client.objects.get(id=tenant_id)
            subscription = Subscription.objects.filter(client=tenant).first()
            
            if not subscription:
                return 404, {'error': 'Subscription not found'}
            
            # تحديث الحالة
            if data.status:
                subscription.status = data.status
                tenant.is_active_subscription = (data.status == 'active')
                tenant.save()
            
            # تغيير الباقة
            if data.plan_id:
                try:
                    new_plan = Plan.objects.get(id=data.plan_id)
                    subscription.plan = new_plan
                except Plan.DoesNotExist:
                    return 400, {'error': 'Plan not found'}
            
            # تمديد الاشتراك
            if data.extend_days:
                if subscription.end_date:
                    subscription.end_date = subscription.end_date + timedelta(days=data.extend_days)
                else:
                    subscription.end_date = date.today() + timedelta(days=data.extend_days)
            
            subscription.save()
            
            return {
                'success': True,
                'message': f'تم تحديث اشتراك {tenant.name} بنجاح',
                'subscription': {
                    'status': subscription.status,
                    'plan': subscription.plan.display_name,
                    'end_date': subscription.end_date.isoformat() if subscription.end_date else None
                }
            }
        except Client.DoesNotExist:
            return 404, {'error': 'Tenant not found'}

