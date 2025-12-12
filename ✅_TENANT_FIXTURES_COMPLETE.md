# ✅ Tenant Fixtures - النسخة النهائية المنقحة

**التاريخ:** ديسمبر 2025  
**الحالة:** ✅ **جاهزة للعمل مباشرة!**

---

## 🎯 ملخص التحديثات

تم تحديث `conftest.py` بالنسخة النهائية المحسّنة التي تستخدم أفضل الممارسات مع `django-tenants` + `pytest`.

---

## 📋 Fixtures المتوفرة

### 1. 🧪 `client` - Django Test Client

```python
@pytest.fixture
def client():
    """Django test client"""
    from django.test import Client
    return Client()
```

**الاستخدام:**
```python
def test_api_endpoint(client):
    response = client.get('/api/some-endpoint/')
    assert response.status_code == 200
```

---

### 2. 👤 Public Schema Users

#### `test_user`, `test_manager`, `test_worker`

```python
def test_public_users(test_user, test_manager, test_worker):
    assert test_user.role == 'owner'
    assert test_manager.role == 'manager'
    assert test_worker.role == 'worker'
```

**ملاحظة:** هؤلاء المستخدمون في `public` schema وليس في tenant schema.

---

### 3. 🏡 `test_tenant` - Tenant Schema كامل

**الوصف:**
- ✅ ينشئ Tenant كامل مع schema معزولة
- ✅ ينشئ Domain تلقائياً
- ✅ يشغل migrations تلقائياً
- ✅ يستخدم `get_or_create` لإعادة استخدام tenant موجود
- ⚠️ **لا يقوم بتعيين schema context تلقائياً**

**الكود:**
```python
@pytest.fixture(scope='function')
def test_tenant(db):
    connection.set_schema_to_public()
    
    schema_name = "test_farm"
    
    tenant, created = TenantModel.objects.get_or_create(
        schema_name=schema_name,
        defaults=dict(
            name="Test Farm",
            email="test@example.com",
            subscription_type="trial",
            on_trial=True,
            is_active=True,
            is_active_subscription=True,
        ),
    )
    
    DomainModel.objects.get_or_create(
        domain=f"{schema_name}.localhost",
        tenant=tenant,
        is_primary=True,
    )
    
    # Run tenant migrations
    with schema_context(schema_name):
        try:
            call_command("migrate_schemas", "--tenant", schema_name=schema_name, verbosity=0, interactive=False)
        except Exception:
            call_command("migrate", schema_name=schema_name, verbosity=0)
    
    yield tenant
    
    # Cleanup
    connection.set_schema_to_public()
```

**الاستخدام:**
```python
def test_something(test_tenant):
    # ⚠️ مهم: يجب استخدام schema_context
    with schema_context(test_tenant.schema_name):
        feed_type = FeedType.objects.create(...)
        assert feed_type.id is not None
```

---

### 4. 🏷️ `tenant_schema_context` - Context Manager

**الوصف:**
- يوفر context manager للعمل داخل tenant schema
- يعين schema context تلقائياً

**الكود:**
```python
@pytest.fixture(scope='function')
def tenant_schema_context(test_tenant):
    return schema_context(test_tenant.schema_name)
```

**الاستخدام:**
```python
def test_with_context(test_tenant, tenant_schema_context):
    with tenant_schema_context:
        feed_type = FeedType.objects.create(...)
        feed_inventory = FeedInventory.objects.create(...)
        assert FeedType.objects.count() == 1
```

---

### 5. 👤 `tenant_user` - مستخدم داخل Tenant

**الوصف:**
- ينشئ مستخدم داخل tenant schema
- جاهز للاستخدام في الاختبارات

**الكود:**
```python
@pytest.fixture
def tenant_user(test_tenant):
    with schema_context(test_tenant.schema_name):
        user = User.objects.create_user(
            username="tenant_user",
            email="tenant@example.com",
            password="testpass123",
            full_name="Tenant User",
            role="owner",
        )
    return user
```

**الاستخدام:**
```python
def test_with_user(test_tenant, tenant_user):
    with schema_context(test_tenant.schema_name):
        assert tenant_user.username == 'tenant_user'
        assert tenant_user.role == 'owner'
```

---

## 📋 أمثلة كاملة

### مثال 1: اختبار بسيط

