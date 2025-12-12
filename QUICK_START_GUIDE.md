# AquaERP: دليل البدء السريع
**للبدء الفوري في التنفيذ**

---

## 🚀 البدء الفوري (خطوات سريعة)

### الخطوة 1: إصلاح الأخطاء الحالية (30 دقيقة)

#### 1.1 إصلاح `tenants/models.py`
```python
# في Domain class
def __str__(self):
    return self.domain  # بدلاً من self.domain_is_primary
```

#### 1.2 إنشاء `manage.py` في الجذر
```python
#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tenants.aqua_core.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(...) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
```

#### 1.3 إنشاء `tenants/aqua_core/wsgi.py`
```python
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tenants.aqua_core.settings')
application = get_wsgi_application()
```

#### 1.4 إنشاء `tenants/aqua_core/urls.py`
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
]
```

---

### الخطوة 2: تحديث Requirements (15 دقيقة)

أضف إلى `requirements.txt`:
```
# موجود ✅
Django>=5.0,<5.1
django-tenants>=3.6.0
psycopg2-binary>=2.9.9
django-ninja>=1.1.0
gunicorn>=21.2.0

# إضافة جديدة
celery>=5.3.0
redis>=5.0.0
djangorestframework-simplejwt>=5.3.0
django-cors-headers>=4.3.0
python-dotenv>=1.0.0
```

---

### الخطوة 3: تحديث Docker Compose (20 دقيقة)

أضف إلى `docker-compose.yml`:
```yaml
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

---

### الخطوة 4: إنشاء .env.example (10 دقائق)

```env
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
DATABASE_URL=postgresql://aqua_admin:secure_pass_123@db:5432/aqua_erp_db
REDIS_URL=redis://redis:6379/0
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## 📋 خطة التنفيذ السريعة

### اليوم الأول (8 ساعات)
- [x] إصلاح الأخطاء الأساسية
- [ ] إنشاء الملفات المفقودة
- [ ] تحديث Requirements و Docker
- [ ] اختبار تشغيل Django

### الأسبوع الأول (Sprint 1 - أيام 1-5)
- [ ] اليوم 1: إكمال البنية الأساسية
- [ ] اليوم 2: إعداد PostgreSQL و Redis
- [ ] اليوم 3: تحسين Client/Domain + Provisioning
- [ ] اليوم 4: نظام المصادقة (JWT)
- [ ] اليوم 5: Frontend الأساسي

### الأسبوع الثاني (Sprint 1 - أيام 6-10)
- [ ] اليوم 6-7: Django Ninja API
- [ ] اليوم 8-9: ربط Frontend بالـ Backend
- [ ] اليوم 10: اختبارات ومراجعة

---

## 🎯 الأولويات

### 🔴 حرج (يجب اليوم)
1. إصلاح خطأ Domain.__str__
2. إنشاء manage.py
3. إنشاء wsgi.py
4. إنشاء urls.py

### 🟡 مهم (هذا الأسبوع)
5. تحديث requirements.txt
6. إضافة Redis إلى Docker
7. إنشاء .env.example
8. إكمال settings.py

### 🟢 يمكن التأجيل (الأسبوع القادم)
9. Frontend
10. API Endpoints
11. Authentication

---

## 📚 الملفات المرجعية

- **الخطة الكاملة:** `AquaERP_Implementation_Plan.md`
- **تحليل الوضع الحالي:** `AquaERP_Current_State_Analysis.md`
- **خارطة الطريق الأصلية:** `AquaERP_Roadmap_Execution.md`

---

## ⚡ أوامر سريعة

### تشغيل المشروع
```bash
docker-compose up -d
docker-compose exec web python manage.py migrate_schemas
docker-compose exec web python manage.py createsuperuser
```

### إنشاء Tenant جديد
```bash
docker-compose exec web python manage.py create_tenant \
  --name "مزرعة تجريبية" \
  --domain "farm1" \
  --email "farm@example.com" \
  --admin-username "admin" \
  --admin-email "admin@example.com"
```

---

**ابدأ الآن! 🚀**

