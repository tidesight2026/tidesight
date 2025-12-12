"""
API Endpoints للتقارير والأداء
"""
from ninja import Router
from ninja.security import HttpBearer
from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from datetime import date, timedelta

router = Router()

# Reuse the same TokenAuth from auth.py
from .auth import TokenAuth, ErrorResponse
from .permissions import require_feature


# ==================== Report Schemas ====================

class CostPerKgReportItem(BaseModel):
    """عنصر في تقرير Cost per Kg"""
    batch_id: int
    batch_number: str
    species_name: str
    total_feed_cost: float
    total_cost: float  # تكلفة العلف + التكلفة الأولية
    total_weight_kg: float
    cost_per_kg: float
    status: str


class BatchProfitabilityItem(BaseModel):
    """عنصر في تقرير Batch Profitability"""
    batch_id: int
    batch_number: str
    species_name: str
    pond_name: str
    initial_cost: float
    total_feed_cost: float
    total_medicine_cost: float
    total_cost: float
    total_revenue: float
    profit: float
    profit_margin: float  # نسبة الربح (%)
    status: str


class BiologicalFinancialReportItem(BaseModel):
    """عنصر في تقرير الأداء الحيوي والمالي"""
    batch_id: int
    batch_number: str
    species_name: str
    pond_name: str
    # البيانات الحيوية
    initial_count: int
    current_count: int
    initial_weight_kg: float
    current_weight_kg: float
    weight_gain_kg: float
    fcr: Optional[float]
    mortality_rate: float
    days_active: int
    # البيانات المالية
    initial_cost: float
    total_feed_cost: float
    total_biological_cost: float
    total_revenue: float
    profit: float
    profit_margin: float
    cost_per_kg: float
    revenue_per_kg: float
    # المؤشرات
    roi: float  # Return on Investment (%)
    status: str


class FeedEfficiencyItem(BaseModel):
    """عنصر في تقرير Feed Efficiency"""
    batch_id: int
    batch_number: str
    species_name: str
    total_feed_consumed_kg: float
    total_weight_gain_kg: float
    fcr: Optional[float]  # Feed Conversion Ratio
    avg_daily_feed_kg: float
    feeding_days: int


class MortalityAnalysisItem(BaseModel):
    """عنصر في تحليل النفوق"""
    batch_id: int
    batch_number: str
    species_name: str
    pond_name: str
    initial_count: int
    current_count: int
    total_mortality: int
    mortality_rate: float  # نسبة النفوق (%)
    avg_daily_mortality: float
    mortality_days: int
    status: str


# ==================== Cost per Kg Report ====================

@router.get('/cost-per-kg', response={200: List[CostPerKgReportItem]}, auth=TokenAuth())
@require_feature('reports')
def get_cost_per_kg_report(request, batch_id: Optional[int] = None):
    """
    تقرير تكلفة الكيلوجرام للدفعات
    
    **Parameters:**
    - batch_id (optional): تصفية حسب دفعة معينة
    
    **Returns:**
    - قائمة بالدفعات مع تكلفة الكيلوجرام
    """
    try:
        from biological.models import Batch
        from daily_operations.utils import calculate_total_feed_cost
        from daily_operations.models import FeedingLog
        
        queryset = Batch.objects.select_related('species', 'pond').all()
        if batch_id:
            queryset = queryset.filter(id=batch_id)
        
        results = []
        for batch in queryset:
            # حساب التكلفة الإجمالية
            total_feed_cost = calculate_total_feed_cost(batch)
            total_cost = float(batch.initial_cost) + float(total_feed_cost)
            
            # حساب الوزن الإجمالي
            total_weight_kg = float(batch.current_weight)
            
            # حساب تكلفة الكيلوجرام
            cost_per_kg = total_cost / total_weight_kg if total_weight_kg > 0 else 0.0
            
            results.append(CostPerKgReportItem(
                batch_id=batch.id,
                batch_number=batch.batch_number,
                species_name=batch.species.arabic_name,
                total_feed_cost=float(total_feed_cost),
                total_cost=total_cost,
                total_weight_kg=total_weight_kg,
                cost_per_kg=cost_per_kg,
                status=batch.status,
            ))
        
        return results
    except Exception as e:
        return 500, ErrorResponse(detail=f"خطأ في استرجاع التقرير: {str(e)}")


# ==================== Batch Profitability Report ====================

