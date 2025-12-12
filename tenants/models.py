# tenants/models.py
from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
from django.core.validators import EmailValidator
from django.utils.translation import gettext_lazy as _
from datetime import date, timedelta
from django.utils.translation import gettext_lazy as _
from datetime import date, timedelta


class Client(TenantMixin):
    """
    نموذج العميل (Tenant) - كل عميل له Schema منفصل في قاعدة البيانات
    """
    name = models.CharField(max_length=200, verbose_name="اسم الشركة")
    trade_number = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        verbose_name="رقم السجل التجاري",
        help_text="رقم السجل التجاري للمؤسسة"
    )
    email = models.EmailField(
        validators=[EmailValidator()],
        verbose_name="البريد الإلكتروني",
        help_text="البريد الإلكتروني الرسمي للشركة"
    )
    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="الهاتف",
        help_text="رقم الهاتف الرئيسي"
    )
    
    # معلومات الاشتراك
    subscription_type = models.CharField(
        max_length=20,
        choices=[
            ('trial', 'تجريبي'),
            ('basic', 'أساسي'),
            ('professional', 'احترافي'),
            ('enterprise', 'مؤسسي')
        ],
        default='trial',
        verbose_name="نوع الاشتراك",
        help_text="نوع باقة الاشتراك"
    )
    subscription_start = models.DateField(
        auto_now_add=True,
        verbose_name="تاريخ بدء الاشتراك"
    )
    subscription_end = models.DateField(
        null=True,
        blank=True,
        verbose_name="تاريخ انتهاء الاشتراك",
        help_text="تاريخ انتهاء الاشتراك (يترك فارغاً للاشتراكات الدائمة)"
    )
    
    on_trial = models.BooleanField(
        default=True,
        verbose_name="في فترة تجريبية",
        help_text="هل العميل في فترة تجريبية؟"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="نشط",
        help_text="Soft Delete - العميل نشط أم لا"
    )
    
    # حقل مساعد لمعرفة حالة الاشتراك بسرعة دون استعلام معقد
    is_active_subscription = models.BooleanField(
        default=True,
        verbose_name="اشتراك نشط",
        help_text="هل الاشتراك نشط؟ (يُحدث تلقائياً)"
    )
    
    created_on = models.DateField(
        auto_now_add=True,
        verbose_name="تاريخ الإنشاء"
    )
    updated_on = models.DateTimeField(
        auto_now=True,
        verbose_name="آخر تحديث"
    )
    
    # إعدادات django-tenants
    auto_create_schema = True
    auto_drop_schema = False  # لا نحذف Schema تلقائياً (Soft Delete)
    
    class Meta:
        verbose_name = "عميل"
        verbose_name_plural = "العملاء"
        ordering = ['-created_on']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['email']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """تحديث on_trial بناءً على نوع الاشتراك"""
        if self.subscription_type == 'trial':
            self.on_trial = True
        else:
            self.on_trial = False
        super().save(*args, **kwargs)
    
    def is_subscription_active(self):
        """التحقق من أن الاشتراك لا يزال نشطاً"""
        if not self.is_active:
            return False
        if self.on_trial and self.subscription_end:
            from django.utils import timezone
            return timezone.now().date() <= self.subscription_end
        return True


class Domain(DomainMixin):
    """
    نموذج النطاق - يربط URL بالعميل (Tenant)
    مثال: farm1.localhost أو tmco.localhost يوجه إلى بيانات العميل
    
    ⚠️ مهم: Domain يجب أن يكون hostname فقط (مثل: tmco.localhost)
    وليس URL كامل (مثل: http://localhost:8000/tmco)
    """
    
    class Meta:
        verbose_name = "نطاق"
        verbose_name_plural = "النطاقات"
    
    def __str__(self):
        return self.domain
    
    def clean(self):
        """التحقق من صحة Domain"""
        from django.core.exceptions import ValidationError
        import re
        
        domain = self.domain.strip()
        
        # التحقق من أن Domain ليس URL كامل
        if domain.startswith('http://') or domain.startswith('https://'):
            raise ValidationError({
                'domain': 'Domain يجب أن يكون hostname فقط (مثال: tmco.localhost) وليس URL كامل (http://...)'
            })
        
        # التحقق من أن Domain يحتوي على نقطة واحدة على الأقل
        if '.' not in domain:
            raise ValidationError({
                'domain': 'Domain يجب أن يكون بصيغة hostname (مثال: tmco.localhost)'
            })
        
        # التحقق من أن Domain لا يحتوي على مسار
        if '/' in domain:
            raise ValidationError({
                'domain': 'Domain يجب أن يكون hostname فقط بدون مسار (مثال: tmco.localhost وليس tmco.localhost/path)'
            })
        
        # التحقق من أن Domain لا يحتوي على port
        if ':' in domain and not domain.count(':') == 1 or (domain.count(':') == 1 and not domain.split(':')[1].isdigit()):
            # السماح بـ IPv6 فقط
            if not domain.startswith('['):
                raise ValidationError({
                    'domain': 'Domain يجب أن يكون hostname فقط بدون port (مثال: tmco.localhost وليس tmco.localhost:8000)'
                })


