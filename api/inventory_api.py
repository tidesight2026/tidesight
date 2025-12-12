"""
API Endpoints لإدارة المخزون (Inventory)
"""
from ninja import Router
from typing import List
from pydantic import BaseModel
from inventory.models import FeedType, FeedInventory, Medicine, MedicineInventory
from .auth import TokenAuth, ErrorResponse
from decimal import Decimal

router = Router()


# Feed Schemas
class FeedTypeSchema(BaseModel):
    """Schema لنوع العلف"""
    id: int
    name: str
    arabic_name: str
    protein_percentage: float | None
    unit: str

    class Config:
        from_attributes = True


class FeedInventorySchema(BaseModel):
    """Schema لمخزون العلف"""
    id: int
    feed_type: FeedTypeSchema
    quantity: float
    unit_price: float
    expiry_date: str | None
    location: str | None

    class Config:
        from_attributes = True


class FeedInventoryCreateSchema(BaseModel):
    """Schema لإنشاء مخزون علف"""
    feed_type_id: int
    quantity: float
    unit_price: float = 0.0
    expiry_date: str | None = None
    location: str | None = None
    notes: str | None = None


class FeedInventoryUpdateSchema(BaseModel):
    """Schema لتحديث مخزون علف"""
    quantity: float | None = None
    unit_price: float | None = None
    expiry_date: str | None = None
    location: str | None = None
    notes: str | None = None


# Medicine Schemas
class MedicineSchema(BaseModel):
    """Schema للدواء"""
    id: int
    name: str
    arabic_name: str
    active_ingredient: str | None
    unit: str

    class Config:
        from_attributes = True


class MedicineInventorySchema(BaseModel):
    """Schema لمخزون الدواء"""
    id: int
    medicine: MedicineSchema
    quantity: float
    unit_price: float
    expiry_date: str | None
    location: str | None

    class Config:
        from_attributes = True


class MedicineInventoryCreateSchema(BaseModel):
    """Schema لإنشاء مخزون دواء"""
    medicine_id: int
    quantity: float
    unit_price: float = 0.0
    expiry_date: str | None = None
    location: str | None = None
    notes: str | None = None


class MedicineInventoryUpdateSchema(BaseModel):
    """Schema لتحديث مخزون دواء"""
    quantity: float | None = None
    unit_price: float | None = None
    expiry_date: str | None = None
    location: str | None = None
    notes: str | None = None


# Feed Endpoints
@router.get('/feeds/types', response={200: List[FeedTypeSchema]}, auth=TokenAuth())
def list_feed_types(request):
    """قائمة أنواع الأعلاف"""
    feed_types = FeedType.objects.filter(is_active=True).order_by('arabic_name')
    return [FeedTypeSchema.model_validate(ft) for ft in feed_types]


@router.get('/feeds', response={200: List[FeedInventorySchema]}, auth=TokenAuth())
def list_feed_inventory(request):
    """قائمة مخزون الأعلاف"""
    inventory = FeedInventory.objects.select_related('feed_type').all().order_by('-created_at')
    return [FeedInventorySchema.model_validate(item) for item in inventory]


@router.get('/feeds/{item_id}', response={200: FeedInventorySchema, 404: ErrorResponse}, auth=TokenAuth())
def get_feed_inventory(request, item_id: int):
    """الحصول على عنصر مخزون علف محدد"""
    try:
        item = FeedInventory.objects.select_related('feed_type').get(id=item_id)
        return FeedInventorySchema.model_validate(item)
    except FeedInventory.DoesNotExist:
        return 404, ErrorResponse(detail="عنصر المخزون غير موجود")


@router.post('/feeds', response={201: FeedInventorySchema, 400: ErrorResponse}, auth=TokenAuth())
def create_feed_inventory(request, data: FeedInventoryCreateSchema):
    """إنشاء عنصر مخزون علف جديد"""
    try:
        feed_type = FeedType.objects.get(id=data.feed_type_id, is_active=True)
        item = FeedInventory.objects.create(
            feed_type=feed_type,
            quantity=Decimal(str(data.quantity)),
            unit_price=Decimal(str(data.unit_price)),
            expiry_date=data.expiry_date,
            location=data.location,
            notes=data.notes,
        )
        return 201, FeedInventorySchema.model_validate(item)
    except FeedType.DoesNotExist:
        return 400, ErrorResponse(detail="نوع العلف غير موجود")
    except Exception as e:
        return 400, ErrorResponse(detail=str(e))


