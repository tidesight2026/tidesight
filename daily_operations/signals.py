"""
Django Signals للعمليات اليومية
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum
from .models import FeedingLog, MortalityLog


@receiver(post_save, sender=MortalityLog)
@receiver(post_delete, sender=MortalityLog)
def update_batch_mortality(sender, instance, **kwargs):
    """
    تحديث العدد الحالي للدفعة عند إضافة أو حذف سجل نفوق
    """
    batch = instance.batch
    
    # حساب إجمالي النفوق من جميع السجلات
    total_mortality = MortalityLog.objects.filter(batch=batch).aggregate(
        total=Sum('count')
    )['total'] or 0
    
    # تحديث العدد الحالي
    new_count = max(0, batch.initial_count - total_mortality)
    if batch.current_count != new_count:
        batch.current_count = new_count
        batch.save(update_fields=['current_count'])


@receiver(post_save, sender=FeedingLog)
def update_feed_inventory(sender, instance, created, **kwargs):
    """
    خصم العلف من المخزون عند تسجيل تغذية
    TODO: سيتم تطبيقه في Sprint 4 عند ربطه بالمحاسبة
    """
    # سيتم تطبيقه لاحقاً عند إضافة خوارزمية خصم من المخزون
    pass

