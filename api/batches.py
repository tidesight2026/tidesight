"""
API Endpoints لإدارة الدفعات (Batches)
"""
from ninja import Router
from typing import List, Optional
from pydantic import BaseModel
from biological.models import Batch, Pond, Species
from .auth import TokenAuth, ErrorResponse

router = Router()


# Schemas
class SpeciesSchema(BaseModel):
    """Schema مختصر للنوع السمكي"""
    id: int
    arabic_name: str

    class Config:
        from_attributes = True


class PondSchema(BaseModel):
    """Schema مختصر للحوض"""
    id: int
    name: str

    class Config:
        from_attributes = True


class BatchSchema(BaseModel):
    """Schema للدفعة"""
    id: int
    batch_number: str
    pond: PondSchema
    species: SpeciesSchema
    start_date: str
    initial_count: int
    initial_weight: float
    initial_cost: float
    current_count: int
    status: str
    notes: str | None

    class Config:
        from_attributes = True


class BatchCreateSchema(BaseModel):
    """Schema لإنشاء دفعة جديدة"""
    pond_id: int
    species_id: int
    batch_number: str
    start_date: str
    initial_count: int
    initial_weight: float
    initial_cost: float = 0.0
    notes: str | None = None


class BatchUpdateSchema(BaseModel):
    """Schema لتحديث دفعة"""
    current_count: int | None = None
    status: str | None = None
    notes: str | None = None


@router.get('/', response={200: List[BatchSchema]}, auth=TokenAuth())
def list_batches(request, status: Optional[str] = None, page: int = 1, page_size: int = 20):
    """
    قائمة جميع الدفعات - مع Pagination وتحسين الاستعلامات
    
    **Parameters:**
    - status: تصفية حسب الحالة (active, harvested, terminated)
    - page: رقم الصفحة (افتراضي: 1)
    - page_size: عدد العناصر في الصفحة (افتراضي: 20, أقصى: 100)
    """
    from performance.query_optimization import paginate_queryset
    
    # استخدام select_related لتقليل عدد الاستعلامات
    queryset = Batch.objects.select_related('pond', 'species').all()
    
    if status:
        queryset = queryset.filter(status=status)
    
    queryset = queryset.order_by('-start_date')
    
    # Pagination
    page_size = min(page_size, 100)  # حد أقصى 100
    paginated = paginate_queryset(queryset, page=page, page_size=page_size)
    
    return [BatchSchema.model_validate(b) for b in paginated['items']]


@router.get('/{batch_id}', response={200: BatchSchema, 404: ErrorResponse}, auth=TokenAuth())
def get_batch(request, batch_id: int):
    """
    الحصول على دفعة محددة
    """
    try:
        batch = Batch.objects.select_related('pond', 'species').get(id=batch_id)
        return BatchSchema.model_validate(batch)
    except Batch.DoesNotExist:
        return 404, ErrorResponse(detail="الدفعة غير موجودة")


@router.post('/', response={201: BatchSchema, 400: ErrorResponse}, auth=TokenAuth())
def create_batch(request, data: BatchCreateSchema):
    """
    إنشاء دفعة جديدة
    """
    try:
        pond = Pond.objects.get(id=data.pond_id, is_active=True)
        species = Species.objects.get(id=data.species_id, is_active=True)
        
        batch = Batch.objects.create(
            pond=pond,
            species=species,
            batch_number=data.batch_number,
            start_date=data.start_date,
            initial_count=data.initial_count,
            initial_weight=data.initial_weight,
            initial_cost=data.initial_cost,
            notes=data.notes,
        )
        
        # تحديث حالة الحوض
        pond.status = 'active'
        pond.save()
        
        return 201, BatchSchema.model_validate(batch)
    except Pond.DoesNotExist:
        return 400, ErrorResponse(detail="الحوض غير موجود")
    except Species.DoesNotExist:
        return 400, ErrorResponse(detail="النوع السمكي غير موجود")
    except Exception as e:
        return 400, ErrorResponse(detail=str(e))


@router.put('/{batch_id}', response={200: BatchSchema, 404: ErrorResponse}, auth=TokenAuth())
def update_batch(request, batch_id: int, data: BatchUpdateSchema):
    """
    تحديث دفعة
    """
    try:
        batch = Batch.objects.get(id=batch_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(batch, key, value)
        batch.save()
        return BatchSchema.model_validate(batch)
    except Batch.DoesNotExist:
        return 404, ErrorResponse(detail="الدفعة غير موجودة")


@router.delete('/{batch_id}', response={200: dict, 404: ErrorResponse}, auth=TokenAuth())
def delete_batch(request, batch_id: int):
    """
    حذف دفعة (Soft Delete)
    """
    try:
        batch = Batch.objects.get(id=batch_id)
        batch.status = 'terminated'
        batch.save()
        return {'detail': 'تم إنهاء الدفعة بنجاح'}
    except Batch.DoesNotExist:
        return 404, ErrorResponse(detail="الدفعة غير موجودة")

