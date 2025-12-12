"""
Audit Logging Utilities
أدوات مساعدة لتسجيل العمليات الحساسة
"""
from typing import Optional, Dict, Any
from .models import AuditLog


def log_action(
    action_type: str,
    entity_type: str,
    user,
    entity_id: Optional[int] = None,
    entity_description: Optional[str] = None,
    old_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None,
    description: Optional[str] = None,
    user_ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    notes: Optional[str] = None,
    request=None,
):
    """
    تسجيل عملية في سجل التدقيق
    
    Args:
        action_type: نوع العملية (create, update, delete, etc.)
        entity_type: نوع الكيان (account, journal_entry, etc.)
        user: المستخدم الذي قام بالعملية
        entity_id: معرف الكيان (اختياري)
        entity_description: وصف الكيان (اختياري)
        old_values: القيم القديمة (اختياري)
        new_values: القيم الجديدة (اختياري)
        description: وصف العملية (اختياري)
        user_ip: عنوان IP للمستخدم (اختياري)
        user_agent: User Agent (اختياري)
        notes: ملاحظات إضافية (اختياري)
    """
    # جلب IP و User Agent من request إذا لم يتم تحديدهما
    if request and not user_ip:
        user_ip = get_client_ip(request)
    if request and not user_agent:
        user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    try:
        AuditLog.objects.create(
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_description=entity_description,
            user=user,
            old_values=old_values,
            new_values=new_values,
            description=description,
            user_ip=user_ip,
            user_agent=user_agent,
            notes=notes,
        )
    except Exception as e:
        # لا نريد أن تفشل العمليات بسبب مشاكل في Audit Logging
        # يمكن إضافة logging هنا للتسجيل في ملف log
        import logging
        logger = logging.getLogger('audit')
        logger.error(f"فشل في تسجيل Audit Log: {str(e)}")


def log_financial_transaction(
    action_type: str,
    entity_type: str,
    entity_id: int,
    entity_description: str,
    user,
    amount: Optional[float] = None,
    account_code: Optional[str] = None,
    old_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None,
    description: Optional[str] = None,
    request=None,
):
    """
    تسجيل معاملة مالية في سجل التدقيق
    
    Args:
        action_type: نوع العملية
        entity_type: نوع الكيان
        entity_id: معرف الكيان
        entity_description: وصف الكيان
        user: المستخدم
        amount: المبلغ (اختياري)
        account_code: كود الحساب (اختياري)
        old_values: القيم القديمة
        new_values: القيم الجديدة
        description: وصف العملية
        request: Django request object (لجلب IP و User Agent)
    """
    user_ip = None
    user_agent = None
    
    if request:
        user_ip = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    notes = None
    if amount:
        notes = f"المبلغ: {amount} ريال"
        if account_code:
            notes += f" | الحساب: {account_code}"
    
    log_action(
        action_type=action_type,
        entity_type=entity_type,
        entity_id=entity_id,
        entity_description=entity_description,
        user=user,
        old_values=old_values,
        new_values=new_values,
        description=description,
        user_ip=user_ip,
        user_agent=user_agent,
        notes=notes,
    )


def get_client_ip(request):
    """الحصول على عنوان IP الحقيقي للعميل"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

