"""
Permission helpers للتحقق من صلاحيات المستخدم
"""
from typing import List
from functools import wraps
from django.http import HttpRequest
from .auth import ErrorResponse


# Roles hierarchy
ROLE_PERMISSIONS = {
    'owner': ['owner', 'manager', 'accountant', 'worker', 'viewer'],
    'manager': ['manager', 'accountant', 'worker', 'viewer'],
    'accountant': ['accountant', 'viewer'],
    'worker': ['worker'],
    'viewer': ['viewer'],
}

# Permissions by feature
FEATURE_PERMISSIONS = {
    'reports': ['owner', 'manager', 'accountant'],
    'accounting': ['owner', 'manager', 'accountant'],
    'sales': ['owner', 'manager', 'accountant'],
    'zatca': ['owner', 'manager', 'accountant'],
    'daily_operations': ['owner', 'manager', 'accountant', 'worker'],
    'inventory': ['owner', 'manager', 'accountant', 'worker'],
    'biological': ['owner', 'manager', 'accountant', 'worker'],
    'view_only': ['owner', 'manager', 'accountant', 'worker', 'viewer'],
}


def check_role_permission(user_role: str, allowed_roles: List[str]) -> bool:
    """
    التحقق من صلاحية الدور
    
    Args:
        user_role: دور المستخدم الحالي
        allowed_roles: قائمة الأدوار المسموحة
    
    Returns:
        True إذا كان المستخدم لديه الصلاحية
    """
    if not user_role:
        return False
    
    # الحصول على جميع الأدوار المسموحة للمستخدم
    user_allowed_roles = ROLE_PERMISSIONS.get(user_role, [])
    
    # التحقق من وجود تقاطع بين الأدوار المسموحة
    return any(role in user_allowed_roles for role in allowed_roles)


def check_feature_permission(user_role: str, feature: str) -> bool:
    """
    التحقق من صلاحية الميزة
    
    Args:
        user_role: دور المستخدم الحالي
        feature: اسم الميزة
    
    Returns:
        True إذا كان المستخدم لديه الصلاحية
    """
    allowed_roles = FEATURE_PERMISSIONS.get(feature, [])
    return check_role_permission(user_role, allowed_roles)


def require_roles(allowed_roles: List[str]):
    """
    Decorator للتحقق من الصلاحيات
    
    Usage:
        @require_roles(['owner', 'manager'])
        def my_endpoint(request):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.auth:
                return 401, ErrorResponse(detail="غير مصرح - يرجى تسجيل الدخول")
            
            user_role = getattr(request.auth, 'role', None)
            if not check_role_permission(user_role, allowed_roles):
                return 403, ErrorResponse(
                    detail=f"ليس لديك صلاحية للوصول إلى هذا المورد. الصلاحية المطلوبة: {', '.join(allowed_roles)}"
                )
            
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_feature(feature: str):
    """
    Decorator للتحقق من صلاحية الميزة
    
    Usage:
        @require_feature('reports')
        def my_endpoint(request):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.auth:
                return 401, ErrorResponse(detail="غير مصرح - يرجى تسجيل الدخول")
            
            user_role = getattr(request.auth, 'role', None)
            if not check_feature_permission(user_role, feature):
                allowed_roles = FEATURE_PERMISSIONS.get(feature, [])
                return 403, ErrorResponse(
                    detail=f"ليس لديك صلاحية للوصول إلى {feature}. الصلاحية المطلوبة: {', '.join(allowed_roles)}"
                )
            
            return func(request, *args, **kwargs)
        return wrapper
    return decorator

