"""
API Endpoints لقراءات المستشعرات (IoT Sensor Readings)
"""
import logging
from ninja import Router
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from .auth import TokenAuth, ErrorResponse
from biological.models import Pond, SensorReading

router = Router()
logger = logging.getLogger('api')


# ==================== Schemas ====================

class SensorReadingSchema(BaseModel):
    """Schema لعرض قراءة مستشعر"""
    id: int
    pond_id: int
    pond_name: str
    sensor_type: str
    reading_value: float
    unit: str
    reading_date: str
    is_alert: bool
    alert_message: Optional[str] = None
    sensor_id: Optional[str] = None
    notes: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


class SensorReadingCreateSchema(BaseModel):
    """Schema لإنشاء قراءة مستشعر"""
    pond_id: int
    sensor_type: str
    reading_value: float
    unit: str = ''
    reading_date: Optional[datetime] = None
    is_alert: bool = False
    alert_message: Optional[str] = None
    sensor_id: Optional[str] = None
    notes: Optional[str] = None


# ==================== Endpoints ====================

@router.post('/sensor-readings', response={201: SensorReadingSchema, 400: ErrorResponse}, auth=TokenAuth())
def create_sensor_reading(request, data: SensorReadingCreateSchema):
    """
    استقبال قراءة مستشعر من نظام IoT
    
    **Authentication:** Bearer Token مطلوب
    **Usage:** يمكن استخدامه من أنظمة IoT لاستقبال القراءات تلقائياً
    """
    try:
        pond = Pond.objects.get(id=data.pond_id, is_active=True)
        
        # استخدام التاريخ المحدد أو التاريخ الحالي
        reading_date = data.reading_date or datetime.now()
        
        reading = SensorReading.objects.create(
            pond=pond,
            sensor_type=data.sensor_type,
            reading_value=Decimal(str(data.reading_value)),
            unit=data.unit,
            reading_date=reading_date,
            is_alert=data.is_alert,
            alert_message=data.alert_message,
            sensor_id=data.sensor_id,
            notes=data.notes,
        )
        
        logger.info(f"تم استقبال قراءة مستشعر: pond_id={pond.id}, sensor_type={data.sensor_type}, value={data.reading_value}")
        
        return 201, SensorReadingSchema(
            id=reading.id,
            pond_id=reading.pond.id,
            pond_name=reading.pond.name,
            sensor_type=reading.sensor_type,
            reading_value=float(reading.reading_value),
            unit=reading.unit,
            reading_date=reading.reading_date.isoformat(),
            is_alert=reading.is_alert,
            alert_message=reading.alert_message,
            sensor_id=reading.sensor_id,
            notes=reading.notes,
            created_at=reading.created_at.isoformat(),
        )
    except Pond.DoesNotExist:
        logger.warning(f"محاولة إنشاء قراءة مستشعر لحوض غير موجود: pond_id={data.pond_id}")
        return 400, ErrorResponse(detail="الحوض غير موجود أو غير نشط")
    except Exception as e:
        logger.error(f"خطأ غير متوقع في إنشاء قراءة مستشعر: {str(e)}", exc_info=True)
        return 400, ErrorResponse(detail=f"خطأ في إنشاء قراءة المستشعر: {str(e)}")


@router.get('/sensor-readings', response={200: List[SensorReadingSchema]}, auth=TokenAuth())
def get_sensor_readings(
    request,
    pond_id: Optional[int] = None,
    sensor_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    is_alert: Optional[bool] = None,
    limit: int = 100
):
    """
    الحصول على قراءات المستشعرات
    
    **Parameters:**
    - pond_id (optional): تصفية حسب حوض معين
    - sensor_type (optional): تصفية حسب نوع المستشعر
    - start_date (optional): تاريخ البداية (ISO format)
    - end_date (optional): تاريخ النهاية (ISO format)
    - is_alert (optional): تصفية حسب وجود تنبيه
    - limit: عدد القراءات (افتراضي: 100)
    
    **Returns:**
    - قائمة بقراءات المستشعرات
    """
    try:
        from datetime import datetime
        
        queryset = SensorReading.objects.select_related('pond').all()
        
        if pond_id:
            queryset = queryset.filter(pond_id=pond_id)
        
        if sensor_type:
            queryset = queryset.filter(sensor_type=sensor_type)
        
        if start_date:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            queryset = queryset.filter(reading_date__gte=start)
        
        if end_date:
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            queryset = queryset.filter(reading_date__lte=end)
        
        if is_alert is not None:
            queryset = queryset.filter(is_alert=is_alert)
        
        readings = queryset.order_by('-reading_date')[:limit]
        
        return [
            SensorReadingSchema(
                id=r.id,
                pond_id=r.pond.id,
                pond_name=r.pond.name,
                sensor_type=r.sensor_type,
                reading_value=float(r.reading_value),
                unit=r.unit,
                reading_date=r.reading_date.isoformat(),
                is_alert=r.is_alert,
                alert_message=r.alert_message,
                sensor_id=r.sensor_id,
                notes=r.notes,
                created_at=r.created_at.isoformat(),
            )
            for r in readings
        ]
    except Exception as e:
        logger.error(f"خطأ في استرجاع قراءات المستشعرات: {str(e)}", exc_info=True)
        return 500, ErrorResponse(detail=f"خطأ في استرجاع البيانات: {str(e)}")


@router.get('/sensor-readings/{reading_id}', response={200: SensorReadingSchema, 404: ErrorResponse}, auth=TokenAuth())
def get_sensor_reading(request, reading_id: int):
    """
    الحصول على قراءة مستشعر محددة
    
    **Returns:**
    - معلومات قراءة المستشعر
    """
    try:
        reading = SensorReading.objects.select_related('pond').get(id=reading_id)
        
        return SensorReadingSchema(
            id=reading.id,
            pond_id=reading.pond.id,
            pond_name=reading.pond.name,
            sensor_type=reading.sensor_type,
            reading_value=float(reading.reading_value),
            unit=reading.unit,
            reading_date=reading.reading_date.isoformat(),
            is_alert=reading.is_alert,
            alert_message=reading.alert_message,
            sensor_id=reading.sensor_id,
            notes=reading.notes,
            created_at=reading.created_at.isoformat(),
        )
    except SensorReading.DoesNotExist:
        logger.warning(f"محاولة استرجاع قراءة مستشعر غير موجودة: reading_id={reading_id}")
        return 404, ErrorResponse(detail=f"قراءة المستشعر رقم {reading_id} غير موجودة")
    except Exception as e:
        logger.error(f"خطأ في استرجاع قراءة المستشعر: {str(e)}", exc_info=True)
        return 500, ErrorResponse(detail=f"خطأ في استرجاع البيانات: {str(e)}")
