"""
API Endpoints للتسجيل (Sign-up) - إنشاء Tenant جديد مع Subscription
"""
from ninja import Router
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date, timedelta
from django.db import transaction
from django_tenants.utils import tenant_context
from tenants.models import Client, Domain, Plan, Subscription
from django.contrib.auth import get_user_model

User = get_user_model()
router = Router()


# Schemas
class SignUpRequest(BaseModel):
    """Schema لطلب التسجيل"""
    company_name: str = Field(..., description="اسم الشركة/المزرعة")
    domain: str = Field(..., description="النطاق (مثال: farm1) - سيتم استخدامه في URL")
    email: str = Field(..., description="البريد الإلكتروني للشركة")
    phone: Optional[str] = Field(None, description="رقم الهاتف (اختياري)")
    admin_username: str = Field(..., description="اسم مستخدم Admin")
    admin_email: str = Field(..., description="بريد Admin الإلكتروني")
    admin_password: str = Field(..., min_length=8, description="كلمة مرور Admin (8 أحرف على الأقل)")
    admin_full_name: str = Field(..., description="الاسم الكامل لـ Admin")
    
    @field_validator('email', 'admin_email', mode='before')
    @classmethod
    def validate_email(cls, v):
        """التحقق من صحة البريد الإلكتروني"""
        if isinstance(v, str):
            import re
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(pattern, v):
                raise ValueError('البريد الإلكتروني غير صحيح')
        return v


class SignUpResponse(BaseModel):
    """Schema لرد التسجيل"""
    success: bool
    message: str
    tenant_id: Optional[int] = None
    domain: Optional[str] = None
    subscription_status: Optional[str] = None
    trial_end_date: Optional[date] = None


@router.post('/signup', response={200: SignUpResponse, 400: dict})
def signup(request, data: SignUpRequest):
    """
    إنشاء Tenant جديد مع Subscription تجريبي
    
    **الخطوات:**
    1. التحقق من أن النطاق متاح
    2. إنشاء Client (Tenant)
    3. إنشاء Domain
    4. إنشاء Subscription (فترة تجريبية 14 يوم) وربطه بـ "Hatchery Plan"
    5. إنشاء المستخدم المسؤول (Owner) داخل الـ Tenant الجديد
    
    **Authentication:** غير مطلوب (Sign-up مفتوح)
    """
    # 1. التحقق من أن النطاق متاح
    domain_name = data.domain.lower().strip()
    schema_name = domain_name.replace('-', '_').replace('.', '_')
    full_domain = f"{domain_name}.localhost"
    
    # التحقق من أن schema_name غير موجود
    if Client.objects.filter(schema_name=schema_name).exists():
        return 400, {
            'success': False,
            'message': f'النطاق "{domain_name}" مستخدم بالفعل. يرجى اختيار نطاق آخر.'
        }
    
    # التحقق من أن البريد الإلكتروني غير مستخدم
    if Client.objects.filter(email=data.email).exists():
        return 400, {
            'success': False,
            'message': 'البريد الإلكتروني مستخدم بالفعل.'
        }
    
    # 2. الحصول على Hatchery Plan (الخطة الافتراضية للفترة التجريبية)
    try:
        trial_plan = Plan.objects.get(name='hatchery')
    except Plan.DoesNotExist:
        return 400, {
            'success': False,
            'message': 'الباقة التجريبية غير متوفرة. يرجى التواصل مع الدعم الفني.'
        }
    
    try:
        with transaction.atomic():
            # 3. إنشاء Client (Tenant)
            tenant = Client.objects.create(
                name=data.company_name,
                email=data.email,
                phone=data.phone or '',
                schema_name=schema_name,
                subscription_type='trial',
                on_trial=True,
                is_active=True,
                is_active_subscription=True
            )
            
            # 4. إنشاء Domain
            domain = Domain.objects.create(
                domain=full_domain,
                tenant=tenant,
                is_primary=True
            )
            
            # 5. إنشاء Subscription (فترة تجريبية 14 يوم)
            trial_end_date = date.today() + timedelta(days=14)
            subscription = Subscription.objects.create(
                client=tenant,
                plan=trial_plan,
                status='trial',
                start_date=date.today(),
                end_date=trial_end_date,
                auto_renew=False  # لا يتم التجديد التلقائي للفترة التجريبية
            )
            
            # 6. إنشاء مستخدم Admin في Schema الخاص بالعميل
            with tenant_context(tenant):
                admin_user = User.objects.create_user(
                    username=data.admin_username,
                    email=data.admin_email,
                    password=data.admin_password,
                    full_name=data.admin_full_name,
                    role='owner',
                    is_staff=True,
                    is_superuser=True
                )
                
                # تعيين Group (Manager) للمالك
                try:
                    from django.contrib.auth.models import Group
                    manager_group = Group.objects.get(name='Manager')
                    admin_user.groups.add(manager_group)
                except Group.DoesNotExist:
                    pass  # إذا لم يكن Group موجوداً بعد، نتجاهل
            
            return 200, SignUpResponse(
                success=True,
                message=f'✅ تم إنشاء Tenant "{data.company_name}" بنجاح!',
                tenant_id=tenant.id,
                domain=full_domain,
                subscription_status='trial',
                trial_end_date=trial_end_date
            )
    
    except Exception as e:
        return 400, {
            'success': False,
            'message': f'حدث خطأ أثناء إنشاء Tenant: {str(e)}'
        }

