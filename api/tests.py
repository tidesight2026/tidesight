"""
Integration Tests للـ API
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from decimal import Decimal

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.api
class TestAuthenticationAPI:
    """اختبارات API المصادقة"""
    
    def test_login_success(self, client):
        """اختبار تسجيل دخول ناجح"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            full_name='Test User',
            role='worker'
        )
        
        response = client.post(
            '/api/auth/login',
            {
                'username': 'testuser',
                'password': 'testpass123'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'access' in data
        assert 'refresh' in data
        assert 'user' in data
        assert data['user']['username'] == 'testuser'
    
    def test_login_failure(self, client):
        """اختبار فشل تسجيل الدخول"""
        response = client.post(
            '/api/auth/login',
            {
                'username': 'wronguser',
                'password': 'wrongpass'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 401
    
    def test_get_user_info(self, client):
        """اختبار الحصول على معلومات المستخدم"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            full_name='Test User',
            role='worker'
        )
        
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        response = client.get(
            '/api/auth/me',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['username'] == 'testuser'
        assert data['full_name'] == 'Test User'


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.api
class TestSpeciesAPI:
    """اختبارات API الأنواع السمكية"""
    
    def test_list_species(self, client):
        """اختبار قائمة الأنواع"""
        user = User.objects.create_user(
            username='testuser',
            password='pass123',
            full_name='Test User'
        )
        
        from biological.models import Species
        Species.objects.create(
            arabic_name='سمك البلطي',
            english_name='Tilapia'
        )
        
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        response = client.get(
            '/api/species/',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
    
    def test_create_species(self, client):
        """اختبار إنشاء نوع جديد"""
        user = User.objects.create_user(
            username='testuser',
            password='pass123',
            full_name='Test User',
            role='manager'
        )
        
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        response = client.post(
            '/api/species/',
            {
                'arabic_name': 'سمك السلمون',
                'english_name': 'Salmon',
                'scientific_name': 'Salmo salar'
            },
            HTTP_AUTHORIZATION=f'Bearer {access_token}',
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['arabic_name'] == 'سمك السلمون'


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.api
class TestPondAPI:
    """اختبارات API الأحواض"""
    
    def test_list_ponds(self, client):
        """اختبار قائمة الأحواض"""
        user = User.objects.create_user(
            username='testuser',
            password='pass123',
            full_name='Test User'
        )
        
        from biological.models import Pond
        Pond.objects.create(
            name='حوض 1',
            pond_type='concrete',
            capacity=Decimal('1000.00')
        )
        
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        response = client.get(
            '/api/ponds/',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1


@pytest.mark.django_db
@pytest.mark.integration
@pytest.mark.api
@pytest.mark.tenant
class TestMultiTenantAPI:
    """اختبارات Multi-tenant للـ API"""
    
    def test_tenant_isolation(self, client):
        """اختبار عزل البيانات بين Tenants"""
        # هذا يتطلب إعداد Tenant محدد
        # سيتطلب إعدادات إضافية للاختبارات
        pass

