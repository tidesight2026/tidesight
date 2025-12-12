# 🔍 Debug Middleware للتحقق من Tenant Resolution

**التاريخ:** ديسمبر 2025

---

## 🔧 ما تم إضافته

تم إضافة `TenantDebugMiddleware` للتحقق من أن tenant يتم تحديده بشكل صحيح من requests.

### الملف: `tenants/aqua_core/middleware.py`

```python
class TenantDebugMiddleware(MiddlewareMixin):
    """Middleware للتحقق من tenant resolution"""
    
    def process_request(self, request):
        """Log tenant info"""
        from django_tenants.utils import get_tenant
        
        host = request.get_host()
        tenant = get_tenant(request)
        
        logger.info(f"🔍 Request: {request.path} | Host: {host} | Tenant: {tenant.schema_name if tenant else 'None'}")
```

---

## 🧪 الخطوة التالية

بعد إعادة تشغيل Backend، جرّب الوصول إلى:
```
http://farm1.localhost:8000/api/docs
```

ثم تحقق من السجلات:
```powershell
docker-compose logs web --tail 30 | Select-String -Pattern "🔍|tenant|Tenant"
```

هذا سيخبرنا:
- ✅ إذا كان tenant يتم تحديده من request
- ❌ إذا كان tenant = None (المشكلة هنا)

---

**أخبرني بما تراه في السجلات!** 🔍

