"""
نماذج المخزون - الأعلاف والأدوية
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class FeedType(models.Model):
    """
    نموذج نوع العلف (Feed Type)
    """
    name = models.CharField(max_length=200, verbose_name="اسم العلف")
    arabic_name = models.CharField(max_length=200, verbose_name="الاسم العربي")
    protein_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        null=True,
        blank=True,
        verbose_name="نسبة البروتين (%)"
    )
    description = models.TextField(null=True, blank=True, verbose_name="الوصف")
    unit = models.CharField(
        max_length=20,
        default='كجم',
        verbose_name="الوحدة",
        help_text="وحدة القياس (كجم، طن، إلخ)"
    )
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    
    class Meta:
        verbose_name = "نوع علف"
        verbose_name_plural = "أنواع الأعلاف"
        ordering = ['arabic_name']
    
    def __str__(self):
        return f"{self.arabic_name} ({self.name})"


class FeedInventory(models.Model):
    """
    نموذج مخزون العلف (Feed Inventory)
    """
    feed_type = models.ForeignKey(
        FeedType,
        on_delete=models.PROTECT,
        related_name='inventory_items',
        verbose_name="نوع العلف"
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="الكمية",
        help_text="الكمية المتوفرة"
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00'),
        verbose_name="سعر الوحدة",
        help_text="سعر الوحدة الواحدة"
    )
    expiry_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="تاريخ انتهاء الصلاحية"
    )
    location = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="الموقع",
        help_text="موقع التخزين"
    )
    notes = models.TextField(null=True, blank=True, verbose_name="ملاحظات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    
    class Meta:
        verbose_name = "مخزون علف"
        verbose_name_plural = "مخزون الأعلاف"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['feed_type']),
        ]
    
    def __str__(self):
        return f"{self.feed_type.arabic_name} - {self.quantity} {self.feed_type.unit}"


class Medicine(models.Model):
    """
    نموذج الدواء (Medicine)
    """
    name = models.CharField(max_length=200, verbose_name="اسم الدواء")
    arabic_name = models.CharField(max_length=200, verbose_name="الاسم العربي")
    active_ingredient = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="المادة الفعالة"
    )
    description = models.TextField(null=True, blank=True, verbose_name="الوصف")
    unit = models.CharField(
        max_length=20,
        default='وحدة',
        verbose_name="الوحدة"
    )
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    
    class Meta:
        verbose_name = "دواء"
        verbose_name_plural = "الأدوية"
        ordering = ['arabic_name']
    
    def __str__(self):
        return f"{self.arabic_name} ({self.name})"


class MedicineInventory(models.Model):
    """
    نموذج مخزون الأدوية (Medicine Inventory)
    """
    medicine = models.ForeignKey(
        Medicine,
        on_delete=models.PROTECT,
        related_name='inventory_items',
        verbose_name="الدواء"
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="الكمية"
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00'),
        verbose_name="سعر الوحدة"
    )
    expiry_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="تاريخ انتهاء الصلاحية"
    )
    location = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="الموقع"
    )
    notes = models.TextField(null=True, blank=True, verbose_name="ملاحظات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    
    class Meta:
        verbose_name = "مخزون دواء"
        verbose_name_plural = "مخزون الأدوية"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.medicine.arabic_name} - {self.quantity} {self.medicine.unit}"