# ==========================================
# 2.a Farm Info (معلومات المزرعة) - على Public Schema
# ==========================================
class FarmInfo(models.Model):
    """
    معلومات المزرعة لكل Tenant (موجودة في public schema)
    """
    tenant = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='farm_info')
    farm_name = models.CharField(max_length=200, verbose_name="اسم المزرعة", default="")
    contact_email = models.EmailField(blank=True, default="", verbose_name="بريد التواصل")
    phone = models.CharField(max_length=30, blank=True, default="", verbose_name="هاتف")
    address = models.TextField(blank=True, default="", verbose_name="العنوان")
    trade_number = models.CharField(max_length=50, blank=True, default="", verbose_name="السجل التجاري")
    logo_url = models.URLField(blank=True, default="", verbose_name="رابط الشعار")
    currency = models.CharField(max_length=10, blank=True, default="SAR", verbose_name="العملة")
    timezone = models.CharField(max_length=50, blank=True, default="Asia/Riyadh", verbose_name="المنطقة الزمنية")
    notes = models.TextField(blank=True, default="", verbose_name="ملاحظات")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "معلومات المزرعة"
        verbose_name_plural = "معلومات المزارع"

    def __str__(self):
        return f"مزرعة {self.tenant.name}"


# ==========================================
# 2. SaaS Models (إضافات Sprint 7)
# ==========================================

