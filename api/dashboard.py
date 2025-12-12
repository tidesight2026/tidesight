"""
API Endpoints للوحة التحكم (Dashboard)
"""
from ninja import Router
from ninja.security import HttpBearer
from django.contrib.auth import get_user_model
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, timedelta
from decimal import Decimal
from django.core.cache import cache
from django.db.models import Sum, Avg, Count

User = get_user_model()
router = Router()

# Reuse the same TokenAuth from auth.py
from .auth import TokenAuth


class StatsResponse(BaseModel):
    """Response schema للإحصائيات"""
    total_ponds: int = 0
    active_batches: int = 0
    total_biomass: float = 0.0
    mortality_rate: float = 0.0
    total_feed_value: float = 0.0
    total_medicine_value: float = 0.0


@router.get('/stats', response=StatsResponse, auth=TokenAuth())
def get_dashboard_stats(request):
    """
    الحصول على إحصائيات لوحة التحكم
    
    **Authentication:** Bearer Token مطلوب
    **Performance:** محسّن باستخدام Cache (60 seconds)
    """
    # التحقق من authentication
    if not request.auth:
        from .auth import ErrorResponse
        return 401, ErrorResponse(detail="غير مصرح - يرجى تسجيل الدخول")
    
    # محاولة جلب من Cache
    cache_key = f'dashboard:stats:{request.auth.id if request.auth else "anonymous"}'
    cached_stats = cache.get(cache_key)
    
    if cached_stats is not None:
        return cached_stats
    
    # استيراد Models
    try:
        from biological.models import Pond, Batch
        
        # إجمالي الأحواض
        total_ponds = Pond.objects.filter(is_active=True).count()
        
        # الدفعات النشطة
        active_batches = Batch.objects.filter(status='active').count()
        
        # حساب الكمية الحي الإجمالية (من الدفعات النشطة)
        active_batches_list = Batch.objects.filter(status='active').select_related('species')
        total_biomass = sum(
            float(batch.initial_weight) * (batch.current_count / batch.initial_count if batch.initial_count > 0 else 1)
            for batch in active_batches_list
        )
        
        # حساب معدل النفوق الإجمالي
        total_initial = sum(batch.initial_count for batch in Batch.objects.filter(status='active'))
        total_current = sum(batch.current_count for batch in Batch.objects.filter(status='active'))
        if total_initial > 0:
            mortality_rate = ((total_initial - total_current) / total_initial) * 100
        else:
            mortality_rate = 0.0
        
        # حساب قيمة المخزون
        from inventory.models import FeedInventory, MedicineInventory
        total_feed_value = sum(
            float(item.quantity * item.unit_price) for item in FeedInventory.objects.all()
        )
        total_medicine_value = sum(
            float(item.quantity * item.unit_price) for item in MedicineInventory.objects.all()
        )
        
        response = StatsResponse(
            total_ponds=total_ponds,
            active_batches=active_batches,
            total_biomass=total_biomass,
            mortality_rate=mortality_rate,
            total_feed_value=total_feed_value,
            total_medicine_value=total_medicine_value,
        )
        
        # حفظ في Cache لمدة دقيقة واحدة
        cache.set(cache_key, response, timeout=60)
        
        return response
    except Exception as e:
        # في حالة عدم وجود Models بعد، نعيد قيم افتراضية
        response = StatsResponse(
            total_ponds=0,
            active_batches=0,
            total_biomass=0.0,
            mortality_rate=0.0,
            total_feed_value=0.0,
            total_medicine_value=0.0,
        )
        cache.set(cache_key, response, timeout=60)
        return response


