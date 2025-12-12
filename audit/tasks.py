"""
Celery Tasks لتطبيق Audit Logging
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

from .models import AuditLog

logger = logging.getLogger(__name__)


@shared_task(name='audit.cleanup_old_logs')
def cleanup_old_audit_logs(retention_months=12, batch_size=1000):
    """
    حذف/أرشفة سجلات التدقيق الأقدم من فترة الاحتفاظ المحددة
    
    **Parameters:**
    - retention_months: عدد الأشهر للاحتفاظ بالسجلات (افتراضي: 12 شهر)
    - batch_size: عدد السجلات للحذف في كل دفعة (افتراضي: 1000)
    
    **Returns:**
    - dict: إحصائيات العملية (عدد السجلات المحذوفة، المدة المستغرقة)
    """
    start_time = timezone.now()
    
    # حساب تاريخ القطع (أقدم من هذا التاريخ سيتم حذفه)
    cutoff_date = timezone.now() - timedelta(days=retention_months * 30)
    
    logger.info(
        f"بدء تنظيف سجلات التدقيق الأقدم من {cutoff_date.strftime('%Y-%m-%d')} "
        f"(الاحتفاظ بآخر {retention_months} شهر)"
    )
    
    # حساب عدد السجلات المراد حذفها
    total_to_delete = AuditLog.objects.filter(created_at__lt=cutoff_date).count()
    
    if total_to_delete == 0:
        logger.info("لا توجد سجلات قديمة للحذف")
        return {
            'deleted_count': 0,
            'cutoff_date': cutoff_date.isoformat(),
            'duration_seconds': 0,
            'status': 'no_records_to_delete'
        }
    
    logger.info(f"تم العثور على {total_to_delete} سجل قديم للحذف")
    
    # حذف السجلات على دفعات لتجنب الضغط على قاعدة البيانات
    deleted_count = 0
    while True:
        # جلب دفعة من السجلات القديمة
        old_logs = AuditLog.objects.filter(
            created_at__lt=cutoff_date
        ).order_by('created_at')[:batch_size]
        
        if not old_logs.exists():
            break
        
        # حذف الدفعة
        batch_ids = list(old_logs.values_list('id', flat=True))
        deleted_batch = AuditLog.objects.filter(id__in=batch_ids).delete()[0]
        deleted_count += deleted_batch
        
        logger.info(
            f"تم حذف {deleted_batch} سجل "
            f"(إجمالي: {deleted_count}/{total_to_delete})"
        )
    
    duration = (timezone.now() - start_time).total_seconds()
    
    logger.info(
        f"اكتمل تنظيف سجلات التدقيق: تم حذف {deleted_count} سجل "
        f"خلال {duration:.2f} ثانية"
    )
    
    return {
        'deleted_count': deleted_count,
        'total_found': total_to_delete,
        'cutoff_date': cutoff_date.isoformat(),
        'retention_months': retention_months,
        'duration_seconds': round(duration, 2),
        'status': 'success'
    }


@shared_task(name='audit.archive_old_logs')
def archive_old_audit_logs(retention_months=12, archive_table_name='audit_auditlog_archive'):
    """
    أرشفة سجلات التدقيق القديمة (بدلاً من حذفها)
    
    **ملاحظة:** هذه الدالة تتطلب إنشاء جدول أرشيف مسبقاً
    يمكن استخدامها كبديل للحذف إذا كان هناك متطلبات قانونية للاحتفاظ بالسجلات
    
    **Parameters:**
    - retention_months: عدد الأشهر للاحتفاظ بالسجلات النشطة
    - archive_table_name: اسم جدول الأرشيف
    
    **Returns:**
    - dict: إحصائيات العملية
    """
    # TODO: تنفيذ منطق الأرشفة عند الحاجة
    # يمكن استخدام django-archive أو إنشاء جدول أرشيف يدوياً
    
    logger.warning(
        "أرشفة سجلات التدقيق غير مُنفذة حالياً. "
        "استخدم cleanup_old_audit_logs للحذف المباشر."
    )
    
    return {
        'status': 'not_implemented',
        'message': 'الأرشفة غير مُنفذة حالياً'
    }

