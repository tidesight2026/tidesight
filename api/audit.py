"""
API Endpoints لسجلات التدقيق
"""
from ninja import Router
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

from .auth import TokenAuth, ErrorResponse
from .permissions import check_feature_permission
from audit.models import AuditLog

router = Router()


# ==================== Schemas ====================

class AuditLogSchema(BaseModel):
    """Schema لعرض سجل تدقيق"""
    id: int
    action_type: str
    action_type_display: str
    entity_type: str
    entity_type_display: str
    entity_id: Optional[int]
    entity_description: Optional[str]
    user_id: Optional[int]
    user_name: Optional[str]
    user_ip: Optional[str]
    old_values: Optional[dict]
    new_values: Optional[dict]
    description: Optional[str]
    notes: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


# ==================== Endpoints ====================

@router.get('/logs', response={200: List[AuditLogSchema]}, auth=TokenAuth())
def list_audit_logs(
    request,
    action_type: Optional[str] = None,
    entity_type: Optional[str] = None,
    user_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
):
    """
    قائمة سجلات التدقيق - يتطلب صلاحية owner أو manager
    
    **Parameters:**
    - action_type: تصفية حسب نوع العملية
    - entity_type: تصفية حسب نوع الكيان
    - user_id: تصفية حسب المستخدم
    - start_date: تاريخ البداية (YYYY-MM-DD)
    - end_date: تاريخ النهاية (YYYY-MM-DD)
    - limit: عدد السجلات (افتراضي: 100)
    """
    # فقط owner و manager يمكنهم الوصول
    if not request.auth:
        return 401, ErrorResponse(detail="غير مصرح - يرجى تسجيل الدخول")
    
    user_role = getattr(request.auth, 'role', None)
    if user_role not in ['owner', 'manager']:
        return 403, ErrorResponse(detail="ليس لديك صلاحية للوصول إلى سجلات التدقيق")
    
    queryset = AuditLog.objects.select_related('user').all()
    
    # Filters
    if action_type:
        queryset = queryset.filter(action_type=action_type)
    if entity_type:
        queryset = queryset.filter(entity_type=entity_type)
    if user_id:
        queryset = queryset.filter(user_id=user_id)
    if start_date:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        queryset = queryset.filter(created_at__gte=start_date_obj)
    if end_date:
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        queryset = queryset.filter(created_at__lte=end_date_obj)
    
    # Limit and order
    logs = queryset.order_by('-created_at')[:limit]
    
    return [
        AuditLogSchema(
            id=log.id,
            action_type=log.action_type,
            action_type_display=log.get_action_type_display(),
            entity_type=log.entity_type,
            entity_type_display=log.get_entity_type_display(),
            entity_id=log.entity_id,
            entity_description=log.entity_description,
            user_id=log.user.id if log.user else None,
            user_name=log.user.full_name if log.user else None,
            user_ip=str(log.user_ip) if log.user_ip else None,
            old_values=log.old_values,
            new_values=log.new_values,
            description=log.description,
            notes=log.notes,
            created_at=log.created_at.isoformat(),
        )
        for log in logs
    ]


@router.get('/logs/{log_id}', response={200: AuditLogSchema, 404: ErrorResponse}, auth=TokenAuth())
def get_audit_log(request, log_id: int):
    """الحصول على سجل تدقيق محدد - يتطلب صلاحية owner أو manager"""
    # فقط owner و manager يمكنهم الوصول
    if not request.auth:
        return 401, ErrorResponse(detail="غير مصرح - يرجى تسجيل الدخول")
    
    user_role = getattr(request.auth, 'role', None)
    if user_role not in ['owner', 'manager']:
        return 403, ErrorResponse(detail="ليس لديك صلاحية للوصول إلى سجلات التدقيق")
    
    try:
        log = AuditLog.objects.select_related('user').get(id=log_id)
        
        return AuditLogSchema(
            id=log.id,
            action_type=log.action_type,
            action_type_display=log.get_action_type_display(),
            entity_type=log.entity_type,
            entity_type_display=log.get_entity_type_display(),
            entity_id=log.entity_id,
            entity_description=log.entity_description,
            user_id=log.user.id if log.user else None,
            user_name=log.user.full_name if log.user else None,
            user_ip=str(log.user_ip) if log.user_ip else None,
            old_values=log.old_values,
            new_values=log.new_values,
            description=log.description,
            notes=log.notes,
            created_at=log.created_at.isoformat(),
        )
    except AuditLog.DoesNotExist:
        return 404, ErrorResponse(detail="سجل التدقيق غير موجود")

