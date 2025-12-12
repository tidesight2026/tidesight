"""
Performance Decorators
Decorators لتحسين الأداء (Caching, Query Optimization)
"""
from functools import wraps
from django.core.cache import cache
from django.utils.decorators import method_decorator
import hashlib
import json


def cache_result(timeout=300, key_prefix=None):
    """
    Decorator لتخزين نتيجة الدالة في Cache
    
    Args:
        timeout: مدة Cache بالثواني (افتراضي: 5 دقائق)
        key_prefix: بادئة مخصصة لـ Cache key
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # إنشاء Cache key من اسم الدالة والـ arguments
            cache_key_parts = [key_prefix or func.__name__]
            
            # إضافة args (تجاهل self إذا كان method)
            if args:
                args_str = str(args[1:] if len(args) > 0 and hasattr(args[0], '__class__') else args)
                cache_key_parts.append(hashlib.md5(args_str.encode()).hexdigest()[:8])
            
            # إضافة kwargs
            if kwargs:
                kwargs_str = json.dumps(kwargs, sort_keys=True)
                cache_key_parts.append(hashlib.md5(kwargs_str.encode()).hexdigest()[:8])
            
            cache_key = ':'.join(cache_key_parts)
            
            # محاولة جلب من Cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # تنفيذ الدالة
            result = func(*args, **kwargs)
            
            # حفظ في Cache
            cache.set(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator


def invalidate_cache(pattern):
    """
    Decorator لإبطال Cache بعد تنفيذ دالة
    
    Args:
        pattern: نمط Cache keys لإبطالها (استخدام * للـ wildcard)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # حذف Cache keys المطابقة
            # في Redis يمكن استخدام KEYS pattern ثم DEL
            # لكن في Django cache نحتاج لتتبع keys يدوياً أو استخدام cache versioning
            try:
                if hasattr(cache, 'delete_pattern'):
                    cache.delete_pattern(pattern)
            except AttributeError:
                # Django cache backend لا يدعم delete_pattern
                # يمكن استخدام cache versioning بدلاً من ذلك
                pass
            
            return result
        return wrapper
    return decorator

