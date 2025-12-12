"""
API Endpoints للمصادقة (Authentication)
"""
import logging
from ninja import Router
from ninja.security import HttpBearer
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from pydantic import BaseModel, EmailStr
from typing import Optional

User = get_user_model()
router = Router()

# Logger مخصص لمصادقة JWT
logger = logging.getLogger(__name__)


class TokenAuth(HttpBearer):
    """Authentication class للـ Bearer Token"""
    
    def authenticate(self, request, token):
        """
        التحقق من JWT Token وإرجاع المستخدم
        
        يتم تسجيل الأخطاء بشكل آمن دون كشف معلومات حساسة
        """
        try:
            from rest_framework_simplejwt.authentication import JWTAuthentication
            jwt_auth = JWTAuthentication()
            validated_token = jwt_auth.get_validated_token(token)
            user = jwt_auth.get_user(validated_token)
            return user
        except InvalidToken as e:
            # تسجيل خطأ Token غير صالح (بدون كشف محتوى Token)
            logger.warning(
                f"محاولة مصادقة فاشلة: Token غير صالح - {type(e).__name__}",
                extra={
                    'error_type': type(e).__name__,
                    'path': request.path,
                    'method': request.method,
                    'ip': self._get_client_ip(request),
                }
            )
            return None
        except TokenError as e:
            # تسجيل خطأ Token عام
            logger.warning(
                f"خطأ في التحقق من Token: {type(e).__name__}",
                extra={
                    'error_type': type(e).__name__,
                    'path': request.path,
                    'method': request.method,
                    'ip': self._get_client_ip(request),
                }
            )
            return None
        except Exception as e:
            # تسجيل أي أخطاء أخرى غير متوقعة
            logger.error(
                f"خطأ غير متوقع في مصادقة Token: {type(e).__name__}",
                extra={
                    'error_type': type(e).__name__,
                    'path': request.path,
                    'method': request.method,
                    'ip': self._get_client_ip(request),
                },
                exc_info=True
            )
            return None
    
    def _get_client_ip(self, request):
        """الحصول على IP العميل بشكل آمن"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


# Schemas
class LoginSchema(BaseModel):
    """Schema لطلب تسجيل الدخول"""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Schema لرد Token"""
    access: str
    refresh: str
    user: dict


class UserInfoResponse(BaseModel):
    """Schema لمعلومات المستخدم"""
    id: int
    username: str
    email: str
    full_name: str
    role: str
    is_staff: bool


class ErrorResponse(BaseModel):
    """Schema للأخطاء"""
    detail: str

class RefreshSchema(BaseModel):
    """Schema لطلب تجديد Token"""
    refresh: str


@router.post('/login', response={200: TokenResponse, 401: ErrorResponse})
def login(request, credentials: LoginSchema):
    """
    تسجيل الدخول والحصول على JWT Token
    
    **Parameters:**
    - username: اسم المستخدم
    - password: كلمة المرور
    
    **Returns:**
    - access: Access Token
    - refresh: Refresh Token
    - user: معلومات المستخدم
    """
    user = authenticate(
        request=request,
        username=credentials.username,
        password=credentials.password
    )
    
    if user is None:
        return 401, ErrorResponse(detail="اسم المستخدم أو كلمة المرور غير صحيحة")
    
    if not user.is_active:
        return 401, ErrorResponse(detail="الحساب معطل")
    
    # تسجيل محاولة تسجيل الدخول في Audit Log
    try:
        from audit.utils import log_action, get_client_ip
        log_action(
            action_type='login',
            entity_type='user',
            entity_id=user.id,
            entity_description=f"{user.full_name} ({user.username})",
            user=user,
            description='تسجيل دخول ناجح',
            user_ip=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            request=request,
        )
    except Exception:
        pass  # لا نريد أن تفشل عملية تسجيل الدخول بسبب Audit Log
    
    # توليد Tokens
    refresh = RefreshToken.for_user(user)
    access_token = refresh.access_token
    
    # الحصول على full_name بشكل آمن
    full_name = getattr(user, 'full_name', None) or user.get_full_name() or user.username
    
    return 200, TokenResponse(
        access=str(access_token),
        refresh=str(refresh),
        user={
            'id': user.id,
            'username': user.username,
            'email': user.email or '',
            'full_name': full_name,
            'role': getattr(user, 'role', 'worker'),
            'is_staff': user.is_staff,
        }
    )


class RefreshSchema(BaseModel):
    """Schema لطلب تجديد Token"""
    refresh: str

@router.post('/refresh', response={200: dict, 401: ErrorResponse})
def refresh_token(request, data: RefreshSchema):
    """
    تجديد Access Token باستخدام Refresh Token
    
    **Parameters:**
    - refresh: Refresh Token
    
    **Returns:**
    - access: Access Token الجديد
    """
    try:
        refresh_token_obj = RefreshToken(data.refresh)
        access_token = refresh_token_obj.access_token
        return 200, {'access': str(access_token)}
    except Exception as e:
        return 401, ErrorResponse(detail=f"Token غير صالح: {str(e)}")


@router.get('/me', response={200: UserInfoResponse, 401: ErrorResponse}, auth=TokenAuth())
def get_current_user(request):
    """
    الحصول على معلومات المستخدم الحالي
    
    **Authentication:** Bearer Token مطلوب
    
    **Returns:**
    - معلومات المستخدم الحالي
    """
    if not request.auth:
        return 401, ErrorResponse(detail="غير مصرح")
    
    user = request.auth
    
    # الحصول على full_name بشكل آمن
    full_name = getattr(user, 'full_name', None) or user.get_full_name() or user.username
    
    return 200, UserInfoResponse(
        id=user.id,
        username=user.username,
        email=user.email or '',
        full_name=full_name,
        role=getattr(user, 'role', 'worker'),
        is_staff=user.is_staff,
    )


@router.post('/logout', response={200: dict, 401: ErrorResponse}, auth=TokenAuth())
def logout(request):
    """
    تسجيل الخروج (إبطال Refresh Token)
    
    **Authentication:** Bearer Token مطلوب
    
    **Note:** في التطبيق الفعلي، قد تحتاج لإضافة Refresh Token إلى Blacklist
    """
    # تسجيل تسجيل الخروج في Audit Log
    if request.auth:
        try:
            from audit.utils import log_action, get_client_ip
            log_action(
                action_type='logout',
                entity_type='user',
                entity_id=request.auth.id,
                entity_description=f"{request.auth.full_name} ({request.auth.username})",
                user=request.auth,
                description='تسجيل خروج',
                user_ip=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                request=request,
            )
        except Exception:
            pass  # لا نريد أن تفشل عملية تسجيل الخروج بسبب Audit Log
    
    # في التطبيق الفعلي، أضف Refresh Token إلى Blacklist
    return 200, {'detail': 'تم تسجيل الخروج بنجاح'}

