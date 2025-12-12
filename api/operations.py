"""
API Endpoints للعمليات اليومية (Feeding & Mortality)
"""
import logging
from ninja import Router
from ninja.security import HttpBearer
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from decimal import Decimal

from .auth import TokenAuth, ErrorResponse
from daily_operations.models import FeedingLog, MortalityLog
from daily_operations.utils import get_batch_statistics
from biological.models import Batch
from inventory.models import FeedType

router = Router()
logger = logging.getLogger('api')


# ==================== Schemas ====================

class FeedingLogSchema(BaseModel):
    """Schema لعرض سجل التغذية"""
    id: int
    batch_id: int
    batch_number: str
    feed_type_id: int
    feed_type_name: str
    feeding_date: date
    quantity: float
    unit_price: float
    total_cost: float
    notes: Optional[str] = None
    created_by_id: Optional[int] = None
    created_at: str

    class Config:
        from_attributes = True


class FeedingLogCreateSchema(BaseModel):
    """Schema لإنشاء سجل تغذية"""
    batch_id: int
    feed_type_id: int
    feeding_date: date
    quantity: float
    unit_price: float
    notes: Optional[str] = None


class FeedingLogUpdateSchema(BaseModel):
    """Schema لتحديث سجل تغذية"""
    feed_type_id: Optional[int] = None
    feeding_date: Optional[date] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    notes: Optional[str] = None


class MortalityLogSchema(BaseModel):
    """Schema لعرض سجل النفوق"""
    id: int
    batch_id: int
    batch_number: str
    mortality_date: date
    count: int
    average_weight: Optional[float] = None
    cause: Optional[str] = None
    notes: Optional[str] = None
    created_by_id: Optional[int] = None
    created_at: str

    class Config:
        from_attributes = True


class MortalityLogCreateSchema(BaseModel):
    """Schema لإنشاء سجل نفوق"""
    batch_id: int
    mortality_date: date
    count: int
    average_weight: Optional[float] = None
    cause: Optional[str] = None
    notes: Optional[str] = None


class MortalityLogUpdateSchema(BaseModel):
    """Schema لتحديث سجل نفوق"""
    mortality_date: Optional[date] = None
    count: Optional[int] = None
    average_weight: Optional[float] = None
    cause: Optional[str] = None
    notes: Optional[str] = None


class BatchStatisticsSchema(BaseModel):
    """Schema لإحصائيات الدفعة"""
    batch_id: int
    batch_number: str
    total_feed_consumed: float
    total_feed_cost: float
    total_mortality: int
    current_count: int
    current_weight: float
    average_weight: float
    mortality_rate: float
    fcr: Optional[float] = None
    avg_daily_feed: float
    feeding_days: int


# ==================== Feeding Log Endpoints ====================

@router.get('/feeding', response={200: List[FeedingLogSchema]}, auth=TokenAuth())
def list_feeding_logs(request, batch_id: Optional[int] = None):
    """قائمة سجلات التغذية"""
    queryset = FeedingLog.objects.select_related('batch', 'feed_type', 'created_by').all()
    
    if batch_id:
        queryset = queryset.filter(batch_id=batch_id)
    
    logs = queryset.order_by('-feeding_date', '-created_at')
    
    return [
        FeedingLogSchema(
            id=log.id,
            batch_id=log.batch.id,
            batch_number=log.batch.batch_number,
            feed_type_id=log.feed_type.id,
            feed_type_name=log.feed_type.arabic_name,
            feeding_date=log.feeding_date,
            quantity=float(log.quantity),
            unit_price=float(log.unit_price),
            total_cost=float(log.total_cost),
            notes=log.notes,
            created_by_id=log.created_by.id if log.created_by else None,
            created_at=log.created_at.isoformat(),
        )
        for log in logs
    ]