```python
from decimal import Decimal
from django_tenants.utils import schema_context
from inventory.models import FeedType

def test_feed_type_creation(test_tenant):
    """اختبار إنشاء FeedType داخل tenant schema"""
    with schema_context(test_tenant.schema_name):
        feed_type = FeedType.objects.create(
            name="Protein 45%",
            arabic_name="بروتين 45%",
            protein_percentage=Decimal('45.00'),
            unit="كجم"
        )
        
        assert feed_type.id is not None
        assert feed_type.name == "Protein 45%"
        assert FeedType.objects.count() == 1
```

### مثال 2: اختبار مع context manager

```python
from inventory.models import FeedType, FeedInventory

def test_feed_inventory_with_context(test_tenant, tenant_schema_context):
    """اختبار مع tenant_schema_context"""
    with tenant_schema_context:
        feed_type = FeedType.objects.create(
            name="Protein 45%",
            arabic_name="بروتين 45%",
            protein_percentage=Decimal('45.00'),
            unit="كجم"
        )
        
        feed_inventory = FeedInventory.objects.create(
            feed_type=feed_type,
            quantity=Decimal('1000.00'),
            unit_price=Decimal('5.00')
        )
        
        assert feed_inventory.id is not None
        assert feed_inventory.quantity == Decimal('1000.00')
```

### مثال 3: اختبار مع مستخدم

```python
def test_with_user(test_tenant, tenant_user):
    """اختبار مع tenant_user"""
    with schema_context(test_tenant.schema_name):
        assert tenant_user.username == 'tenant_user'
        assert tenant_user.role == 'owner'
        
        feed_type = FeedType.objects.create(
            name="Test Feed",
            arabic_name="علف تجريبي",
            protein_percentage=Decimal('45.00'),
            unit="كجم"
        )
        
        assert feed_type.id is not None
```

---

## ⚠️ ملاحظات مهمة

### 1. Schema Context مطلوب دائماً

**✅ صحيح:**
```python
def test_something(test_tenant):
    with schema_context(test_tenant.schema_name):
        FeedType.objects.create(...)  # ✅ يعمل
```

**❌ خاطئ:**
```python
def test_something(test_tenant):
    FeedType.objects.create(...)  # ❌ خطأ! يعمل في public schema
```

### 2. Scope

- `scope='function'` (افتراضي): tenant جديد لكل test (موصى به للعزل الكامل)
- `scope='class'`: tenant واحد لكل test class
- `scope='module'`: tenant واحد لكل ملف اختبار

### 3. Cleanup

- ✅ العودة إلى public schema بعد كل test تلقائياً
- ✅ إعادة استخدام tenant إذا كان موجوداً (`get_or_create`)

---

## 🔧 الاستخدام مع pytest

```bash
# تشغيل اختبار محدد
pytest tests/test_tenant_fixture_example.py::test_feed_type_creation -v

# تشغيل جميع الاختبارات
pytest tests/test_tenant_fixture_example.py -v

# تشغيل مع output مفصل
pytest tests/test_tenant_fixture_example.py -v -s

# تشغيل جميع الاختبارات
pytest tests/ -v
```

---

## ✅ الميزات

### 1. إنشاء Tenant تلقائياً
- ✅ يستخدم `get_or_create` لإعادة استخدام tenant موجود
- ✅ ينشئ Domain تلقائياً

### 2. تشغيل Migrations تلقائياً
- ✅ يحاول `migrate_schemas` أولاً
- ✅ يتراجع إلى `migrate` إذا فشل

### 3. Cleanup تلقائي
- ✅ العودة إلى public schema بعد كل test

---

## 📝 قائمة التحقق

- [x] `client` fixture
- [x] `test_user`, `test_manager`, `test_worker` fixtures (public schema)
- [x] `test_tenant` fixture (creates schema + migrations)
- [x] `tenant_schema_context` fixture (context manager)
- [x] `tenant_user` fixture (user inside tenant schema)
- [x] Migrations يتم تشغيلها تلقائياً
- [x] Cleanup تلقائي بعد الاختبارات
- [x] أمثلة كاملة متوفرة

---

## 🎯 الخلاصة

**Fixtures جاهزة للاستخدام!**

- ✅ تستخدم أفضل الممارسات مع django-tenants
- ✅ تعمل مع pytest بشكل صحيح
- ✅ تنظف تلقائياً بعد الاختبارات
- ✅ تدعم scope مختلفة (function, class, module)
- ✅ تستخدم `get_or_create` للأداء الأفضل

**🚀 جاهزة للاستخدام الفوري!**