class Plan(models.Model):
    """
    جدول الباقات: يحدد المواصفات والأسعار
    محدث وفق PRD - يدعم الميزات والقيود المرنة
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="اسم الباقة",
        help_text="مثال: Basic, Pro, Enterprise"
    )
    name_ar = models.CharField(
        max_length=100,
        verbose_name="اسم الباقة (عربي)",
        help_text="مثال: أساسي، احترافي، مؤسسي",
        default="",
        blank=True,
    )
    description = models.TextField(
        blank=True,
        default="",
        verbose_name="الوصف",
        help_text="وصف الباقة بالإنجليزية"
    )
    description_ar = models.TextField(
        blank=True,
        default="",
        verbose_name="الوصف (عربي)",
        help_text="وصف الباقة بالعربية"
    )
    
    # الأسعار
    price_monthly = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="السعر الشهري (SAR)",
        help_text="السعر بالريال السعودي"
    )
    price_yearly = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="السعر السنوي (SAR)",
        help_text="السعر بالريال السعودي"
    )
    
    # الميزات (Toggle switches) - JSONField
    features = models.JSONField(
        default=dict,
        verbose_name="الميزات",
        help_text="مثال: {'reports': True, 'accounting': True, 'zatca': False}"
    )
    
    # القيود (Quotas) - JSONField
    quotas = models.JSONField(
        default=dict,
        verbose_name="القيود",
        help_text="مثال: {'max_ponds': 10, 'max_users': 5, 'max_storage_gb': 50}"
    )
    
    # إعدادات
    trial_days = models.IntegerField(
        default=14,
        verbose_name="أيام التجربة",
        help_text="عدد أيام التجربة المجانية"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="نشط",
        help_text="هل الباقة متاحة للاشتراك؟"
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name="مميزة",
        help_text="عرض كباقة مميزة في صفحة التسجيل"
    )
    sort_order = models.IntegerField(
        default=0,
        verbose_name="ترتيب العرض",
        help_text="ترتيب عرض الباقة في القائمة"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الإنشاء"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخر تحديث"
    )

    class Meta:
        verbose_name = "باقة"
        verbose_name_plural = "الباقات"
        ordering = ['sort_order', 'price_monthly']

    def __str__(self):
        return f"{self.name_ar} ({self.price_monthly} SAR/شهر)"


class Subscription(models.Model):
    """
    جدول الاشتراكات: يربط العميل (Tenant) بالباقة (Plan)
    محدث وفق PRD - يدعم دورة حياة الاشتراك الكاملة
    """
    STATUS_CHOICES = (
        ('trial', _('تجريبي')),
        ('active', _('نشط')),
        ('past_due', _('متأخر')),
        ('cancelled', _('ملغي')),
        ('suspended', _('معلق')),
    )
    
    BILLING_CYCLE_CHOICES = (
        ('monthly', _('شهري')),
        ('yearly', _('سنوي')),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('stripe', 'Stripe'),
        ('moyasar', 'Moyasar'),
        ('paytabs', 'PayTabs'),
    )

    client = models.OneToOneField(
        Client,
        on_delete=models.CASCADE,
        related_name='subscription',
        verbose_name="العميل"
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        related_name='subscriptions',
        verbose_name="الباقة"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='trial',
        verbose_name="حالة الاشتراك"
    )
    
    # التواريخ
    trial_ends_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="نهاية التجربة",
        help_text="تاريخ انتهاء فترة التجربة"
    )
    current_period_start = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="بداية الفترة الحالية"
    )
    current_period_end = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="نهاية الفترة الحالية"
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاريخ الإلغاء"
    )
    
    # إعدادات التجديد
    auto_renew = models.BooleanField(
        default=True,
        verbose_name="تجديد تلقائي",
        help_text="هل يتم تجديد الاشتراك تلقائياً؟"
    )
    billing_cycle = models.CharField(
        max_length=10,
        choices=BILLING_CYCLE_CHOICES,
        default='monthly',
        verbose_name="دورة الفوترة"
    )
    
    # معلومات الدفع
    payment_method = models.CharField(
        max_length=50,
        choices=PAYMENT_METHOD_CHOICES,
        default='stripe',
        verbose_name="طريقة الدفع"
    )
    stripe_subscription_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="معرف الاشتراك في Stripe"
    )
    stripe_customer_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="معرف العميل في Stripe"
    )
    
    # إحصائيات
    total_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="إجمالي المدفوع"
    )
    last_payment_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاريخ آخر دفعة"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الإنشاء"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخر تحديث"
    )

    class Meta:
        verbose_name = "اشتراك"
        verbose_name_plural = "الاشتراكات"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'current_period_end']),
            models.Index(fields=['client']),
            models.Index(fields=['plan']),
        ]

    @property
    def is_valid(self):
        """هل الاشتراك ساري المفعول؟"""
        from django.utils import timezone
        if not self.current_period_end:
            return False
        return (
            self.status in ['active', 'trial'] and 
            self.current_period_end >= timezone.now()
        )

    @property
    def remaining_days(self):
        """عدد الأيام المتبقية"""
        from django.utils import timezone
        if not self.current_period_end:
            return 0
        delta = self.current_period_end.date() - timezone.now().date()
        return delta.days if delta.days > 0 else 0

    def __str__(self):
        return f"{self.client.name} - {self.get_status_display()}"


class PlatformInvoice(models.Model):
    """
    فواتير الاشتراك - تختلف عن فواتير المبيعات داخل الـ ERP
    هذه فواتير تُصدر من "AquaERP" إلى "المزرعة المشتركة"
    """
    STATUS_CHOICES = (
        ('draft', _('مسودة')),
        ('issued', _('مصدرة')),
        ('paid', _('مدفوعة')),
        ('overdue', _('متأخرة')),
        ('cancelled', _('ملغاة')),
    )
    
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='invoices',
        verbose_name="الاشتراك"
    )
    
    invoice_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="رقم الفاتورة"
    )
    invoice_date = models.DateField(
        auto_now_add=True,
        verbose_name="تاريخ الفاتورة"
    )
    due_date = models.DateField(
        verbose_name="تاريخ الاستحقاق"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="حالة الفاتورة"
    )
    
    # المبالغ
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="المبلغ الفرعي"
    )
    vat_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="ضريبة القيمة المضافة"
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="المبلغ الإجمالي"
    )
    
    # معلومات الدفع
    payment_method = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="طريقة الدفع"
    )
    payment_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاريخ الدفع"
    )
    payment_reference = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="مرجع الدفع"
    )
    
    # PDF
    pdf_file = models.FileField(
        upload_to='invoices/',
        blank=True,
        null=True,
        verbose_name="ملف PDF"
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name="ملاحظات"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الإنشاء"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخر تحديث"
    )
    
    class Meta:
        verbose_name = "فاتورة اشتراك"
        verbose_name_plural = "فواتير الاشتراكات"
        ordering = ['-invoice_date']
        indexes = [
            models.Index(fields=['invoice_number']),
            models.Index(fields=['status', 'due_date']),
            models.Index(fields=['subscription']),
        ]
    
    def __str__(self):
        return f"فاتورة #{self.invoice_number} - {self.subscription.client.name}"