@router.get('/feeding/{log_id}', response={200: FeedingLogSchema, 404: ErrorResponse}, auth=TokenAuth())
def get_feeding_log(request, log_id: int):
    """الحصول على سجل تغذية محدد"""
    try:
        log = FeedingLog.objects.select_related('batch', 'feed_type', 'created_by').get(id=log_id)
        return FeedingLogSchema(
            id=log.id,
            batch_id=log.batch.id,
            batch_number=log.batch.batch_number,
            feed_type_id=log.feed_type.id,
            feed_type_name=log.feed_type.arabic_name,
            feeding_date=log.feeding_date,
            quantity=float(log.quantity),
            unit_price=float(log.unit_price),
            total_cost=float(log.total_cost),
            notes=log.notes,
            created_by_id=log.created_by.id if log.created_by else None,
            created_at=log.created_at.isoformat(),
        )
    except FeedingLog.DoesNotExist:
        return 404, ErrorResponse(detail="سجل التغذية غير موجود")


@router.post('/feeding', response={201: FeedingLogSchema, 400: ErrorResponse}, auth=TokenAuth())
def create_feeding_log(request, data: FeedingLogCreateSchema):
    """إنشاء سجل تغذية جديد"""
    try:
        batch = Batch.objects.get(id=data.batch_id, is_active=True)
        feed_type = FeedType.objects.get(id=data.feed_type_id, is_active=True)
        
        log = FeedingLog.objects.create(
            batch=batch,
            feed_type=feed_type,
            feeding_date=data.feeding_date,
            quantity=Decimal(str(data.quantity)),
            unit_price=Decimal(str(data.unit_price)),
            notes=data.notes,
            created_by=request.user if hasattr(request, 'user') else None,
        )
        
        log.refresh_from_db()
        return 201, FeedingLogSchema(
            id=log.id,
            batch_id=log.batch.id,
            batch_number=log.batch.batch_number,
            feed_type_id=log.feed_type.id,
            feed_type_name=log.feed_type.arabic_name,
            feeding_date=log.feeding_date,
            quantity=float(log.quantity),
            unit_price=float(log.unit_price),
            total_cost=float(log.total_cost),
            notes=log.notes,
            created_by_id=log.created_by.id if log.created_by else None,
            created_at=log.created_at.isoformat(),
        )
    except Batch.DoesNotExist:
        logger.warning(f"محاولة إنشاء سجل تغذية لدفعة غير موجودة: batch_id={data.batch_id}, user_id={getattr(request.auth, 'id', None)}")
        return 400, ErrorResponse(detail="الدفعة غير موجودة أو غير نشطة")
    except FeedType.DoesNotExist:
        logger.warning(f"محاولة إنشاء سجل تغذية بنوع علف غير موجود: feed_type_id={data.feed_type_id}, user_id={getattr(request.auth, 'id', None)}")
        return 400, ErrorResponse(detail="نوع العلف غير موجود أو غير نشط")
    except Exception as e:
        logger.error(f"خطأ غير متوقع في إنشاء سجل التغذية: {str(e)}", exc_info=True)
        return 400, ErrorResponse(detail=f"خطأ في إنشاء سجل التغذية: {str(e)}")


@router.put('/feeding/{log_id}', response={200: FeedingLogSchema, 404: ErrorResponse, 400: ErrorResponse}, auth=TokenAuth())
def update_feeding_log(request, log_id: int, data: FeedingLogUpdateSchema):
    """تحديث سجل تغذية"""
    try:
        log = FeedingLog.objects.select_related('batch', 'feed_type', 'created_by').get(id=log_id)
        update_data = data.model_dump(exclude_unset=True)
        
        if 'feed_type_id' in update_data:
            feed_type = FeedType.objects.get(id=update_data.pop('feed_type_id'), is_active=True)
            log.feed_type = feed_type
        
        if 'quantity' in update_data:
            log.quantity = Decimal(str(update_data.pop('quantity')))
        
        if 'unit_price' in update_data:
            log.unit_price = Decimal(str(update_data.pop('unit_price')))
        
        for attr, value in update_data.items():
            setattr(log, attr, value)
        
        log.save()
        log.refresh_from_db()
        
        return FeedingLogSchema(
            id=log.id,
            batch_id=log.batch.id,
            batch_number=log.batch.batch_number,
            feed_type_id=log.feed_type.id,
            feed_type_name=log.feed_type.arabic_name,
            feeding_date=log.feeding_date,
            quantity=float(log.quantity),
            unit_price=float(log.unit_price),
            total_cost=float(log.total_cost),
            notes=log.notes,
            created_by_id=log.created_by.id if log.created_by else None,
            created_at=log.created_at.isoformat(),
        )
    except FeedingLog.DoesNotExist:
        logger.warning(f"محاولة تحديث سجل تغذية غير موجود: log_id={log_id}, user_id={getattr(request.auth, 'id', None)}")
        return 404, ErrorResponse(detail="سجل التغذية غير موجود")
    except FeedType.DoesNotExist:
        logger.warning(f"محاولة تحديث سجل تغذية بنوع علف غير موجود: feed_type_id={data.feed_type_id}, user_id={getattr(request.auth, 'id', None)}")
        return 400, ErrorResponse(detail="نوع العلف غير موجود أو غير نشط")
    except Exception as e:
        logger.error(f"خطأ غير متوقع في تحديث سجل التغذية: log_id={log_id}, error={str(e)}", exc_info=True)
        return 400, ErrorResponse(detail=f"خطأ في تحديث سجل التغذية: {str(e)}")


