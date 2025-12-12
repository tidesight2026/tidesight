"""
API Endpoints لإدارة الأنواع السمكية (Species)
"""
from ninja import Router
from typing import List
from pydantic import BaseModel
from biological.models import Species
from .auth import TokenAuth, ErrorResponse

router = Router()


# Schemas
class SpeciesSchema(BaseModel):
    """Schema للنوع السمكي"""
    id: int
    name: str
    arabic_name: str
    scientific_name: str | None
    description: str | None

    class Config:
        from_attributes = True


class SpeciesCreateSchema(BaseModel):
    """Schema لإنشاء نوع جديد"""
    name: str
    arabic_name: str
    scientific_name: str | None = None
    description: str | None = None


@router.get('/', response={200: List[SpeciesSchema]}, auth=TokenAuth())
def list_species(request):
    """قائمة جميع الأنواع السمكية - محسّن باستخدام Cache (10 minutes)"""
    from django.core.cache import cache
    
    cache_key = 'species:list:active'
    cached_species = cache.get(cache_key)
    
    if cached_species is not None:
        return cached_species
    
    species_list = Species.objects.filter(is_active=True).order_by('arabic_name')
    result = [SpeciesSchema.model_validate(s) for s in species_list]
    
    # Cache لمدة 10 دقائق (الأنواع لا تتغير كثيراً)
    cache.set(cache_key, result, timeout=600)
    
    return result


@router.get('/{species_id}', response={200: SpeciesSchema, 404: ErrorResponse}, auth=TokenAuth())
def get_species(request, species_id: int):
    """الحصول على نوع محدد"""
    try:
        species = Species.objects.get(id=species_id, is_active=True)
        return SpeciesSchema.model_validate(species)
    except Species.DoesNotExist:
        return 404, ErrorResponse(detail="النوع غير موجود")


@router.post('/', response={201: SpeciesSchema, 400: ErrorResponse}, auth=TokenAuth())
def create_species(request, data: SpeciesCreateSchema):
    """إنشاء نوع جديد"""
    try:
        species = Species.objects.create(**data.model_dump())
        return 201, SpeciesSchema.model_validate(species)
    except Exception as e:
        return 400, ErrorResponse(detail=str(e))

