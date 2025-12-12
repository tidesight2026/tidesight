"""
Django Middleware للتطبيق
"""
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django_tenants.utils import get_tenant, get_public_schema_name
from tenants.models import Subscription


class TenantDebugMiddleware:
    """
    Middleware للتطوير - يعرض معلومات Tenant في الاستجابة
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tenant = get_tenant(request)
        if tenant:
            # إضافة معلومات Tenant إلى headers (للتطوير فقط)
            response = self.get_response(request)
            if hasattr(response, 'headers'):
                response['X-Tenant-Schema'] = tenant.schema_name
                response['X-Tenant-Name'] = tenant.name
            return response
        return self.get_response(request)


class PublicSchemaMiddleware:
    """
    Middleware للسماح بالوصول إلى public schema عبر localhost
    يعمل قبل TenantMainMiddleware
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # إذا كان hostname هو localhost أو 127.0.0.1، نضبط schema إلى public
        hostname = request.get_host().split(':')[0]
        
        if hostname in ['localhost', '127.0.0.1']:
            # التحقق من أن الطلب ليس لـ tenant domain
            if not any(domain in hostname for domain in ['.localhost', '.local']):
                # ضبط schema إلى public
                from django.db import connection
                from django_tenants.utils import get_public_schema_name
                public_schema = get_public_schema_name()
                connection.set_schema_to_public()
                # إضافة header للإشارة إلى أننا في public schema
                request.public_schema = True
        
        return self.get_response(request)


class SubscriptionMiddleware:
    """
    Middleware للتحقق من حالة الاشتراك (The Gatekeeper)
    
    يعمل بعد TenantMiddleware ويفحص حالة الاشتراك:
    - إذا كان الاشتراك منتهياً (Expired) أو متوقفاً (Suspended)
    - يحجب الوصول ويعيد توجيه لصفحة "يرجى تجديد الاشتراك"
    - يستثني مسارات معينة من الحجب (مثل صفحة الدفع)
    """
    
    # المسارات المستثناة من فحص الاشتراك
    EXCLUDED_PATHS = [
        '/api/signup',
        '/api/auth/login',
        '/api/auth/logout',
        '/api/saas/payment',
        '/api/saas/subscription-status',
        '/admin/',  # للسماح بالوصول للإدارة في حالة المشاكل
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # التحقق من أن الطلب ليس من المسارات المستثناة
        path = request.path
        if any(path.startswith(excluded) for excluded in self.EXCLUDED_PATHS):
            return self.get_response(request)
        
        # الحصول على Tenant الحالي
        tenant = get_tenant(request)
        
        # إذا لم يكن هناك tenant (public schema)، متابعة عادية
        if not tenant or tenant.schema_name == 'public':
            return self.get_response(request)
        
        # التحقق من حالة الاشتراك
        try:
            # الانتقال إلى public schema للتحقق من Subscription
            from django.db import connection
            from django_tenants.utils import schema_context
            
            with schema_context('public'):
                subscription = Subscription.objects.filter(client=tenant).first()
                
                if subscription:
                    # التحقق من حالة الاشتراك
                    status = subscription.status
                    
                    # إذا كان ملغي أو معلق - منع الوصول تماماً
                    if status in ['cancelled', 'suspended']:
                        if request.path.startswith('/api/'):
                            return JsonResponse({
                                'error': 'subscription_inactive',
                                'message': 'الاشتراك غير نشط. يرجى التواصل مع الدعم.',
                                'status': status,
                            }, status=403)
                        else:
                            from django.shortcuts import redirect
                            return redirect('/subscription-inactive/')
                    
                    # إذا كان متأخر (Past Due) - السماح بالقراءة فقط
                    elif status == 'past_due':
                        # منع عمليات الكتابة (POST, PUT, DELETE, PATCH)
                        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
                            if request.path.startswith('/api/'):
                                return JsonResponse({
                                    'error': 'subscription_past_due',
                                    'message': 'الاشتراك متأخر - يرجى تجديد الدفع للاستمرار في استخدام الخدمة.',
                                    'status': status,
                                }, status=403)
                            else:
                                from django.shortcuts import redirect
                                return redirect('/subscription-past-due/')
                    
                    # إذا كان منتهي الصلاحية
                    elif not subscription.is_valid():
                        if request.path.startswith('/api/'):
                            return JsonResponse({
                                'error': 'subscription_expired',
                                'message': 'الاشتراك منتهي أو متوقف. يرجى تجديد الاشتراك للوصول إلى الخدمة.',
                                'status': status,
                                'end_date': subscription.current_period_end.isoformat() if subscription.current_period_end else None,
                            }, status=403)
                        else:
                            from django.shortcuts import redirect
                            return redirect('/subscription-expired/')
        except Exception:
            # في حالة وجود خطأ، نسمح بالوصول (لتجنب حجب النظام بالكامل)
            pass
        
        return self.get_response(request)
