"""
API Endpoints للدعم الفني وعن المنتج (About & Support)
"""
from ninja import Router
from pydantic import BaseModel

router = Router()


class AboutResponse(BaseModel):
    """معلومات عن النظام"""
    name: str
    version: str
    description: str
    developer: dict
    support: dict


@router.get('/about', response=AboutResponse)
def get_about(request):
    """
    معلومات عن النظام (About)
    
    **جميع المستخدمين يمكنهم الوصول**
    """
    return AboutResponse(
        name="AquaERP",
        version="1.0.0",
        description="نظام ERP متخصص في إدارة المزارع السمكية - متوافق مع معايير ZATCA و SOCPA",
        developer={
            "name": "AquaERP Development Team",
            "email": "support@aquaerp.com",
            "website": "https://aquaerp.com"
        },
        support={
            "email": "support@aquaerp.com",
            "phone": "+966500000000",
            "whatsapp": "https://wa.me/966500000000",
            "hours": "الأحد - الخميس: 9:00 ص - 5:00 م"
        }
    )


@router.get('/support', response=dict)
def get_support(request):
    """
    معلومات الدعم الفني
    
    **جميع المستخدمين يمكنهم الوصول**
    """
    return {
        "technical_support": {
            "email": "support@aquaerp.com",
            "phone": "+966500000000",
            "whatsapp": "https://wa.me/966500000000",
            "working_hours": {
                "ar": "الأحد - الخميس: 9:00 ص - 5:00 م",
                "en": "Sunday - Thursday: 9:00 AM - 5:00 PM"
            }
        },
        "documentation": {
            "user_guide": "https://docs.aquaerp.com/user-guide",
            "api_docs": "/api/docs",
            "faq": "https://docs.aquaerp.com/faq"
        },
        "community": {
            "forum": "https://forum.aquaerp.com",
            "github": "https://github.com/aquaerp/aquaerp"
        }
    }

