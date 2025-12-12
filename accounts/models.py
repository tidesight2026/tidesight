from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    نموذج المستخدم المخصص - يمتد من AbstractUser
    يحتوي على حقول إضافية للدور والتفاصيل الشخصية
    """
    ROLE_CHOICES = [
        ('owner', 'مالك'),
        ('manager', 'مدير'),
        ('accountant', 'محاسب'),
        ('worker', 'عامل'),
        ('viewer', 'مشاهد'),
    ]
    
    full_name = models.CharField(
        max_length=255,
        verbose_name="الاسم الكامل",
        help_text="الاسم الكامل للمستخدم"
    )
    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="الهاتف",
        help_text="رقم الهاتف (اختياري)"
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='worker',
        verbose_name="الدور",
        help_text="دور المستخدم في النظام"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="نشط",
        help_text="هل المستخدم نشط؟ (Soft Delete)"
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
        verbose_name = "مستخدم"
        verbose_name_plural = "المستخدمون"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.full_name} ({self.username})"
    
    def get_full_name(self):
        """إرجاع الاسم الكامل"""
        return self.full_name or self.username
    
    def is_owner(self):
        """التحقق من أن المستخدم هو مالك"""
        return self.role == 'owner'
    
    def is_manager(self):
        """التحقق من أن المستخدم مدير"""
        return self.role in ['owner', 'manager']
    
    def can_edit_financial(self):
        """التحقق من صلاحية التعديل على البيانات المالية"""
        return self.role in ['owner', 'manager', 'accountant']

