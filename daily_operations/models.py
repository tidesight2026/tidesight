"""
نماذج العمليات اليومية - تسجيل العلف والنفوق
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from biological.models import Batch
from inventory.models import FeedType


class FeedingLog(models.Model):
    """
    نموذج سجل التغذية (Feeding Log)
    """
    batch = models.ForeignKey(
        Batch,
        on_delete=models.PROTECT,
        related_name='feeding_logs',
        verbose_name="الدفعة"
    )
    feed_type = models.ForeignKey(
        FeedType,
        on_delete=models.PROTECT,
        related_name='feeding_logs',
        verbose_name="نوع العلف"
    )
    feeding_date = models.DateField(verbose_name="تاريخ التغذية")
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="الكمية (كجم)",
        help_text="كمية العلف بالكيلوجرام"
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00'),
        verbose_name="سعر الوحدة",
        help_text="سعر الكيلوجرام الواحد"
    )
    total_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00'),
        verbose_name="التكلفة الإجمالية",
        help_text="الكمية × سعر الوحدة"
    )
    notes = models.TextField(null=True, blank=True, verbose_name="ملاحظات")
    is_posted = models.BooleanField(
        default=False,
        verbose_name="مُسجل محاسبياً",
        help_text="هل تم إنشاء قيد محاسبي لهذا السجل؟"
    )
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='feeding_logs',
        verbose_name="المسجل"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    
    class Meta:
        verbose_name = "سجل تغذية"
        verbose_name_plural = "سجلات التغذية"
        ordering = ['-feeding_date', '-created_at']
        indexes = [
            models.Index(fields=['batch', 'feeding_date']),
            models.Index(fields=['feeding_date']),
        ]
    
    def __str__(self):
        return f"{self.batch.batch_number} - {self.feeding_date} - {self.quantity} كجم"
    
    def save(self, *args, **kwargs):
        # حساب التكلفة الإجمالية تلقائياً
        if self.quantity and self.unit_price:
            self.total_cost = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class MortalityLog(models.Model):
    """
    نموذج سجل النفوق (Mortality Log)
    """
    batch = models.ForeignKey(
        Batch,
        on_delete=models.PROTECT,
        related_name='mortality_logs',
        verbose_name="الدفعة"
    )
    mortality_date = models.DateField(verbose_name="تاريخ النفوق")
    count = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="عدد النفوق"
    )
    average_weight = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        null=True,
        blank=True,
        verbose_name="متوسط الوزن (كجم)",
        help_text="متوسط وزن السمكة النافقة"
    )
    cause = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="سبب النفوق",
        help_text="سبب النفوق (مرض، نقص أكسجين، إلخ)"
    )
    notes = models.TextField(null=True, blank=True, verbose_name="ملاحظات")
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='mortality_logs',
        verbose_name="المسجل"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    
    class Meta:
        verbose_name = "سجل نفوق"
        verbose_name_plural = "سجلات النفوق"
        ordering = ['-mortality_date', '-created_at']
        indexes = [
            models.Index(fields=['batch', 'mortality_date']),
            models.Index(fields=['mortality_date']),
        ]
    
    def __str__(self):
        return f"{self.batch.batch_number} - {self.mortality_date} - {self.count} سمكة"
