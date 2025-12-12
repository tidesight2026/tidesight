"""
Audit Logging Models
تسجيل جميع العمليات الحساسة في النظام
"""
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.translation import gettext_lazy as _


class AuditLog(models.Model):
    """
    نموذج سجل التدقيق (Audit Log)
    لتسجيل جميع العمليات الحساسة في النظام
    """
    ACTION_TYPES = [
        ('create', 'إنشاء'),
        ('update', 'تعديل'),
        ('delete', 'حذف'),
        ('view', 'عرض'),
        ('export', 'تصدير'),
        ('login', 'تسجيل دخول'),
        ('logout', 'تسجيل خروج'),
        ('approve', 'موافقة'),
        ('reject', 'رفض'),
        ('post', 'ترحيل'),
        ('cancel', 'إلغاء'),
    ]
    
    ENTITY_TYPES = [
        ('account', 'حساب'),
        ('journal_entry', 'قيد محاسبي'),
        ('harvest', 'حصاد'),
        ('sales_order', 'طلب بيع'),
        ('invoice', 'فاتورة'),
        ('feeding_log', 'سجل تغذية'),
        ('mortality_log', 'سجل نفوق'),
        ('batch', 'دفعة'),
        ('pond', 'حوض'),
        ('species', 'نوع سمكي'),
        ('user', 'مستخدم'),
        ('settings', 'إعدادات'),
    ]
    
    # معلومات العملية
    action_type = models.CharField(
        max_length=20,
        choices=ACTION_TYPES,
        verbose_name="نوع العملية"
    )
    entity_type = models.CharField(
        max_length=50,
        choices=ENTITY_TYPES,
        verbose_name="نوع الكيان"
    )
    entity_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="معرف الكيان"
    )
    entity_description = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="وصف الكيان"
    )
    
    # معلومات المستخدم
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs',
        verbose_name="المستخدم"
    )
    user_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="عنوان IP"
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
        verbose_name="User Agent"
    )
    
    # تفاصيل التغيير
    old_values = models.JSONField(
        null=True,
        blank=True,
        verbose_name="القيم القديمة",
        help_text="القيم قبل التغيير (JSON)"
    )
    new_values = models.JSONField(
        null=True,
        blank=True,
        verbose_name="القيم الجديدة",
        help_text="القيم بعد التغيير (JSON)"
    )
    
    # معلومات إضافية
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="وصف العملية"
    )
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name="ملاحظات"
    )
    
    # الطابع الزمني
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ العملية"
    )
    
    class Meta:
        verbose_name = "سجل تدقيق"
        verbose_name_plural = "سجلات التدقيق"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['action_type']),
            models.Index(fields=['entity_type']),
            models.Index(fields=['entity_id']),
            models.Index(fields=['user']),
            models.Index(fields=['created_at']),
            models.Index(fields=['action_type', 'entity_type']),
        ]
    
    def __str__(self):
        return f"{self.get_action_type_display()} {self.get_entity_type_display()} - {self.user} - {self.created_at}"