@router.get('/batch-profitability', response={200: List[BatchProfitabilityItem]}, auth=TokenAuth())
def get_batch_profitability_report(request, batch_id: Optional[int] = None):
    """
    تقرير ربحية الدفعات
    
    **Parameters:**
    - batch_id (optional): تصفية حسب دفعة معينة
    
    **Returns:**
    - قائمة بالدفعات مع بيانات الربحية
    """
    try:
        from biological.models import Batch
        from daily_operations.utils import calculate_total_feed_cost
        from daily_operations.models import FeedingLog
        from sales.models import Harvest, SalesOrderLine
        from django.db.models import Sum
        
        queryset = Batch.objects.select_related('species', 'pond').all()
        if batch_id:
            queryset = queryset.filter(id=batch_id)
        
        results = []
        for batch in queryset:
            # حساب التكاليف
            total_feed_cost = calculate_total_feed_cost(batch)
            total_medicine_cost = Decimal('0.00')  # يمكن إضافته لاحقاً
            total_cost = float(batch.initial_cost) + float(total_feed_cost) + float(total_medicine_cost)
            
            # حساب الإيرادات من المبيعات
            harvests = Harvest.objects.filter(batch=batch, status='completed')
            harvest_ids = [h.id for h in harvests]
            
            total_revenue = SalesOrderLine.objects.filter(
                harvest_id__in=harvest_ids
            ).aggregate(total=Sum('line_total'))['total'] or Decimal('0.00')
            total_revenue = float(total_revenue)
            
            # حساب الربح
            profit = total_revenue - total_cost
            profit_margin = (profit / total_revenue * 100) if total_revenue > 0 else 0.0
            
            results.append(BatchProfitabilityItem(
                batch_id=batch.id,
                batch_number=batch.batch_number,
                species_name=batch.species.arabic_name,
                pond_name=batch.pond.name,
                initial_cost=float(batch.initial_cost),
                total_feed_cost=float(total_feed_cost),
                total_medicine_cost=float(total_medicine_cost),
                total_cost=total_cost,
                total_revenue=total_revenue,
                profit=profit,
                profit_margin=profit_margin,
                status=batch.status,
            ))
        
        return results
    except Exception as e:
        return 500, ErrorResponse(detail=f"خطأ في استرجاع التقرير: {str(e)}")


# ==================== Biological-Financial Report ====================

@router.get('/biological-financial', response={200: List[BiologicalFinancialReportItem]}, auth=TokenAuth())
@require_feature('reports')
def get_biological_financial_report(request, batch_id: Optional[int] = None):
    """
    تقرير يربط بين الأداء الحيوي والمالي
    
    يجمع بين:
    - المؤشرات الحيوية (FCR، معدل النمو، النفوق)
    - المؤشرات المالية (التكلفة، الإيرادات، الربح)
    - مؤشرات الأداء (ROI، هامش الربح)
    
    **Parameters:**
    - batch_id (optional): تصفية حسب دفعة معينة
    
    **Returns:**
    - قائمة بالدفعات مع بيانات شاملة
    """
    try:
        from biological.models import Batch
        from daily_operations.utils import calculate_total_feed_cost, calculate_fcr, calculate_weight_gain
        from sales.models import Harvest, SalesOrderLine
        from django.db.models import Sum
        from datetime import date
        
        queryset = Batch.objects.select_related('species', 'pond').all()
        if batch_id:
            queryset = queryset.filter(id=batch_id)
        
        results = []
        today = date.today()
        
        for batch in queryset:
            # البيانات الحيوية
            weight_gain = calculate_weight_gain(batch)
            fcr = calculate_fcr(batch)
            days_active = (today - batch.start_date).days
            
            # البيانات المالية
            total_feed_cost = calculate_total_feed_cost(batch)
            total_biological_cost = float(batch.initial_cost) + float(total_feed_cost)
            
            # حساب الإيرادات
            harvests = Harvest.objects.filter(batch=batch, status='completed')
            harvest_ids = [h.id for h in harvests]
            
            total_revenue = SalesOrderLine.objects.filter(
                harvest_id__in=harvest_ids
            ).aggregate(total=Sum('line_total'))['total'] or Decimal('0.00')
            total_revenue = float(total_revenue)
            
            # حساب الربح والمؤشرات
            profit = total_revenue - total_biological_cost
            profit_margin = (profit / total_revenue * 100) if total_revenue > 0 else 0.0
            roi = (profit / total_biological_cost * 100) if total_biological_cost > 0 else 0.0
            
            # حساب التكلفة والإيرادات لكل كيلوجرام
            current_weight_kg = float(batch.current_weight)
            cost_per_kg = total_biological_cost / current_weight_kg if current_weight_kg > 0 else 0.0
            revenue_per_kg = total_revenue / current_weight_kg if current_weight_kg > 0 else 0.0
            
            results.append(BiologicalFinancialReportItem(
                batch_id=batch.id,
                batch_number=batch.batch_number,
                species_name=batch.species.arabic_name,
                pond_name=batch.pond.name,
                # البيانات الحيوية
                initial_count=batch.initial_count,
                current_count=batch.current_count,
                initial_weight_kg=float(batch.initial_weight),
                current_weight_kg=current_weight_kg,
                weight_gain_kg=float(weight_gain),
                fcr=float(fcr) if fcr else None,
                mortality_rate=float(batch.mortality_rate),
                days_active=days_active,
                # البيانات المالية
                initial_cost=float(batch.initial_cost),
                total_feed_cost=float(total_feed_cost),
                total_biological_cost=total_biological_cost,
                total_revenue=total_revenue,
                profit=profit,
                profit_margin=profit_margin,
                cost_per_kg=cost_per_kg,
                revenue_per_kg=revenue_per_kg,
                # المؤشرات
                roi=roi,
                status=batch.status,
            ))
        
        return results
    except Exception as e:
        return 500, ErrorResponse(detail=f"خطأ في استرجاع التقرير: {str(e)}")


