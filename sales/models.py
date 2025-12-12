"""
نماذج المبيعات والحصاد
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from biological.models import Batch


class Harvest(models.Model):
    """
    نموذج الحصاد (Harvest) - تحويل الأصل البيولوجي إلى منتج تام
    """
    STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('in_progress', 'قيد التنفيذ'),
        ('completed', 'مكتمل'),
        ('cancelled', 'ملغي'),
    ]
    
    batch = models.ForeignKey(
        Batch,
        on_delete=models.PROTECT,
        related_name='harvests',
        verbose_name="الدفعة"
    )
    harvest_date = models.DateField(verbose_name="تاريخ الحصاد")
    quantity_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="الكمية (كجم)",
        help_text="كمية السمك المحصود بالكيلوجرام"
    )
    count = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="العدد",
        help_text="عدد الأسماك المحصودة"
    )
    average_weight = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        verbose_name="متوسط الوزن (كجم)"
    )
    fair_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="القيمة العادلة",
        help_text="القيمة العادلة للسمك المحصود"
    )
    cost_per_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00'),
        verbose_name="التكلفة لكل كيلوجرام",
        help_text="التكلفة التراكمية لكل كيلوجرام"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="الحالة"
    )
    notes = models.TextField(null=True, blank=True, verbose_name="ملاحظات")
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='harvests',
        verbose_name="المسجل"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    
    class Meta:
        verbose_name = "حصاد"
        verbose_name_plural = "الحصاد"
        ordering = ['-harvest_date', '-created_at']
        indexes = [
            models.Index(fields=['batch', 'harvest_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"حصاد {self.batch.batch_number} - {self.harvest_date} - {self.quantity_kg} كجم"
    
    def save(self, *args, **kwargs):
        # حساب متوسط الوزن تلقائياً
        if self.quantity_kg > 0 and self.count > 0 and not self.average_weight:
            self.average_weight = self.quantity_kg / self.count
        super().save(*args, **kwargs)


class SalesOrder(models.Model):
    """
    نموذج طلب البيع (Sales Order)
    """
    STATUS_CHOICES = [
        ('draft', 'مسودة'),
        ('confirmed', 'مؤكد'),
        ('invoiced', 'مفوتر'),
        ('delivered', 'تم التسليم'),
        ('cancelled', 'ملغي'),
    ]
    
    order_number = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="رقم الطلب",
        help_text="رقم فريد لطلب البيع"
    )
    order_date = models.DateField(verbose_name="تاريخ الطلب")
    customer_name = models.CharField(max_length=200, verbose_name="اسم العميل")
    customer_phone = models.CharField(max_length=20, null=True, blank=True, verbose_name="هاتف العميل")
    customer_address = models.TextField(null=True, blank=True, verbose_name="عنوان العميل")
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="المجموع الفرعي"
    )
    vat_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('15.00'),
        verbose_name="معدل الضريبة (%)",
        help_text="معدل ضريبة القيمة المضافة"
    )
    vat_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="مبلغ الضريبة"
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="المبلغ الإجمالي"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="الحالة"
    )
    notes = models.TextField(null=True, blank=True, verbose_name="ملاحظات")
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='sales_orders',
        verbose_name="المسجل"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    
    class Meta:
        verbose_name = "طلب بيع"
        verbose_name_plural = "طلبات البيع"
        ordering = ['-order_date', '-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.order_number} - {self.customer_name}"
    
    def save(self, *args, **kwargs):
        # حساب الضريبة والإجمالي تلقائياً
        if self.subtotal and self.vat_rate:
            self.vat_amount = (self.subtotal * self.vat_rate) / 100
            self.total_amount = self.subtotal + self.vat_amount
        super().save(*args, **kwargs)


class SalesOrderLine(models.Model):
    """
    نموذج بند طلب البيع (Sales Order Line)
    """
    sales_order = models.ForeignKey(
        SalesOrder,
        on_delete=models.CASCADE,
        related_name='lines',
        verbose_name="طلب البيع"
    )
    harvest = models.ForeignKey(
        Harvest,
        on_delete=models.PROTECT,
        related_name='sales_order_lines',
        verbose_name="الحصاد",
        help_text="السمك المباع من هذا الحصاد"
    )
    quantity_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="الكمية (كجم)"
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="سعر الكيلوجرام"
    )
    line_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="المجموع"
    )
    
    class Meta:
        verbose_name = "بند طلب بيع"
        verbose_name_plural = "بنود طلبات البيع"
        ordering = ['sales_order', 'id']
    
    def __str__(self):
        return f"{self.sales_order.order_number} - {self.quantity_kg} كجم"
    
    def save(self, *args, **kwargs):
        # حساب المجموع تلقائياً
        if self.quantity_kg and self.unit_price:
            self.line_total = self.quantity_kg * self.unit_price
        super().save(*args, **kwargs)


class Invoice(models.Model):
    """
    نموذج الفاتورة (Invoice)
    """
    STATUS_CHOICES = [
        ('draft', 'مسودة'),
        ('issued', 'مصدرة'),
        ('paid', 'مدفوعة'),
        ('cancelled', 'ملغاة'),
    ]
    
    invoice_number = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="رقم الفاتورة",
        help_text="رقم الفاتورة الضريبية"
    )
    sales_order = models.OneToOneField(
        SalesOrder,
        on_delete=models.PROTECT,
        related_name='invoice',
        verbose_name="طلب البيع"
    )
    invoice_date = models.DateField(verbose_name="تاريخ الفاتورة")
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="المجموع الفرعي"
    )
    vat_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="مبلغ الضريبة"
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="المبلغ الإجمالي"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="الحالة"
    )
    # ZATCA Fields
    qr_code = models.TextField(null=True, blank=True, verbose_name="QR Code")
    uuid = models.CharField(max_length=100, null=True, blank=True, verbose_name="UUID")
    signed_xml = models.TextField(null=True, blank=True, verbose_name="XML الموقع")
    zatca_status = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="حالة ZATCA",
        help_text="حالة إرسال الفاتورة إلى ZATCA"
    )
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='invoices',
        verbose_name="المسجل"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    
    class Meta:
        verbose_name = "فاتورة"
        verbose_name_plural = "الفواتير"
        ordering = ['-invoice_date', '-created_at']
        indexes = [
            models.Index(fields=['invoice_number']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.invoice_number} - {self.total_amount} ريال"
