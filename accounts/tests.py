"""
Unit Tests للمستخدمين
"""
import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.unit
class TestUserModel:
    """اختبارات نموذج المستخدم"""
    
    def test_create_user(self):
        """اختبار إنشاء مستخدم جديد"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            full_name='Test User',
            role='worker'
        )
        
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.full_name == 'Test User'
        assert user.role == 'worker'
        assert user.is_active is True
        assert user.check_password('testpass123')
    
    def test_create_superuser(self):
        """اختبار إنشاء superuser"""
        user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            full_name='Admin User'
        )
        
        assert user.is_superuser is True
        assert user.is_staff is True
    
    def test_user_str(self):
        """اختبار __str__ method"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            full_name='Test User'
        )
        
        assert str(user) == 'Test User (testuser)'
    
    def test_user_role_methods(self):
        """اختبار methods للدور"""
        owner = User.objects.create_user(
            username='owner',
            password='pass123',
            full_name='Owner',
            role='owner'
        )
        manager = User.objects.create_user(
            username='manager',
            password='pass123',
            full_name='Manager',
            role='manager'
        )
        worker = User.objects.create_user(
            username='worker',
            password='pass123',
            full_name='Worker',
            role='worker'
        )
        
        assert owner.is_owner() is True
        assert manager.is_manager() is True
        assert owner.is_manager() is True
        assert worker.is_manager() is False
        assert owner.can_edit_financial() is True
        assert manager.can_edit_financial() is True
        assert worker.can_edit_financial() is False
    
    def test_user_get_full_name(self):
        """اختبار get_full_name method"""
        user = User.objects.create_user(
            username='testuser',
            password='pass123',
            full_name='Test User'
        )
        
        assert user.get_full_name() == 'Test User'
        
        # إذا لم يكن هناك full_name
        user2 = User.objects.create_user(
            username='testuser2',
            password='pass123'
        )
        user2.full_name = ''
        assert user2.get_full_name() == 'testuser2'
