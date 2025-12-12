"""
نماذج البيانات البيولوجية - الأنواع السمكية والأحواض والدفعات
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class LifecycleStage(models.Model):
    """
    نموذج مراحل النمو (Lifecycle Stages)
    """
    name = models.CharField(max_length=100, verbose_name="اسم المرحلة")
    arabic_name = models.CharField(max_length=100, verbose_name="الاسم العربي")
    description = models.TextField(null=True, blank=True, verbose_name="الوصف")
    min_days = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="الحد الأدنى للأيام",
        help_text="الحد الأدنى للأيام لهذه المرحلة"
    )
    max_days = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="الحد الأقصى للأيام",
        help_text="الحد الأقصى للأيام لهذه المرحلة"
    )
    order = models.IntegerField(default=0, verbose_name="ترتيب المرحلة")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    
    class Meta:
        verbose_name = "مرحلة نمو"
        verbose_name_plural = "مراحل النمو"
        ordering = ['order', 'name']
    
    def __str__(self):
        return f"{self.arabic_name} ({self.name})"


class Species(models.Model):
    """
    نموذج الأنواع السمكية (Species)
    """
    name = models.CharField(max_length=200, verbose_name="الاسم العلمي")
    arabic_name = models.CharField(max_length=200, verbose_name="الاسم العربي")
    scientific_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="الاسم اللاتيني"
    )
    description = models.TextField(null=True, blank=True, verbose_name="الوصف")
    lifecycle_stages = models.ManyToManyField(
        LifecycleStage,
        blank=True,
        related_name='species',
        verbose_name="مراحل النمو",
        help_text="مراحل النمو لهذا النوع"
    )
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    
    class Meta:
        verbose_name = "نوع سمكي"
        verbose_name_plural = "الأنواع السمكية"
        ordering = ['arabic_name']
    
    def __str__(self):
        return f"{self.arabic_name} ({self.name})"


class FarmLocation(models.Model):
    """
    نموذج موقع المزرعة (Farm Location) - للمناطق والأقسام
    """
    name = models.CharField(max_length=200, verbose_name="اسم الموقع")
    arabic_name = models.CharField(max_length=200, verbose_name="الاسم العربي")
    description = models.TextField(null=True, blank=True, verbose_name="الوصف")
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="الموقع الأب",
        help_text="الموقع الأكبر (مثل: المبنى الرئيسي)"
    )
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    
    class Meta:
        verbose_name = "موقع المزرعة"
        verbose_name_plural = "مواقع المزرعة"
        ordering = ['arabic_name']
    
    def __str__(self):
        return self.arabic_name or self.name


class Pond(models.Model):
    """
    نموذج الحوض (Pond/Tank)
    """
    POND_TYPES = [
        ('concrete', 'خرسانة'),
        ('earth', 'ترابي'),
        ('fiberglass', 'فيبرجلاس'),
        ('cage', 'قفص'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'نشط'),
        ('maintenance', 'صيانة'),
        ('empty', 'فارغ'),
        ('inactive', 'غير نشط'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="اسم الحوض")
    pond_type = models.CharField(
        max_length=20,
        choices=POND_TYPES,
        default='concrete',
        verbose_name="نوع الحوض"
    )
    capacity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="السعة (م³)",
        help_text="سعة الحوض بالمتر المكعب"
    )
    location = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="الموقع",
        help_text="موقع الحوض في المزرعة"
    )
    farm_location = models.ForeignKey(
        FarmLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ponds',
        verbose_name="موقع المزرعة",
        help_text="الموقع الرسمي في المزرعة"
    )
    coordinates_x = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="إحداثي X",
        help_text="للاستخدام في الخريطة"
    )
    coordinates_y = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="إحداثي Y",
        help_text="للاستخدام في الخريطة"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='empty',
        verbose_name="الحالة"
    )
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    
    class Meta:
        verbose_name = "حوض"
        verbose_name_plural = "الأحواض"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_pond_type_display()})"


class Batch(models.Model):
    """
    نموذج الدفعة (Batch) - مجموعة من الأسماك
    """
    STATUS_CHOICES = [
        ('active', 'نشط'),
        ('harvested', 'محصود'),
        ('terminated', 'منتهي'),
    ]
    
    pond = models.ForeignKey(
        Pond,
        on_delete=models.PROTECT,
        related_name='batches',
        verbose_name="الحوض"
    )
    species = models.ForeignKey(
        Species,
        on_delete=models.PROTECT,
        related_name='batches',
        verbose_name="النوع السمكي"
    )
    batch_number = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="رقم الدفعة",
        help_text="رقم فريد للدفعة"
    )
    start_date = models.DateField(verbose_name="تاريخ البدء")
    initial_count = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="العدد الأولي",
        help_text="عدد الأسماك عند البدء"
    )
    initial_weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="الوزن الأولي (كجم)",
        help_text="الوزن الإجمالي الأولي بالكيلوجرام"
    )
    initial_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00'),
        verbose_name="التكلفة الأولية",
        help_text="التكلفة الأولية للزريعة"
    )
    current_count = models.IntegerField(
        default=0,
        verbose_name="العدد الحالي",
        help_text="العدد الحالي الحي"
    )
    current_weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00'),
        verbose_name="الوزن الحالي (كجم)",
        help_text="الوزن الإجمالي الحالي بالكيلوجرام"
    )
    lifecycle_stage = models.ForeignKey(
        LifecycleStage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='batches',
        verbose_name="مرحلة النمو الحالية",
        help_text="المرحلة الحالية للنمو"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name="الحالة"
    )
    notes = models.TextField(null=True, blank=True, verbose_name="ملاحظات")
    is_active = models.BooleanField(
        default=True,
        verbose_name="نشط",
        help_text="Soft Delete - هل الدفعة نشطة؟"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    
    class Meta:
        verbose_name = "دفعة"
        verbose_name_plural = "الدفعات"
        ordering = ['-start_date', '-created_at']
        indexes = [
            models.Index(fields=['batch_number']),
            models.Index(fields=['status']),
            models.Index(fields=['pond']),
        ]
    
    def __str__(self):
        return f"{self.batch_number} - {self.species.arabic_name} ({self.pond.name})"
    
    def save(self, *args, **kwargs):
        # عند الإنشاء، نضع current_count = initial_count و current_weight = initial_weight
        if not self.pk:
            self.current_count = self.initial_count
            if not self.current_weight or self.current_weight == 0:
                self.current_weight = self.initial_weight
        super().save(*args, **kwargs)
    
    @property
    def average_weight(self):
        """حساب متوسط وزن السمكة الواحدة"""
        if self.current_count > 0 and self.current_weight > 0:
            return self.current_weight / self.current_count
        return Decimal('0.00')
    
    @property
    def estimated_biomass(self):
        """تقدير الكتلة الحيوية"""
        return self.current_weight
    
    @property
    def mortality_count(self):
        """عدد النفوق"""
        return self.initial_count - self.current_count
    
    @property
    def mortality_rate(self):
        """معدل النفوق كنسبة مئوية"""
        if self.initial_count > 0:
            return ((self.initial_count - self.current_count) / self.initial_count) * 100
        return Decimal('0.00')
    
    @property
    def fcr(self):
        """حساب معامل تحويل العلف (FCR)"""
        from daily_operations.utils import calculate_fcr
        return calculate_fcr(self)
    
    @property
    def weight_gain(self):
        """حساب زيادة الوزن الإجمالية"""
        from daily_operations.utils import calculate_weight_gain
        return calculate_weight_gain(self)
    
    @property
    def weight_gain_rate_daily(self):
        """حساب معدل النمو اليومي"""
        from daily_operations.utils import calculate_weight_gain_rate
        return calculate_weight_gain_rate(self, period='daily')
    
    @property
    def weight_gain_rate_weekly(self):
        """حساب معدل النمو الأسبوعي"""
        from daily_operations.utils import calculate_weight_gain_rate
        return calculate_weight_gain_rate(self, period='weekly')
    
    @property
    def weight_gain_rate_monthly(self):
        """حساب معدل النمو الشهري"""
        from daily_operations.utils import calculate_weight_gain_rate
        return calculate_weight_gain_rate(self, period='monthly')
    
    def get_statistics(self):
        """الحصول على إحصائيات شاملة للدفعة"""
        from daily_operations.utils import get_batch_statistics
        return get_batch_statistics(self)


class SensorReading(models.Model):
    """
    نموذج قراءات المستشعرات (Sensor Readings) - للتحضير لتكامل IoT
    
    يحفظ قراءات من مستشعرات IoT مثل:
    - درجة الحرارة
    - الأكسجين المذاب
    - درجة الحموضة (pH)
    - وغيرها
    """
    SENSOR_TYPES = [
        ('temperature', 'درجة الحرارة'),
        ('oxygen', 'الأكسجين المذاب'),
        ('ph', 'درجة الحموضة (pH)'),
        ('ammonia', 'الأمونيا'),
        ('nitrite', 'النتريت'),
        ('nitrate', 'النتريت'),
        ('turbidity', 'العكارة'),
        ('salinity', 'الملوحة'),
        ('other', 'أخرى'),
    ]
    
    pond = models.ForeignKey(
        Pond,
        on_delete=models.CASCADE,
        related_name='sensor_readings',
        verbose_name="الحوض",
        help_text="الحوض الذي تم أخذ القراءة منه"
    )
    sensor_type = models.CharField(
        max_length=20,
        choices=SENSOR_TYPES,
        verbose_name="نوع المستشعر"
    )
    reading_value = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        verbose_name="قيمة القراءة",
        help_text="قيمة القراءة من المستشعر"
    )
    unit = models.CharField(
        max_length=20,
        default='',
        verbose_name="الوحدة",
        help_text="وحدة القياس (مثل: °C، mg/L، إلخ)"
    )
    reading_date = models.DateTimeField(
        verbose_name="تاريخ ووقت القراءة",
        help_text="تاريخ ووقت أخذ القراءة"
    )
    is_alert = models.BooleanField(
        default=False,
        verbose_name="تنبيه",
        help_text="هل هذه القراءة تتطلب تنبيه؟ (خارج النطاق الطبيعي)"
    )
    alert_message = models.TextField(
        null=True,
        blank=True,
        verbose_name="رسالة التنبيه",
        help_text="رسالة التنبيه إذا كانت القراءة خارج النطاق الطبيعي"
    )
    sensor_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="معرف المستشعر",
        help_text="معرف المستشعر في نظام IoT"
    )
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name="ملاحظات"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    
    class Meta:
        verbose_name = "قراءة مستشعر"
        verbose_name_plural = "قراءات المستشعرات"
        ordering = ['-reading_date', '-created_at']
        indexes = [
            models.Index(fields=['pond', 'sensor_type', 'reading_date']),
            models.Index(fields=['reading_date']),
            models.Index(fields=['sensor_type']),
            models.Index(fields=['is_alert']),
        ]
    
    def __str__(self):
        return f"{self.get_sensor_type_display()} - {self.reading_value} {self.unit} - {self.pond.name} - {self.reading_date}"