# ==================== Feed Efficiency Report ====================

@router.get('/feed-efficiency', response={200: List[FeedEfficiencyItem]}, auth=TokenAuth())
def get_feed_efficiency_report(request, batch_id: Optional[int] = None):
    """
    تقرير كفاءة العلف (Feed Efficiency)
    
    **Parameters:**
    - batch_id (optional): تصفية حسب دفعة معينة
    
    **Returns:**
    - قائمة بالدفعات مع بيانات كفاءة العلف
    """
    try:
        from biological.models import Batch
        from daily_operations.models import FeedingLog
        from daily_operations.utils import calculate_fcr
        from django.db.models import Sum, Count
        from datetime import date
        
        queryset = Batch.objects.select_related('species').all()
        if batch_id:
            queryset = queryset.filter(id=batch_id)
        
        results = []
        for batch in queryset:
            # إجمالي العلف المستهلك
            feeding_logs = FeedingLog.objects.filter(batch=batch)
            total_feed = feeding_logs.aggregate(
                total=Sum('quantity')
            )['total'] or Decimal('0.00')
            total_feed_kg = float(total_feed)
            
            # حساب زيادة الوزن
            initial_weight = float(batch.initial_weight or 0)
            current_weight = float(batch.current_weight or 0) if hasattr(batch, 'current_weight') else initial_weight
            total_weight_gain_kg = max(0, (current_weight - initial_weight) / 1000)  # تحويل من جرام إلى كجم
            
            # حساب FCR
            fcr = calculate_fcr(batch)
            
            # متوسط العلف اليومي
            feeding_count = feeding_logs.count()
            avg_daily_feed_kg = 0.0
            feeding_days = 0
            
            if feeding_count > 0:
                # حساب عدد الأيام
                if hasattr(batch, 'stocking_date') and batch.stocking_date:
                    days_active = (date.today() - batch.stocking_date).days
                    feeding_days = max(1, days_active)
                    avg_daily_feed_kg = total_feed_kg / feeding_days
                else:
                    feeding_days = feeding_count
                    avg_daily_feed_kg = total_feed_kg / feeding_count
            
            results.append(FeedEfficiencyItem(
                batch_id=batch.id,
                batch_number=batch.batch_number,
                species_name=batch.species.arabic_name,
                total_feed_consumed_kg=total_feed_kg,
                total_weight_gain_kg=total_weight_gain_kg,
                fcr=float(fcr) if fcr else None,
                avg_daily_feed_kg=avg_daily_feed_kg,
                feeding_days=feeding_days,
            ))
        
        return results
    except Exception as e:
        return 500, ErrorResponse(detail=f"خطأ في استرجاع التقرير: {str(e)}")


# ==================== Mortality Analysis Report ====================

@router.get('/mortality-analysis', response={200: List[MortalityAnalysisItem]}, auth=TokenAuth())
def get_mortality_analysis_report(request, batch_id: Optional[int] = None):
    """
    تحليل النفوق للدفعات
    
    **Parameters:**
    - batch_id (optional): تصفية حسب دفعة معينة
    
    **Returns:**
    - قائمة بالدفعات مع بيانات النفوق
    """
    try:
        from biological.models import Batch
        from daily_operations.models import MortalityLog
        from django.db.models import Sum, Count
        from datetime import date
        
        queryset = Batch.objects.select_related('species', 'pond').all()
        if batch_id:
            queryset = queryset.filter(id=batch_id)
        
        results = []
        today = date.today()
        
        for batch in queryset:
            # حساب النفوق
            mortality_logs = MortalityLog.objects.filter(batch=batch)
            total_mortality = mortality_logs.aggregate(
                total=Sum('count')
            )['total'] or 0
            
            # حساب معدل النفوق
            mortality_rate = float(batch.mortality_rate) if hasattr(batch, 'mortality_rate') else 0.0
            
            # حساب متوسط النفوق اليومي
            mortality_count = mortality_logs.count()
            avg_daily_mortality = 0.0
            mortality_days = 0
            
            if mortality_count > 0:
                days_active = (today - batch.start_date).days
                mortality_days = max(1, days_active)
                avg_daily_mortality = total_mortality / mortality_days if mortality_days > 0 else 0.0
            
            results.append(MortalityAnalysisItem(
                batch_id=batch.id,
                batch_number=batch.batch_number,
                species_name=batch.species.arabic_name,
                pond_name=batch.pond.name,
                initial_count=batch.initial_count,
                current_count=batch.current_count,
                total_mortality=total_mortality,
                mortality_rate=mortality_rate,
                avg_daily_mortality=avg_daily_mortality,
                mortality_days=mortality_days,
                status=batch.status,
            ))
        
        return results
    except Exception as e:
        return 500, ErrorResponse(detail=f"خطأ في استرجاع التقرير: {str(e)}")
