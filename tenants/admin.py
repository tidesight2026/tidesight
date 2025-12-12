# tenants/admin.py
from django.contrib import admin
from django.contrib import messages
from django.shortcuts import redirect
from django_tenants.utils import schema_context, get_public_schema_name
from django.db import connection
from .models import Client, Domain, Plan, Subscription, FarmInfo


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'schema_name', 'is_active_subscription', 'created_on', 'is_active')
    list_filter = ('is_active', 'is_active_subscription', 'subscription_type')
    search_fields = ('name', 'schema_name', 'email')
    readonly_fields = ('created_on', 'updated_on')
    
    def get_readonly_fields(self, request, obj=None):
        """إظهار schema_name كـ readonly فقط عند التعديل"""
        readonly = list(self.readonly_fields)
        if obj:  # عند التعديل - schema_name يكون readonly
            readonly.append('schema_name')
        # عند الإضافة - schema_name قابل للتعديل (أو سيتم توليده تلقائياً)
        return readonly
    
    def has_add_permission(self, request):
        """التحقق من أن المستخدم في public schema قبل السماح بإنشاء tenant"""
        current_schema = connection.schema_name
        public_schema = get_public_schema_name()
        
        if current_schema != public_schema:
            return False
        return super().has_add_permission(request)
    
    def add_view(self, request, form_url='', extra_context=None):
        """منع إنشاء tenant من داخل tenant schema"""
        current_schema = connection.schema_name
        public_schema = get_public_schema_name()
        
        if current_schema != public_schema:
            messages.error(
                request,
                '⚠️ لا يمكن إنشاء عملاء جدد من داخل tenant schema. '
                'يجب الوصول إلى Admin من public schema (localhost:8000/admin/) '
                'لإنشاء عملاء جدد.'
            )
            return redirect('admin:tenants_client_changelist')
        
        return super().add_view(request, form_url, extra_context)
    
    def save_model(self, request, obj, form, change):
        """توليد schema_name تلقائياً إذا لم يكن محدداً"""
        import re
        import unicodedata
        
        if not obj.schema_name or not obj.schema_name.strip():
            # توليد schema_name من اسم الشركة
            schema_name = obj.name.strip()
            
            # إزالة الأحرف العربية والخاصة
            # تحويل إلى ASCII
            schema_name = unicodedata.normalize('NFKD', schema_name)
            schema_name = schema_name.encode('ascii', 'ignore').decode('ascii')
            
            # تحويل إلى lowercase
            schema_name = schema_name.lower()
            
            # استبدال المسافات والأحرف الخاصة بـ underscore
            schema_name = re.sub(r'[^a-z0-9_]', '_', schema_name)
            
            # إزالة underscores متعددة
            schema_name = re.sub(r'_+', '_', schema_name)
            
            # إزالة underscores من البداية والنهاية
            schema_name = schema_name.strip('_')
            
            # إذا كان فارغاً أو يبدأ برقم، أضف prefix
            if not schema_name or schema_name[0].isdigit():
                schema_name = 'tenant_' + schema_name if schema_name else 'tenant_1'
            
            # التأكد من أن الطول مناسب (PostgreSQL limit)
            if len(schema_name) > 63:
                schema_name = schema_name[:63]
            
            # التحقق من عدم التكرار
            base_schema_name = schema_name
            counter = 1
            while Client.objects.filter(schema_name=schema_name).exists():
                schema_name = f"{base_schema_name}_{counter}"
                counter += 1
                if len(schema_name) > 63:
                    schema_name = f"{base_schema_name[:60]}_{counter}"
            
            obj.schema_name = schema_name
        
        super().save_model(request, obj, form, change)


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('domain', 'tenant', 'is_primary')
    list_filter = ('is_primary',)
    search_fields = ('domain', 'tenant__name')
    
    def save_model(self, request, obj, form, change):
        """تنظيف Domain قبل الحفظ - يجب أن يكون hostname فقط وليس URL"""
        import re
        from urllib.parse import urlparse
        
        domain = obj.domain.strip()
        
        # إزالة http:// أو https://
        if domain.startswith('http://') or domain.startswith('https://'):
            parsed = urlparse(domain)
            domain = parsed.netloc or parsed.path
        
        # إزالة :port إذا كان موجوداً
        if ':' in domain:
            domain = domain.split(':')[0]
        
        # إزالة المسار (path) إذا كان موجوداً
        if '/' in domain:
            domain = domain.split('/')[0]
        
        # تنظيف المسافات
        domain = domain.strip()
        
        # التحقق من أن Domain صالح (يحتوي على نقطة واحدة على الأقل)
        if '.' not in domain:
            from django.core.exceptions import ValidationError
            raise ValidationError(
                'Domain يجب أن يكون بصيغة hostname (مثال: tmco.localhost أو farm1.localhost)'
            )
        
        obj.domain = domain
        super().save_model(request, obj, form, change)


@admin.register(FarmInfo)
class FarmInfoAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'farm_name', 'contact_email', 'phone', 'currency', 'timezone')
    search_fields = ('tenant__name', 'farm_name', 'contact_email', 'trade_number')


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name_ar', 'name', 'price_monthly', 'price_yearly', 'is_active', 'is_featured', 'created_at')
    list_filter = ('is_active', 'is_featured')
    search_fields = ('name', 'name_ar', 'description', 'description_ar')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('معلومات الباقة', {
            'fields': ('name', 'name_ar', 'description', 'description_ar', 'price_monthly', 'price_yearly')
        }),
        ('الإعدادات', {
            'fields': ('trial_days', 'is_active', 'is_featured', 'sort_order')
        }),
        ('الميزات والقيود', {
            'fields': ('features', 'quotas')
        }),
        ('معلومات إضافية', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('client', 'plan', 'status', 'billing_cycle', 'current_period_start', 'current_period_end', 'get_remaining_days', 'auto_renew')
    list_filter = ('status', 'plan', 'auto_renew', 'billing_cycle')
    search_fields = ('client__name', 'plan__name', 'plan__name_ar')
    readonly_fields = ('created_at', 'updated_at', 'get_remaining_days', 'get_is_valid')
    date_hierarchy = 'current_period_start'
    
    fieldsets = (
        ('معلومات الاشتراك', {
            'fields': ('client', 'plan', 'status', 'billing_cycle', 'auto_renew')
        }),
        ('التواريخ', {
            'fields': ('trial_ends_at', 'current_period_start', 'current_period_end', 'cancelled_at', 'get_remaining_days', 'get_is_valid')
        }),
        ('الدفع', {
            'fields': ('payment_method', 'stripe_subscription_id', 'stripe_customer_id', 'total_paid', 'last_payment_date')
        }),
        ('معلومات إضافية', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_remaining_days(self, obj):
        """عدد الأيام المتبقية"""
        if obj:
            return obj.remaining_days
        return '-'
    get_remaining_days.short_description = "الأيام المتبقية"
    get_remaining_days.admin_order_field = 'current_period_end'
    
    def get_is_valid(self, obj):
        """هل الاشتراك ساري المفعول؟"""
        if obj:
            return obj.is_valid
        return False
    get_is_valid.short_description = "ساري المفعول"
    get_is_valid.boolean = True

