"""
Audit Logging Middleware
لتسجيل IP و User Agent للمستخدم
"""
import threading


class AuditLoggingMiddleware:
    """
    Middleware لحفظ request في thread local
    لاستخدامه في signals
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # حفظ request في thread local
        thread_local = threading.current_thread()
        thread_local.request = request
        
        try:
            response = self.get_response(request)
            return response
        finally:
            # تنظيف بعد انتهاء request
            if hasattr(thread_local, 'request'):
                delattr(thread_local, 'request')

