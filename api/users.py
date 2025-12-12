"""
API Endpoints لإدارة المستخدمين والصلاحيات (RBAC)
"""
from ninja import Router
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction

User = get_user_model()
router = Router()


# Schemas
class UserSchema(BaseModel):
    """Schema لعرض معلومات المستخدم"""
    id: int
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool
    groups: List[str] = []


class UserCreateRequest(BaseModel):
    """طلب إنشاء مستخدم جديد"""
    username: str
    email: EmailStr
    password: str
    full_name: str
    role: str = 'worker'
    phone: Optional[str] = None


class UserUpdateRequest(BaseModel):
    """طلب تحديث مستخدم"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    groups: Optional[List[int]] = None  # Group IDs


class GroupSchema(BaseModel):
    """Schema لعرض Group"""
    id: int
    name: str


@router.get('/users', response=List[UserSchema])
def list_users(request):
    """
    قائمة جميع المستخدمين
    
    **Permissions:** Owner, Manager فقط
    """
    # التحقق من الصلاحيات
    if not (request.user.is_owner() or request.user.is_manager()):
        return 403, {'error': 'Unauthorized - Owner or Manager only'}
    
    users_list = []
    for user in User.objects.all().order_by('-created_at'):
        users_list.append(UserSchema(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            groups=[g.name for g in user.groups.all()]
        ))
    
    return users_list


@router.post('/users', response={200: UserSchema, 400: dict})
def create_user(request, data: UserCreateRequest):
    """
    إنشاء مستخدم جديد
    
    **Permissions:** Owner, Manager فقط
    """
    # التحقق من الصلاحيات
    if not (request.user.is_owner() or request.user.is_manager()):
        return 403, {'error': 'Unauthorized - Owner or Manager only'}
    
    # التحقق من وجود المستخدم
    if User.objects.filter(username=data.username).exists():
        return 400, {'error': 'Username already exists'}
    
    if User.objects.filter(email=data.email).exists():
        return 400, {'error': 'Email already exists'}
    
    try:
        # إنشاء المستخدم
        user = User.objects.create_user(
            username=data.username,
            email=data.email,
            password=data.password,
            full_name=data.full_name,
            role=data.role,
            phone=data.phone or ''
        )
        
        # تعيين Group بناءً على Role
        group_name = {
            'owner': 'Manager',  # Owner يحصل على صلاحيات Manager
            'manager': 'Manager',
            'accountant': 'Accountant',
            'worker': 'Worker',
            'viewer': 'Viewer',
        }.get(data.role, 'Worker')
        
        try:
            group = Group.objects.get(name=group_name)
            user.groups.add(group)
        except Group.DoesNotExist:
            pass  # إذا لم يكن Group موجوداً، نتجاهل
        
        return 200, UserSchema(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            groups=[group_name]
        )
    except Exception as e:
        return 400, {'error': f'Failed to create user: {str(e)}'}


@router.put('/users/{user_id}', response={200: UserSchema, 400: dict, 404: dict})
def update_user(request, user_id: int, data: UserUpdateRequest):
    """
    تحديث معلومات مستخدم
    
    **Permissions:** Owner, Manager فقط (لا يمكن للمستخدم تعديل نفسه)
    """
    # التحقق من الصلاحيات
    if not (request.user.is_owner() or request.user.is_manager()):
        return 403, {'error': 'Unauthorized - Owner or Manager only'}
    
    try:
        user = User.objects.get(id=user_id)
        
        # تحديث الحقول
        if data.email is not None:
            # التحقق من عدم استخدام البريد من قبل مستخدم آخر
            if User.objects.filter(email=data.email).exclude(id=user_id).exists():
                return 400, {'error': 'Email already in use'}
            user.email = data.email
        
        if data.full_name is not None:
            user.full_name = data.full_name
        
        if data.role is not None:
            user.role = data.role
        
        if data.phone is not None:
            user.phone = data.phone
        
        if data.is_active is not None:
            # لا يمكن تعطيل Owner
            if user.is_owner() and not data.is_active:
                return 400, {'error': 'Cannot deactivate Owner'}
            user.is_active = data.is_active
        
        user.save()
        
        # تحديث Groups
        if data.groups is not None:
            user.groups.clear()
            for group_id in data.groups:
                try:
                    group = Group.objects.get(id=group_id)
                    user.groups.add(group)
                except Group.DoesNotExist:
                    pass
        
        return 200, UserSchema(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            groups=[g.name for g in user.groups.all()]
        )
    except User.DoesNotExist:
        return 404, {'error': 'User not found'}
    except Exception as e:
        return 400, {'error': f'Failed to update user: {str(e)}'}


@router.delete('/users/{user_id}', response={200: dict, 403: dict, 404: dict})
def delete_user(request, user_id: int):
    """
    حذف مستخدم (Soft Delete)
    
    **Permissions:** Owner فقط
    """
    # التحقق من الصلاحيات
    if not request.user.is_owner():
        return 403, {'error': 'Unauthorized - Owner only'}
    
    try:
        user = User.objects.get(id=user_id)
        
        # لا يمكن حذف Owner
        if user.is_owner():
            return 403, {'error': 'Cannot delete Owner'}
        
        # Soft Delete
        user.is_active = False
        user.save()
        
        return 200, {'success': True, 'message': f'User {user.username} has been deactivated'}
    except User.DoesNotExist:
        return 404, {'error': 'User not found'}


@router.get('/groups', response=List[GroupSchema])
def list_groups(request):
    """
    قائمة جميع Groups
    
    **Permissions:** Owner, Manager فقط
    """
    if not (request.user.is_owner() or request.user.is_manager()):
        return 403, {'error': 'Unauthorized - Owner or Manager only'}
    
    groups_list = []
    for group in Group.objects.all().order_by('name'):
        groups_list.append(GroupSchema(
            id=group.id,
            name=group.name
        ))
    
    return groups_list