@router.put('/feeds/{item_id}', response={200: FeedInventorySchema, 404: ErrorResponse}, auth=TokenAuth())
def update_feed_inventory(request, item_id: int, data: FeedInventoryUpdateSchema):
    """تحديث عنصر مخزون علف"""
    try:
        item = FeedInventory.objects.get(id=item_id)
        update_data = data.model_dump(exclude_unset=True)
        
        for key, value in update_data.items():
            if key in ['quantity', 'unit_price'] and value is not None:
                setattr(item, key, Decimal(str(value)))
            else:
                setattr(item, key, value)
        
        item.save()
        return FeedInventorySchema.model_validate(item)
    except FeedInventory.DoesNotExist:
        return 404, ErrorResponse(detail="عنصر المخزون غير موجود")


@router.delete('/feeds/{item_id}', response={200: dict, 404: ErrorResponse}, auth=TokenAuth())
def delete_feed_inventory(request, item_id: int):
    """حذف عنصر مخزون علف"""
    try:
        item = FeedInventory.objects.get(id=item_id)
        item.delete()
        return {'detail': 'تم حذف عنصر المخزون بنجاح'}
    except FeedInventory.DoesNotExist:
        return 404, ErrorResponse(detail="عنصر المخزون غير موجود")


# Medicine Endpoints
@router.get('/medicines/types', response={200: List[MedicineSchema]}, auth=TokenAuth())
def list_medicine_types(request):
    """قائمة أنواع الأدوية"""
    medicines = Medicine.objects.filter(is_active=True).order_by('arabic_name')
    return [MedicineSchema.model_validate(m) for m in medicines]


@router.get('/medicines', response={200: List[MedicineInventorySchema]}, auth=TokenAuth())
def list_medicine_inventory(request):
    """قائمة مخزون الأدوية"""
    inventory = MedicineInventory.objects.select_related('medicine').all().order_by('-created_at')
    return [MedicineInventorySchema.model_validate(item) for item in inventory]


@router.get('/medicines/{item_id}', response={200: MedicineInventorySchema, 404: ErrorResponse}, auth=TokenAuth())
def get_medicine_inventory(request, item_id: int):
    """الحصول على عنصر مخزون دواء محدد"""
    try:
        item = MedicineInventory.objects.select_related('medicine').get(id=item_id)
        return MedicineInventorySchema.model_validate(item)
    except MedicineInventory.DoesNotExist:
        return 404, ErrorResponse(detail="عنصر المخزون غير موجود")


@router.post('/medicines', response={201: MedicineInventorySchema, 400: ErrorResponse}, auth=TokenAuth())
def create_medicine_inventory(request, data: MedicineInventoryCreateSchema):
    """إنشاء عنصر مخزون دواء جديد"""
    try:
        medicine = Medicine.objects.get(id=data.medicine_id, is_active=True)
        item = MedicineInventory.objects.create(
            medicine=medicine,
            quantity=Decimal(str(data.quantity)),
            unit_price=Decimal(str(data.unit_price)),
            expiry_date=data.expiry_date,
            location=data.location,
            notes=data.notes,
        )
        return 201, MedicineInventorySchema.model_validate(item)
    except Medicine.DoesNotExist:
        return 400, ErrorResponse(detail="الدواء غير موجود")
    except Exception as e:
        return 400, ErrorResponse(detail=str(e))


@router.put('/medicines/{item_id}', response={200: MedicineInventorySchema, 404: ErrorResponse}, auth=TokenAuth())
def update_medicine_inventory(request, item_id: int, data: MedicineInventoryUpdateSchema):
    """تحديث عنصر مخزون دواء"""
    try:
        item = MedicineInventory.objects.get(id=item_id)
        update_data = data.model_dump(exclude_unset=True)
        
        for key, value in update_data.items():
            if key in ['quantity', 'unit_price'] and value is not None:
                setattr(item, key, Decimal(str(value)))
            else:
                setattr(item, key, value)
        
        item.save()
        return MedicineInventorySchema.model_validate(item)
    except MedicineInventory.DoesNotExist:
        return 404, ErrorResponse(detail="عنصر المخزون غير موجود")


@router.delete('/medicines/{item_id}', response={200: dict, 404: ErrorResponse}, auth=TokenAuth())
def delete_medicine_inventory(request, item_id: int):
    """حذف عنصر مخزون دواء"""
    try:
        item = MedicineInventory.objects.get(id=item_id)
        item.delete()
        return {'detail': 'تم حذف عنصر المخزون بنجاح'}
    except MedicineInventory.DoesNotExist:
        return 404, ErrorResponse(detail="عنصر المخزون غير موجود")
