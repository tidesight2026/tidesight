"""
نماذج المحاسبة - Double Entry Bookkeeping
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class AccountType(models.TextChoices):
    """أنواع الحسابات الرئيسية"""
    ASSET = 'asset', 'أصول'
    LIABILITY = 'liability', 'خصوم'
    EQUITY = 'equity', 'حقوق ملكية'
    REVENUE = 'revenue', 'إيرادات'
    EXPENSE = 'expense', 'مصروفات'
    BIOLOGICAL_ASSET = 'biological_asset', 'أصول بيولوجية'


class Account(models.Model):
    """
    نموذج الحساب (Account) - دليل الحسابات
    """
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="رقم الحساب",
        help_text="رقم الحساب في دليل الحسابات"
    )
    name = models.CharField(max_length=200, verbose_name="اسم الحساب")
    arabic_name = models.CharField(max_length=200, verbose_name="الاسم العربي")
    account_type = models.CharField(
        max_length=20,
        choices=AccountType.choices,
        verbose_name="نوع الحساب"
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="الحساب الأب",
        help_text="الحساب الرئيسي (لإنشاء هيكلية شجرية)"
    )
    description = models.TextField(null=True, blank=True, verbose_name="الوصف")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    
    class Meta:
        verbose_name = "حساب"
        verbose_name_plural = "الحسابات"
        ordering = ['code']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['account_type']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.arabic_name}"
    
    @property
    def balance(self):
        """حساب رصيد الحساب"""
        from django.db.models import Sum, Q
        
        # حساب مجموع المدين
        total_debit = JournalEntryLine.objects.filter(
            account=self
        ).filter(
            type='debit'
        ).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        # حساب مجموع الدائن
        total_credit = JournalEntryLine.objects.filter(
            account=self
        ).filter(
            type='credit'
        ).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        # حساب الرصيد حسب نوع الحساب
        if self.account_type in ['asset', 'expense', 'biological_asset']:
            return total_debit - total_credit
        else:
            return total_credit - total_debit


class JournalEntry(models.Model):
    """
    نموذج القيد المحاسبي (Journal Entry) - Double Entry Bookkeeping
    """
    entry_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="رقم القيد"
    )
    entry_date = models.DateField(verbose_name="تاريخ القيد")
    description = models.TextField(verbose_name="وصف القيد")
    reference_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="نوع المرجع",
        help_text="مثل: feeding_log, mortality_log, harvest, sale"
    )
    reference_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="رقم المرجع",
        help_text="معرف المرجع في الجدول المصدري"
    )
    is_posted = models.BooleanField(
        default=False,
        verbose_name="مُسجل",
        help_text="هل تم تسجيل القيد نهائياً؟"
    )
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='journal_entries',
        verbose_name="المسجل"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    
    class Meta:
        verbose_name = "قيد محاسبي"
        verbose_name_plural = "القيود المحاسبية"
        ordering = ['-entry_date', '-created_at']
        indexes = [
            models.Index(fields=['entry_number']),
            models.Index(fields=['entry_date']),
            models.Index(fields=['reference_type', 'reference_id']),
        ]
    
    def __str__(self):
        return f"{self.entry_number} - {self.entry_date}"
    
    def validate_balance(self):
        """التحقق من توازن القيد (المدين = الدائن)"""
        from django.db.models import Sum
        total_debit = self.lines.filter(type='debit').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        total_credit = self.lines.filter(type='credit').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        return total_debit == total_credit
    
    def save(self, *args, **kwargs):
        """الحفظ مع التحقق من التوازن"""
        super().save(*args, **kwargs)
        
        # التحقق من التوازن بعد الحفظ
        if self.lines.exists():
            if not self.validate_balance():
                raise ValueError("القيد غير متوازن! يجب أن يكون مجموع المدين = مجموع الدائن")


class JournalEntryLine(models.Model):
    """
    نموذج بند القيد (Journal Entry Line)
    """
    TYPE_CHOICES = [
        ('debit', 'مدين'),
        ('credit', 'دائن'),
    ]
    
    journal_entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.CASCADE,
        related_name='lines',
        verbose_name="القيد المحاسبي"
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name='journal_entry_lines',
        verbose_name="الحساب"
    )
    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        verbose_name="نوع البند"
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="المبلغ"
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="وصف البند"
    )
    
    class Meta:
        verbose_name = "بند قيد"
        verbose_name_plural = "بنود القيود"
        ordering = ['journal_entry', 'type', 'id']
    
    def __str__(self):
        return f"{self.journal_entry.entry_number} - {self.account.code} - {self.get_type_display()} {self.amount}"


class BiologicalAssetRevaluation(models.Model):
    """
    نموذج إعادة تقييم الأصل البيولوجي حسب معيار IAS 41
    
    يتم تشغيله شهرياً لإعادة تقييم الأسماك بناءً على:
    - الوزن الحالي (من Batch)
    - سعر السوق الحالي
    - حساب القيمة العادلة (Fair Value)
    - تسجيل الربح/الخسارة غير المحققة
    """
    batch = models.ForeignKey(
        'biological.Batch',
        on_delete=models.CASCADE,
        related_name='revaluations',
        verbose_name="الدفعة"
    )
    revaluation_date = models.DateField(verbose_name="تاريخ إعادة التقييم")
    
    # القيمة الدفترية (Carrying Amount) قبل إعادة التقييم
    carrying_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="القيمة الدفترية",
        help_text="القيمة المسجلة في الحسابات قبل إعادة التقييم"
    )
    
    # القيمة العادلة (Fair Value) - الوزن × سعر السوق
    fair_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="القيمة العادلة",
        help_text="الوزن الحالي × سعر السوق"
    )
    
    # سعر السوق المستخدم
    market_price_per_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="سعر السوق (ريال/كجم)",
        help_text="سعر السوق الحالي للكيلوجرام"
    )
    
    # الوزن الحالي للدفعة
    current_weight_kg = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="الوزن الحالي (كجم)",
        help_text="الوزن التقديري الحالي للدفعة"
    )
    
    # عدد الأسماك الحالية
    current_count = models.IntegerField(
        verbose_name="العدد الحالي",
        help_text="عدد الأسماك الحالي في الدفعة"
    )
    
    # الفرق (الربح/الخسارة غير المحققة)
    unrealized_gain_loss = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="ربح/خسارة غير محققة",
        help_text="الفرق بين القيمة العادلة والقيمة الدفترية"
    )
    
    # القيد المحاسبي المرتبط
    journal_entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='biological_revaluations',
        verbose_name="القيد المحاسبي"
    )
    
    # ملاحظات
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name="ملاحظات"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="المُنشئ"
    )
    
    class Meta:
        verbose_name = "إعادة تقييم أصل بيولوجي"
        verbose_name_plural = "إعادة تقييم الأصول البيولوجية"
        ordering = ['-revaluation_date', '-created_at']
        indexes = [
            models.Index(fields=['batch', 'revaluation_date']),
            models.Index(fields=['revaluation_date']),
        ]
        unique_together = [['batch', 'revaluation_date']]  # تقييم واحد لكل دفعة في التاريخ
    
    def __str__(self):
        return f"إعادة تقييم {self.batch.batch_number} - {self.revaluation_date}"
    
    def save(self, *args, **kwargs):
        """حساب الربح/الخسارة غير المحققة تلقائياً"""
        self.unrealized_gain_loss = self.fair_value - self.carrying_amount
        super().save(*args, **kwargs)