@router.delete('/feeding/{log_id}', response={204: None, 404: ErrorResponse}, auth=TokenAuth())
def delete_feeding_log(request, log_id: int):
    """حذف سجل تغذية"""
    try:
        log = FeedingLog.objects.select_related('batch', 'feed_type').get(id=log_id)
        log.delete()
        return 204, None
    except FeedingLog.DoesNotExist:
        return 404, ErrorResponse(detail="سجل التغذية غير موجود")


# ==================== Mortality Log Endpoints ====================

@router.get('/mortality', response={200: List[MortalityLogSchema]}, auth=TokenAuth())
def list_mortality_logs(request, batch_id: Optional[int] = None):
    """قائمة سجلات النفوق"""
    queryset = MortalityLog.objects.select_related('batch', 'created_by').all()
    
    if batch_id:
        queryset = queryset.filter(batch_id=batch_id)
    
    logs = queryset.order_by('-mortality_date', '-created_at')
    
    return [
        MortalityLogSchema(
            id=log.id,
            batch_id=log.batch.id,
            batch_number=log.batch.batch_number,
            mortality_date=log.mortality_date,
            count=log.count,
            average_weight=float(log.average_weight) if log.average_weight else None,
            cause=log.cause,
            notes=log.notes,
            created_by_id=log.created_by.id if log.created_by else None,
            created_at=log.created_at.isoformat(),
        )
        for log in logs
    ]


@router.get('/mortality/{log_id}', response={200: MortalityLogSchema, 404: ErrorResponse}, auth=TokenAuth())
def get_mortality_log(request, log_id: int):
    """الحصول على سجل نفوق محدد"""
    try:
        log = MortalityLog.objects.select_related('batch', 'created_by').get(id=log_id)
        return MortalityLogSchema(
            id=log.id,
            batch_id=log.batch.id,
            batch_number=log.batch.batch_number,
            mortality_date=log.mortality_date,
            count=log.count,
            average_weight=float(log.average_weight) if log.average_weight else None,
            cause=log.cause,
            notes=log.notes,
            created_by_id=log.created_by.id if log.created_by else None,
            created_at=log.created_at.isoformat(),
        )
    except MortalityLog.DoesNotExist:
        return 404, ErrorResponse(detail="سجل النفوق غير موجود")


