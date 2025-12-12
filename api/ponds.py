"""
API Endpoints لإدارة الأحواض (Ponds)
"""
from ninja import Router
from typing import List
from pydantic import BaseModel
from biological.models import Pond
from .auth import TokenAuth, ErrorResponse
from tenants.aqua_core.services.quota_service import QuotaService

router = Router()


# Schemas
class PondSchema(BaseModel):
    """Schema للحوض"""
    id: int
    name: str
    pond_type: str
    capacity: float
    location: str | None
    status: str
    is_active: bool

    class Config:
        from_attributes = True


class PondCreateSchema(BaseModel):
    """Schema لإنشاء حوض جديد"""
    name: str
    pond_type: str = 'concrete'
    capacity: float
    location: str | None = None
    status: str = 'empty'


class PondUpdateSchema(BaseModel):
    """Schema لتحديث حوض"""
    name: str | None = None
    pond_type: str | None = None
    capacity: float | None = None
    location: str | None = None
    status: str | None = None
    is_active: bool | None = None


@router.get('/', response={200: List[PondSchema]}, auth=TokenAuth())
def list_ponds(request):
    """
    قائمة جميع الأحواض - مع تحسين الاستعلامات
    """
    # استخدام select_related/prefetch_related إذا كانت هناك علاقات
    # في هذه الحالة، Pond لا يحتوي على ForeignKey، لكن نضيف التحسين للاستعداد للمستقبل
    ponds = Pond.objects.filter(is_active=True).order_by('name')
    return [PondSchema.model_validate(pond) for pond in ponds]


@router.get('/{pond_id}', response={200: PondSchema, 404: ErrorResponse}, auth=TokenAuth())
def get_pond(request, pond_id: int):
    """
    الحصول على حوض محدد
    """
    try:
        pond = Pond.objects.get(id=pond_id, is_active=True)
        return PondSchema.model_validate(pond)
    except Pond.DoesNotExist:
        return 404, ErrorResponse(detail="الحوض غير موجود")


@router.post('/', response={201: PondSchema, 400: ErrorResponse, 403: ErrorResponse}, auth=TokenAuth())
def create_pond(request, data: PondCreateSchema):
    """
    إنشاء حوض جديد - مع التحقق من القيد (Quota)
    """
    # التحقق من القيد
    tenant = request.tenant
    if tenant:
        current_count = Pond.objects.filter(is_active=True).count()
        allowed, message = QuotaService.check_quota(tenant, 'max_ponds', current_count)
        
        if not allowed:
            return 403, ErrorResponse(detail=message)
    
    try:
        pond = Pond.objects.create(**data.model_dump())
        return 201, PondSchema.model_validate(pond)
    except Exception as e:
        return 400, ErrorResponse(detail=str(e))


@router.put('/{pond_id}', response={200: PondSchema, 404: ErrorResponse}, auth=TokenAuth())
def update_pond(request, pond_id: int, data: PondUpdateSchema):
    """
    تحديث حوض
    """
    try:
        pond = Pond.objects.get(id=pond_id, is_active=True)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(pond, key, value)
        pond.save()
        return PondSchema.model_validate(pond)
    except Pond.DoesNotExist:
        return 404, ErrorResponse(detail="الحوض غير موجود")


@router.delete('/{pond_id}', response={200: dict, 404: ErrorResponse}, auth=TokenAuth())
def delete_pond(request, pond_id: int):
    """
    حذف حوض (Soft Delete)
    """
    try:
        pond = Pond.objects.get(id=pond_id, is_active=True)
        pond.is_active = False
        pond.save()
        return {'detail': 'تم حذف الحوض بنجاح'}
    except Pond.DoesNotExist:
        return 404, ErrorResponse(detail="الحوض غير موجود")

