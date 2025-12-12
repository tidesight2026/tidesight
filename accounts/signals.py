"""
Django Signals لإنشاء Groups الافتراضية عند Migration
"""
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction


@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    """
    إنشاء Groups الافتراضية بعد Migration
    يعمل لكل Tenant Schema منفصلة
    """
    # التحقق من أن هذا الـ app هو accounts
    if sender.name != 'accounts':
        return
    
    # تجنب التنفيذ المزدوج
    if hasattr(create_default_groups, '_executed'):
        return
    create_default_groups._executed = True
    
    with transaction.atomic():
        # 1. Group: Manager (مدير)
        manager_group, created = Group.objects.get_or_create(name='Manager')
        if created:
            # منح جميع الصلاحيات ما عدا حذف البيانات المالية الحساسة
            # نستخدم has_perm للتحقق من الصلاحيات في الكود
            manager_group.save()
            print("✅ تم إنشاء مجموعة 'Manager'")
        
        # 2. Group: Accountant (محاسب)
        accountant_group, created = Group.objects.get_or_create(name='Accountant')
        if created:
            # صلاحيات View, Add في المحاسبة والمبيعات
            # نحصل على ContentTypes للتطبيقات ذات الصلة
            try:
                # محاسبة
                accounting_ct = ContentType.objects.filter(app_label='accounting').first()
                if accounting_ct:
                    permissions = Permission.objects.filter(content_type=accounting_ct)
                    accountant_group.permissions.add(*permissions)
                
                # مبيعات
                sales_ct = ContentType.objects.filter(app_label='sales').first()
                if sales_ct:
                    view_perms = Permission.objects.filter(content_type=sales_ct, codename__startswith='view_')
                    add_perms = Permission.objects.filter(content_type=sales_ct, codename__startswith='add_')
                    accountant_group.permissions.add(*list(view_perms) + list(add_perms))
                
                accountant_group.save()
                print("✅ تم إنشاء مجموعة 'Accountant'")
            except Exception as e:
                print(f"⚠️ خطأ في إعداد صلاحيات Accountant: {e}")
        
        # 3. Group: Worker (عامل)
        worker_group, created = Group.objects.get_or_create(name='Worker')
        if created:
            # صلاحيات Add فقط في العمليات اليومية
            try:
                operations_ct = ContentType.objects.filter(app_label='daily_operations').first()
                if operations_ct:
                    add_perms = Permission.objects.filter(
                        content_type=operations_ct,
                        codename__in=['add_feedinglog', 'add_mortalitylog']
                    )
                    worker_group.permissions.add(*add_perms)
                
                worker_group.save()
                print("✅ تم إنشاء مجموعة 'Worker'")
            except Exception as e:
                print(f"⚠️ خطأ في إعداد صلاحيات Worker: {e}")
        
        # 4. Group: Viewer (مشاهد)
        viewer_group, created = Group.objects.get_or_create(name='Viewer')
        if created:
            # صلاحيات View فقط
            try:
                # جميع ContentTypes
                all_cts = ContentType.objects.filter(
                    app_label__in=['biological', 'inventory', 'daily_operations', 'accounting', 'sales']
                )
                for ct in all_cts:
                    view_perms = Permission.objects.filter(content_type=ct, codename__startswith='view_')
                    viewer_group.permissions.add(*view_perms)
                
                viewer_group.save()
                print("✅ تم إنشاء مجموعة 'Viewer'")
            except Exception as e:
                print(f"⚠️ خطأ في إعداد صلاحيات Viewer: {e}")

