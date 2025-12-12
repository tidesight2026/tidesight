"""
Quota Service - للتحقق من القيود (Quotas) قبل تنفيذ العمليات
"""
from typing import Tuple
from django.core.exceptions import PermissionDenied


class QuotaService:
    """خدمة للتحقق من القيود (Quotas)"""
    
    @staticmethod
    def check_quota(tenant, quota_type: str, current_count: int) -> Tuple[bool, str]:
        """
        التحقق من القيد
        
        Args:
            tenant: Client object
            quota_type: نوع القيد (مثال: 'max_ponds', 'max_users')
            current_count: العدد الحالي المستخدم
        
        Returns:
            Tuple[bool, str]: (مسموح, رسالة الخطأ)
        """
        # الحصول على الاشتراك
        subscription = getattr(tenant, 'subscription', None)
        if not subscription:
            return False, "لا يوجد اشتراك نشط"
        
        # التحقق من حالة الاشتراك
        if not subscription.is_valid():
            return False, "الاشتراك غير نشط أو منتهي الصلاحية"
        
        # الحصول على الباقة
        plan = subscription.plan
        if not plan:
            return False, "لا توجد باقة مرتبطة"
        
        # الحصول على الحد الأقصى من القيود
        max_allowed = plan.quotas.get(quota_type)
        
        # إذا كان None، يعني لا محدود
        if max_allowed is None:
            return True, ""
        
        # التحقق من القيد
        if current_count >= max_allowed:
            return False, (
                f"لقد تجاوزت حد الباقة الحالية ({max_allowed} {quota_type}). "
                f"يرجى الترقية إلى باقة أعلى."
            )
        
        return True, ""
    
    @staticmethod
    def check_feature(tenant, feature: str) -> Tuple[bool, str]:
        """
        التحقق من توفر الميزة
        
        Args:
            tenant: Client object
            feature: اسم الميزة (مثال: 'reports', 'accounting', 'zatca')
        
        Returns:
            Tuple[bool, str]: (متاحة, رسالة الخطأ)
        """
        subscription = getattr(tenant, 'subscription', None)
        if not subscription:
            return False, "لا يوجد اشتراك نشط"
        
        if not subscription.is_valid():
            return False, "الاشتراك غير نشط أو منتهي الصلاحية"
        
        plan = subscription.plan
        if not plan:
            return False, "لا توجد باقة مرتبطة"
        
        # التحقق من الميزة
        feature_enabled = plan.features.get(feature, False)
        
        if not feature_enabled:
            return False, (
                f"الميزة '{feature}' غير متاحة في باقاتك الحالية. "
                f"يرجى الترقية إلى باقة أعلى."
            )
        
        return True, ""

