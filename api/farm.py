"""
API لإدارة معلومات المزرعة (Farm Info) على Public Schema
"""
from ninja import Router
from pydantic import BaseModel, EmailStr
from typing import Optional
from django_tenants.utils import schema_context
from .auth import TokenAuth, ErrorResponse
from tenants.models import FarmInfo, Client

router = Router()


class FarmInfoSchema(BaseModel):
    farm_name: str
    contact_email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    trade_number: Optional[str] = None
    logo_url: Optional[str] = None
    currency: Optional[str] = None
    timezone: Optional[str] = None
    notes: Optional[str] = None


@router.get('/', response={200: FarmInfoSchema, 404: ErrorResponse}, auth=TokenAuth())
def get_farm_info(request):
    """
    الحصول على معلومات المزرعة للـ Tenant الحالي
    """
    tenant = request.tenant
    if not tenant:
        return 404, ErrorResponse(detail="Tenant غير موجود")

    with schema_context('public'):
        try:
            info = FarmInfo.objects.get(tenant=tenant)
            return 200, FarmInfoSchema(
                farm_name=info.farm_name,
                contact_email=info.contact_email,
                phone=info.phone,
                address=info.address,
                trade_number=info.trade_number,
                logo_url=info.logo_url,
                currency=info.currency,
                timezone=info.timezone,
                notes=info.notes,
            )
        except FarmInfo.DoesNotExist:
            # إنشاء سجل افتراضي إذا لم يوجد
            info = FarmInfo.objects.create(
                tenant=tenant,
                farm_name=tenant.name,
                contact_email=tenant.email,
                trade_number=tenant.trade_number or "",
            )
            return 200, FarmInfoSchema(
                farm_name=info.farm_name,
                contact_email=info.contact_email,
                phone=info.phone,
                address=info.address,
                trade_number=info.trade_number,
                logo_url=info.logo_url,
                currency=info.currency,
                timezone=info.timezone,
                notes=info.notes,
            )


@router.put('/', response={200: FarmInfoSchema, 400: ErrorResponse}, auth=TokenAuth())
def update_farm_info(request, data: FarmInfoSchema):
    """
    تحديث معلومات المزرعة
    """
    tenant = request.tenant
    if not tenant:
        return 400, ErrorResponse(detail="Tenant غير موجود")

    with schema_context('public'):
        info, _ = FarmInfo.objects.get_or_create(
            tenant=tenant,
            defaults={
                'farm_name': tenant.name,
                'contact_email': tenant.email,
                'trade_number': tenant.trade_number or "",
            }
        )

        info.farm_name = data.farm_name
        info.contact_email = data.contact_email or ""
        info.phone = data.phone or ""
        info.address = data.address or ""
        info.trade_number = data.trade_number or ""
        info.logo_url = data.logo_url or ""
        info.currency = data.currency or "SAR"
        info.timezone = data.timezone or "Asia/Riyadh"
        info.notes = data.notes or ""
        info.save()

        return 200, FarmInfoSchema(
            farm_name=info.farm_name,
            contact_email=info.contact_email,
            phone=info.phone,
            address=info.address,
            trade_number=info.trade_number,
            logo_url=info.logo_url,
            currency=info.currency,
            timezone=info.timezone,
            notes=info.notes,
        )

