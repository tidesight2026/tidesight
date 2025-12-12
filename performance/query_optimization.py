"""
Query Optimization Utilities
أدوات لتحسين استعلامات قاعدة البيانات
"""
from django.db import models
from django.db.models import Prefetch, Q, F, Count, Sum, Avg, Max, Min
from django.db.models.functions import Coalesce


def optimize_queryset(queryset, select_related=None, prefetch_related=None):
    """
    تحسين QuerySet باستخدام select_related و prefetch_related
    
    Args:
        queryset: QuerySet للتحسين
        select_related: قائمة ForeignKeys لـ select_related
        prefetch_related: قائمة ManyToMany أو reverse ForeignKeys لـ prefetch_related
    
    Returns:
        QuerySet محسّن
    """
    if select_related:
        queryset = queryset.select_related(*select_related)
    
    if prefetch_related:
        queryset = queryset.prefetch_related(*prefetch_related)
    
    return queryset


def get_batches_with_stats():
    """
    جلب الدفعات مع الإحصائيات باستخدام annotate لتقليل عدد الاستعلامات
    
    Returns:
        QuerySet محسّن للدفعات مع الإحصائيات
    """
    from biological.models import Batch
    from daily_operations.models import FeedingLog, MortalityLog
    
    queryset = Batch.objects.select_related(
        'pond',
        'species'
    ).prefetch_related(
        Prefetch(
            'feeding_logs',
            queryset=FeedingLog.objects.select_related('feed_type')
        ),
        Prefetch(
            'mortality_logs',
            queryset=MortalityLog.objects.all()
        )
    ).annotate(
        total_feed_consumed=Coalesce(
            Sum('feeding_logs__quantity'),
            models.Value(0)
        ),
        total_feed_cost=Coalesce(
            Sum('feeding_logs__total_cost'),
            models.Value(0)
        ),
        total_mortality=Coalesce(
            Sum('mortality_logs__count'),
            models.Value(0)
        ),
        feeding_days=Count('feeding_logs', distinct=True)
    )
    
    return queryset


def get_accounts_with_balance():
    """
    جلب الحسابات مع الرصيد باستخدام annotate
    
    Returns:
        QuerySet محسّن للحسابات مع الرصيد
    """
    from accounting.models import Account, JournalEntryLine
    
    queryset = Account.objects.annotate(
        total_debit=Coalesce(
            Sum(
                'journal_entry_lines__amount',
                filter=Q(journal_entry_lines__type='debit',
                        journal_entry_lines__journal_entry__is_posted=True)
            ),
            models.Value(0)
        ),
        total_credit=Coalesce(
            Sum(
                'journal_entry_lines__amount',
                filter=Q(journal_entry_lines__type='credit',
                        journal_entry_lines__journal_entry__is_posted=True)
            ),
            models.Value(0)
        )
    )
    
    return queryset


def paginate_queryset(queryset, page=1, page_size=20):
    """
    Pagination للـ QuerySet
    
    Args:
        queryset: QuerySet للتنقيح
        page: رقم الصفحة (يبدأ من 1)
        page_size: عدد العناصر في الصفحة
    
    Returns:
        dict يحتوي على:
        - items: العناصر في الصفحة
        - total: إجمالي عدد العناصر
        - page: رقم الصفحة الحالية
        - page_size: حجم الصفحة
        - total_pages: إجمالي عدد الصفحات
        - has_next: هل هناك صفحة تالية
        - has_previous: هل هناك صفحة سابقة
    """
    total = queryset.count()
    total_pages = (total + page_size - 1) // page_size  # Ceiling division
    
    offset = (page - 1) * page_size
    items = queryset[offset:offset + page_size]
    
    return {
        'items': list(items),
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': total_pages,
        'has_next': page < total_pages,
        'has_previous': page > 1,
    }

