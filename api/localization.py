"""
API Endpoints للغة (Localization)
"""
from ninja import Router
from pydantic import BaseModel
from django.http import JsonResponse
from django.utils import translation
from django.conf import settings

router = Router()


class LanguageRequest(BaseModel):
    """طلب تغيير اللغة"""
    language: str  # 'ar' or 'en'


@router.post('/set-language', response={200: dict, 400: dict})
def set_language(request, data: LanguageRequest):
    """
    تعيين لغة الجلسة
    
    **اللغات المدعومة:** ar, en
    """
    # التحقق من اللغة المدعومة
    supported_languages = [lang[0] for lang in settings.LANGUAGES]
    if data.language not in supported_languages:
        return 400, {
            'error': 'Unsupported language',
            'supported_languages': supported_languages
        }
    
    # تعيين اللغة للجلسة
    translation.activate(data.language)
    if hasattr(request, 'session'):
        request.session[translation.LANGUAGE_SESSION_KEY] = data.language
    
    return {
        'success': True,
        'message': f'Language set to {data.language}',
        'language': data.language
    }


@router.get('/languages', response=dict)
def get_languages(request):
    """
    الحصول على قائمة اللغات المدعومة
    """
    return {
        'languages': [
            {'code': lang[0], 'name': lang[1]} for lang in settings.LANGUAGES
        ],
        'current': translation.get_language()
    }

