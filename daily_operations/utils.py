"""
Utilities للعمليات اليومية - حساب FCR والكتلة الحيوية
"""
from decimal import Decimal
from datetime import date, timedelta
from django.db.models import Sum, Avg
from .models import FeedingLog, MortalityLog


def calculate_fcr(batch):
    """
    حساب FCR (Feed Conversion Ratio) - معدل التحويل الغذائي
    
    FCR = إجمالي العلف المستهلك / (الوزن الحالي - الوزن الأولي)
    
    Returns:
        Decimal: قيمة FCR، أو None إذا لم يكن هناك بيانات كافية
    """
    total_feed = FeedingLog.objects.filter(batch=batch).aggregate(
        total=Sum('quantity')
    )['total'] or Decimal('0.00')
    
    if total_feed == 0:
        return None
    
    weight_gain = batch.current_weight - batch.initial_weight
    
    if weight_gain <= 0:
        return None
    
    fcr = total_feed / weight_gain
    return fcr


def calculate_weight_gain(batch):
    """
    حساب زيادة الوزن الإجمالية (Total Weight Gain)
    
    Returns:
        Decimal: زيادة الوزن بالكيلوجرام، أو Decimal('0.00') إذا لم يكن هناك زيادة
    """
    weight_gain = batch.current_weight - batch.initial_weight
    return max(Decimal('0.00'), weight_gain)


def calculate_weight_gain_rate(batch, period='daily'):
    """
    حساب معدل النمو (Weight Gain Rate)
    
    Args:
        batch: كائن Batch
        period: الفترة ('daily', 'weekly', 'monthly')
    
    Returns:
        Decimal: معدل النمو بالكيلوجرام لكل فترة، أو None إذا لم يكن هناك بيانات كافية
    """
    weight_gain = calculate_weight_gain(batch)
    
    if weight_gain <= 0:
        return None
    
    # حساب عدد الأيام
    days_active = (date.today() - batch.start_date).days
    
    if days_active <= 0:
        return None
    
    # حساب المعدل اليومي
    daily_rate = weight_gain / days_active
    
    # تحويل حسب الفترة المطلوبة
    if period == 'daily':
        return daily_rate
    elif period == 'weekly':
        return daily_rate * 7
    elif period == 'monthly':
        return daily_rate * 30
    else:
        return daily_rate


def calculate_average_daily_gain(batch):
    """
    حساب متوسط النمو اليومي (Average Daily Gain - ADG)
    
    ADG = (الوزن الحالي - الوزن الأولي) / عدد الأيام
    
    Returns:
        Decimal: متوسط النمو اليومي بالكيلوجرام/يوم، أو None إذا لم يكن هناك بيانات كافية
    """
    return calculate_weight_gain_rate(batch, period='daily')


def calculate_estimated_biomass(batch_id):
    """
    حساب الكتلة الحيوية المقدرة (Estimated Biomass)
    
    في هذا الإصدار البسيط، نستخدم الوزن الحالي المحدث.
    يمكن تحسينه لاحقاً باستخدام جداول النمو المعيارية.
    
    Args:
        batch_id: معرف الدفعة (int أو Batch object)
    
    Returns:
        Decimal: الكتلة الحيوية بالكيلوجرام
    """
    from biological.models import Batch
    
    if isinstance(batch_id, Batch):
        batch = batch_id
    else:
        try:
            batch = Batch.objects.get(id=batch_id)
        except Batch.DoesNotExist:
            return Decimal('0.00')
    
    return batch.current_weight


def calculate_total_feed_cost(batch):
    """
    حساب إجمالي تكلفة العلف للدفعة
    
    Returns:
        Decimal: إجمالي التكلفة
    """
    total = FeedingLog.objects.filter(batch=batch).aggregate(
        total=Sum('total_cost')
    )['total'] or Decimal('0.00')
    return total


def calculate_total_mortality(batch):
    """
    حساب إجمالي عدد النفوق للدفعة
    
    Returns:
        int: إجمالي عدد النفوق
    """
    total = MortalityLog.objects.filter(batch=batch).aggregate(
        total=Sum('count')
    )['total'] or 0
    return total


def get_batch_statistics(batch):
    """
    الحصول على إحصائيات شاملة للدفعة
    
    Returns:
        dict: إحصائيات الدفعة
    """
    total_feed = FeedingLog.objects.filter(batch=batch).aggregate(
        total=Sum('quantity')
    )['total'] or Decimal('0.00')
    
    total_feed_cost = calculate_total_feed_cost(batch)
    total_mortality = calculate_total_mortality(batch)
    fcr = calculate_fcr(batch)
    weight_gain = calculate_weight_gain(batch)
    weight_gain_rate_daily = calculate_weight_gain_rate(batch, period='daily')
    weight_gain_rate_weekly = calculate_weight_gain_rate(batch, period='weekly')
    weight_gain_rate_monthly = calculate_weight_gain_rate(batch, period='monthly')
    
    avg_daily_feed = Decimal('0.00')
    feeding_count = FeedingLog.objects.filter(batch=batch).count()
    days_active = (date.today() - batch.start_date).days
    if days_active > 0:
        avg_daily_feed = total_feed / days_active
    
    return {
        'total_feed_consumed': total_feed,
        'total_feed_cost': total_feed_cost,
        'total_mortality': total_mortality,
        'current_count': batch.current_count,
        'current_weight': batch.current_weight,
        'average_weight': batch.average_weight,
        'mortality_rate': batch.mortality_rate,
        'fcr': float(fcr) if fcr else None,
        'weight_gain': float(weight_gain),
        'weight_gain_rate_daily': float(weight_gain_rate_daily) if weight_gain_rate_daily else None,
        'weight_gain_rate_weekly': float(weight_gain_rate_weekly) if weight_gain_rate_weekly else None,
        'weight_gain_rate_monthly': float(weight_gain_rate_monthly) if weight_gain_rate_monthly else None,
        'avg_daily_feed': avg_daily_feed,
        'feeding_days': feeding_count,
        'days_active': days_active,
    }

