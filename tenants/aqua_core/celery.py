"""
Celery configuration for AquaERP
"""
import os
from celery import Celery

# تحديد إعدادات Django الافتراضية
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tenants.aqua_core.settings')

app = Celery('aqua_erp')

# تحميل الإعدادات من Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# اكتشاف المهام تلقائياً من جميع التطبيقات المثبتة
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

