"""
Admin interface لسجلات التدقيق
"""
from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin interface لـ AuditLog"""
    
    list_display = [
        'id',
        'action_type',
        'entity_type',
        'entity_description',
        'user',
        'user_ip',
        'created_at',
    ]
    
    list_filter = [
        'action_type',
        'entity_type',
        'created_at',
        'user',
    ]
    
    search_fields = [
        'entity_description',
        'description',
        'user__username',
        'user__full_name',
        'user_ip',
    ]
    
    readonly_fields = [
        'action_type',
        'entity_type',
        'entity_id',
        'entity_description',
        'user',
        'user_ip',
        'user_agent',
        'old_values',
        'new_values',
        'description',
        'notes',
        'created_at',
    ]
    
    date_hierarchy = 'created_at'
    
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        """لا يمكن إضافة سجلات يدوياً"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """لا يمكن تعديل سجلات التدقيق"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """لا يمكن حذف سجلات التدقيق (مهمة للأمان)"""
        return False