@router.post('/mortality', response={201: MortalityLogSchema, 400: ErrorResponse}, auth=TokenAuth())
def create_mortality_log(request, data: MortalityLogCreateSchema):
    """إنشاء سجل نفوق جديد"""
    try:
        batch = Batch.objects.get(id=data.batch_id, is_active=True)
        
        log = MortalityLog.objects.create(
            batch=batch,
            mortality_date=data.mortality_date,
            count=data.count,
            average_weight=Decimal(str(data.average_weight)) if data.average_weight else None,
            cause=data.cause,
            notes=data.notes,
            created_by=request.user if hasattr(request, 'user') else None,
        )
        
        log.refresh_from_db()
        return 201, MortalityLogSchema(
            id=log.id,
            batch_id=log.batch.id,
            batch_number=log.batch.batch_number,
            mortality_date=log.mortality_date,
            count=log.count,
            average_weight=float(log.average_weight) if log.average_weight else None,
            cause=log.cause,
            notes=log.notes,
            created_by_id=log.created_by.id if log.created_by else None,
            created_at=log.created_at.isoformat(),
        )
    except Batch.DoesNotExist:
        logger.warning(f"محاولة إنشاء سجل نفوق لدفعة غير موجودة: batch_id={data.batch_id}, user_id={getattr(request.auth, 'id', None)}")
        return 400, ErrorResponse(detail="الدفعة غير موجودة أو غير نشطة")
    except Exception as e:
        logger.error(f"خطأ غير متوقع في إنشاء سجل النفوق: {str(e)}", exc_info=True)
        return 400, ErrorResponse(detail=f"خطأ في إنشاء سجل النفوق: {str(e)}")


@router.put('/mortality/{log_id}', response={200: MortalityLogSchema, 404: ErrorResponse, 400: ErrorResponse}, auth=TokenAuth())
def update_mortality_log(request, log_id: int, data: MortalityLogUpdateSchema):
    """تحديث سجل نفوق"""
    try:
        log = MortalityLog.objects.select_related('batch', 'created_by').get(id=log_id)
        update_data = data.model_dump(exclude_unset=True)
        
        if 'average_weight' in update_data and update_data['average_weight']:
            log.average_weight = Decimal(str(update_data.pop('average_weight')))
        
        for attr, value in update_data.items():
            setattr(log, attr, value)
        
        log.save()
        log.refresh_from_db()
        
        return MortalityLogSchema(
            id=log.id,
            batch_id=log.batch.id,
            batch_number=log.batch.batch_number,
            mortality_date=log.mortality_date,
            count=log.count,
            average_weight=float(log.average_weight) if log.average_weight else None,
            cause=log.cause,
            notes=log.notes,
            created_by_id=log.created_by.id if log.created_by else None,
            created_at=log.created_at.isoformat(),
        )
    except MortalityLog.DoesNotExist:
        return 404, ErrorResponse(detail="سجل النفوق غير موجود")
    except Exception as e:
        return 400, ErrorResponse(detail=f"خطأ في تحديث سجل النفوق: {str(e)}")


@router.delete('/mortality/{log_id}', response={204: None, 404: ErrorResponse}, auth=TokenAuth())
def delete_mortality_log(request, log_id: int):
    """حذف سجل نفوق"""
    try:
        log = MortalityLog.objects.select_related('batch').get(id=log_id)
        log.delete()
        return 204, None
    except MortalityLog.DoesNotExist:
        return 404, ErrorResponse(detail="سجل النفوق غير موجود")


# ==================== Batch Statistics Endpoint ====================

@router.get('/batch-stats/{batch_id}', response={200: BatchStatisticsSchema, 404: ErrorResponse}, auth=TokenAuth())
def get_batch_statistics_endpoint(request, batch_id: int):
    """الحصول على إحصائيات شاملة للدفعة"""
    try:
        batch = Batch.objects.select_related('pond', 'species').get(id=batch_id, is_active=True)
        stats = get_batch_statistics(batch)
        
        return BatchStatisticsSchema(
            batch_id=batch.id,
            batch_number=batch.batch_number,
            total_feed_consumed=float(stats['total_feed_consumed']),
            total_feed_cost=float(stats['total_feed_cost']),
            total_mortality=stats['total_mortality'],
            current_count=stats['current_count'],
            current_weight=float(stats['current_weight']),
            average_weight=float(stats['average_weight']),
            mortality_rate=float(stats['mortality_rate']),
            fcr=stats['fcr'],
            avg_daily_feed=float(stats['avg_daily_feed']),
            feeding_days=stats['feeding_days'],
        )
    except Batch.DoesNotExist:
        return 404, ErrorResponse(detail="الدفعة غير موجودة")