@router.get('/health', response={200: dict})
def health_check(request):
    """
    فحص حالة النظام - Health Check Endpoint للـ DevOps
    
    يتحقق من:
    - إمكانية الاتصال بقاعدة البيانات
    - إمكانية الاتصال بـ Redis
    - حالة الخدمة العامة
    
    **Usage:** يمكن استخدامه في Kubernetes/Load Balancer health checks
    """
    from django.db import connection
    from django.core.cache import cache
    from django.conf import settings
    
    health_status = {
        'status': 'healthy',
        'service': 'AquaERP API',
        'version': '1.0.0',
        'checks': {
            'database': 'unknown',
            'cache': 'unknown',
        },
        'timestamp': None,
    }
    
    # التحقق من قاعدة البيانات
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        health_status['checks']['database'] = 'healthy'
    except Exception as e:
        health_status['checks']['database'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'degraded'
    
    # التحقق من Redis/Cache
    try:
        cache.set('health_check_test', 'ok', timeout=10)
        test_value = cache.get('health_check_test')
        if test_value == 'ok':
            health_status['checks']['cache'] = 'healthy'
        else:
            health_status['checks']['cache'] = 'unhealthy: cache test failed'
            health_status['status'] = 'degraded'
    except Exception as e:
        health_status['checks']['cache'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'degraded'
    
    # إضافة timestamp
    from django.utils import timezone
    health_status['timestamp'] = timezone.now().isoformat()
    
    # إذا كان هناك مشكلة في أي خدمة حرجة، نعيد 503
    if health_status['status'] == 'degraded' and health_status['checks']['database'] != 'healthy':
        return 503, health_status
    
    return health_status


# ==================== Farm Overview Schema ====================

class FarmOverviewResponse(BaseModel):
    """Response schema لمعلومات المزرعة العامة"""
    active_ponds: int = 0
    active_batches: int = 0
    total_biomass_kg: float = 0.0
    feed_consumption_week_kg: float = 0.0
    feed_consumption_month_kg: float = 0.0
    mortality_count_week: int = 0
    mortality_count_month: int = 0


@router.get('/farm-overview', response={200: FarmOverviewResponse, 500: dict}, auth=TokenAuth())
def get_farm_overview(request):
    """
    الحصول على معلومات المزرعة العامة
    
    يعيد:
    - عدد الأحواض النشطة
    - عدد الدفعات النشطة
    - إجمالي الكتلة الحية التقديرية
    - استهلاك العلف خلال الأسبوع الماضي
    - استهلاك العلف خلال الشهر الماضي
    - عدد النفوق خلال الأسبوع الماضي
    - عدد النفوق خلال الشهر الماضي
    
    **Authentication:** Bearer Token مطلوب
    **Performance:** محسّن باستخدام Cache (60 seconds)
    """
    if not request.auth:
        from .auth import ErrorResponse
        return 401, ErrorResponse(detail="غير مصرح - يرجى تسجيل الدخول")
    
    # محاولة جلب من Cache
    cache_key = f'dashboard:farm-overview:{request.auth.id if request.auth else "anonymous"}'
    cached_data = cache.get(cache_key)
    
    if cached_data is not None:
        return cached_data
    
    try:
        from biological.models import Pond, Batch
        from daily_operations.models import FeedingLog, MortalityLog
        
        # عدد الأحواض النشطة
        active_ponds = Pond.objects.filter(is_active=True, status='active').count()
        
        # عدد الدفعات النشطة
        active_batches = Batch.objects.filter(status='active', is_active=True).count()
        
        # إجمالي الكتلة الحية التقديرية (من الدفعات النشطة)
        active_batches_list = Batch.objects.filter(
            status='active', 
            is_active=True
        ).select_related('species', 'pond')
        
        total_biomass_kg = sum(
            float(batch.current_weight) for batch in active_batches_list
        )
        
        # حساب تواريخ الفترات
        today = date.today()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # استهلاك العلف خلال الأسبوع الماضي
        feed_consumption_week = FeedingLog.objects.filter(
            feeding_date__gte=week_ago,
            feeding_date__lte=today
        ).aggregate(total=Sum('quantity'))['total'] or Decimal('0.00')
        
        # استهلاك العلف خلال الشهر الماضي
        feed_consumption_month = FeedingLog.objects.filter(
            feeding_date__gte=month_ago,
            feeding_date__lte=today
        ).aggregate(total=Sum('quantity'))['total'] or Decimal('0.00')
        
        # عدد النفوق خلال الأسبوع الماضي
        mortality_count_week = MortalityLog.objects.filter(
            mortality_date__gte=week_ago,
            mortality_date__lte=today
        ).aggregate(total=Sum('count'))['total'] or 0
        
        # عدد النفوق خلال الشهر الماضي
        mortality_count_month = MortalityLog.objects.filter(
            mortality_date__gte=month_ago,
            mortality_date__lte=today
        ).aggregate(total=Sum('count'))['total'] or 0
        
        response = FarmOverviewResponse(
            active_ponds=active_ponds,
            active_batches=active_batches,
            total_biomass_kg=float(total_biomass_kg),
            feed_consumption_week_kg=float(feed_consumption_week),
            feed_consumption_month_kg=float(feed_consumption_month),
            mortality_count_week=mortality_count_week,
            mortality_count_month=mortality_count_month,
        )
        
        # حفظ في Cache لمدة دقيقة واحدة
        cache.set(cache_key, response, timeout=60)
        
        return response
    except Exception as e:
        return 500, {"detail": f"خطأ في استرجاع البيانات: {str(e)}"}


# ==================== Batch Performance Schema ====================

class BatchPerformanceItem(BaseModel):
    """معلومات أداء دفعة واحدة"""
    batch_id: int
    batch_number: str
    species_name: str
    pond_name: str
    fcr: Optional[float] = None
    average_weight_kg: float = 0.0
    mortality_rate: float = 0.0
    weight_gain_rate_daily: Optional[float] = None
    days_active: int = 0
    current_count: int = 0
    current_weight_kg: float = 0.0


class BatchPerformanceResponse(BaseModel):
    """Response schema لأداء الدفعات"""
    batches: List[BatchPerformanceItem]


@router.get('/batch-performance', response={200: BatchPerformanceResponse, 500: dict}, auth=TokenAuth())
def get_batch_performance(request):
    """
    الحصول على أداء جميع الدفعات النشطة
    
    يعيد لكل دفعة:
    - FCR (معامل تحويل العلف)
    - متوسط الوزن
    - نسبة النفوق
    - معدل النمو اليومي
    - عدد الأيام النشطة
    - العدد الحالي
    - الوزن الحالي
    
    **Authentication:** Bearer Token مطلوب
    **Performance:** محسّن باستخدام Cache (60 seconds)
    """
    if not request.auth:
        from .auth import ErrorResponse
        return 401, ErrorResponse(detail="غير مصرح - يرجى تسجيل الدخول")
    
    # محاولة جلب من Cache
    cache_key = f'dashboard:batch-performance:{request.auth.id if request.auth else "anonymous"}'
    cached_data = cache.get(cache_key)
    
    if cached_data is not None:
        return cached_data
    
    try:
        from biological.models import Batch
        from daily_operations.utils import calculate_fcr, calculate_weight_gain_rate
        
        # الحصول على جميع الدفعات النشطة
        batches = Batch.objects.filter(
            status='active',
            is_active=True
        ).select_related('species', 'pond').order_by('-start_date')
        
        batch_performance_list = []
        today = date.today()
        
        for batch in batches:
            # حساب FCR
            fcr = calculate_fcr(batch)
            
            # حساب معدل النمو اليومي
            weight_gain_rate_daily = calculate_weight_gain_rate(batch, period='daily')
            
            # حساب عدد الأيام النشطة
            days_active = (today - batch.start_date).days
            
            batch_performance_list.append(
                BatchPerformanceItem(
                    batch_id=batch.id,
                    batch_number=batch.batch_number,
                    species_name=batch.species.arabic_name,
                    pond_name=batch.pond.name,
                    fcr=float(fcr) if fcr else None,
                    average_weight_kg=float(batch.average_weight),
                    mortality_rate=float(batch.mortality_rate),
                    weight_gain_rate_daily=float(weight_gain_rate_daily) if weight_gain_rate_daily else None,
                    days_active=days_active,
                    current_count=batch.current_count,
                    current_weight_kg=float(batch.current_weight),
                )
            )
        
        response = BatchPerformanceResponse(batches=batch_performance_list)
        
        # حفظ في Cache لمدة دقيقة واحدة
        cache.set(cache_key, response, timeout=60)
        
        return response
    except Exception as e:
        return 500, {"detail": f"خطأ في استرجاع البيانات: {str(e)}"}

