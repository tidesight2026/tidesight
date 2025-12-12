"""
Celery Tasks لتطبيق Tenants (إدارة الاشتراكات)
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

from tenants.models import Subscription
from tenants.aqua_core.services.subscription_service import SubscriptionService

logger = logging.getLogger(__name__)


@shared_task(name='tenants.check_expired_subscriptions')
def check_expired_subscriptions():
    """
    التحقق من الاشتراكات المنتهية وتحديث حالتها تلقائياً
    
    **المنطق:**
    - الاشتراكات التي current_period_end < الآن وتكون في حالة 'active' → تصبح 'past_due'
    - الاشتراكات التي current_period_end < الآن بـ 7 أيام أو أكثر وتكون 'past_due' → تصبح 'suspended'
    
    **Returns:**
    - dict: إحصائيات العملية
    """
    start_time = timezone.now()
    now = timezone.now()
    
    logger.info("بدء التحقق من الاشتراكات المنتهية")
    
    # 1. العثور على الاشتراكات المنتهية (active)
    expired_active = Subscription.objects.filter(
        status='active',
        current_period_end__lt=now
    ).select_related('client', 'plan')
    
    past_due_count = 0
    for subscription in expired_active:
        SubscriptionService.mark_subscription_past_due(
            subscription,
            reason="انتهت فترة الاشتراك"
        )
        past_due_count += 1
    
    # 2. العثور على الاشتراكات المتأخرة لأكثر من 7 أيام
    seven_days_ago = now - timedelta(days=7)
    expired_past_due = Subscription.objects.filter(
        status='past_due',
        current_period_end__lt=seven_days_ago
    ).select_related('client', 'plan')
    
    suspended_count = 0
    for subscription in expired_past_due:
        SubscriptionService.suspend_subscription(
            subscription,
            reason="تأخر الدفع لأكثر من 7 أيام"
        )
        suspended_count += 1
    
    # 3. العثور على الاشتراكات التجريبية المنتهية
    expired_trials = Subscription.objects.filter(
        status='trial',
        trial_ends_at__lt=now
    ).select_related('client', 'plan')
    
    trial_expired_count = 0
    for subscription in expired_trials:
        # تحويل التجربة المنتهية إلى past_due إذا لم يتم الدفع
        SubscriptionService.mark_subscription_past_due(
            subscription,
            reason="انتهت فترة التجربة"
        )
        trial_expired_count += 1
    
    duration = (timezone.now() - start_time).total_seconds()
    
    total_processed = past_due_count + suspended_count + trial_expired_count
    
    logger.info(
        f"اكتمل التحقق من الاشتراكات: "
        f"{past_due_count} أصبحت متأخرة، "
        f"{suspended_count} تم تعليقها، "
        f"{trial_expired_count} انتهت تجربتها "
        f"خلال {duration:.2f} ثانية"
    )
    
    return {
        'past_due_count': past_due_count,
        'suspended_count': suspended_count,
        'trial_expired_count': trial_expired_count,
        'total_processed': total_processed,
        'duration_seconds': round(duration, 2),
        'status': 'success'
    }

