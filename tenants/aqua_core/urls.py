"""
URL configuration for AquaERP project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from ninja import NinjaAPI
from api.router import api_router

# إنشاء Django Ninja API instance
# ملاحظة: api موجود في SHARED_APPS، لذا يمكن إنشاؤه مباشرة
api = NinjaAPI(
    title="AquaERP API",
    version="1.0.0",
    description="API documentation for AquaERP System",
    urls_namespace="aquaerp-api",
)

# إضافة Routers
api.add_router("", api_router)

# تخزين api.urls في متغير لتجنب إنشاء instance متعدد
api_urls = api.urls  # (urlpatterns_list, app_name, namespace)

# View بسيطة للاختبار
from django.http import JsonResponse
from django_tenants.utils import get_tenant

def root_view(request):
    """Root view للاختبار"""
    tenant = get_tenant(request)
    return JsonResponse({
        'message': 'AquaERP API',
        'tenant': tenant.schema_name if tenant else None,
        'host': request.get_host(),
    })

urlpatterns = [
    # Root path للاختبار
    path('', root_view, name='root'),
    
    # Admin panel (سيتم تفعيله لاحقاً لكل tenant)
    path('admin/', admin.site.urls),
    
    # API endpoints
    # include() يحتاج 2-tuple + namespace argument
    path('api/', include((api_urls[0], api_urls[1]), namespace=api_urls[2])),
]

# Serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    if hasattr(settings, 'MEDIA_URL'):
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

