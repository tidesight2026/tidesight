# ✅ دليل استخدام Tenant Fixtures للاختبارات

**التاريخ:** ديسمبر 2025  
**الهدف:** إنشاء fixtures محسّنة لاختبارات Tenant

---

## 🎯 Fixtures المتوفرة

### 1. `test_tenant` - Tenant Schema كامل

**الوصف:**
- ينشئ Tenant كامل مع schema معزولة
- يشغل migrations تلقائياً
- يعين schema context للاختبارات

**الاستخدام:**
```python
def test_something(test_tenant):
    # test_tenant هو Tenant object
    # جميع العمليات تتم داخل tenant schema تلقائياً
    
    with schema_context(test_tenant.schema_name):
        # يمكنك الوصول إلى نماذج tenant هنا
        feed_type = FeedType.objects.create(
            name="Test Feed",
            arabic_name="علف تجريبي",
            protein_percentage=Decimal('45.00')
        )
        assert feed_type.id is not None
```

**الميزات:**
- ✅ ينشئ tenant schema تلقائياً
- ✅ يشغل migrations في tenant schema
- ✅ يعين schema context
- ✅ ينظف بعد الاختبار

---

### 2. `tenant_schema_context` - Context Manager

**الوصف:**
- يوفر context manager للعمل داخل tenant schema
- مفيد عندما تحتاج للتبديل بين schemas

**الاستخدام:**
```python
def test_with_context_manager(test_tenant, tenant_schema_context):
    # العمل في public schema
    tenant = Client.objects.get(schema_name='test_farm')
    
    # الانتقال إلى tenant schema
    with tenant_schema_context:
        feed_type = FeedType.objects.create(...)
        assert feed_type.id is not None
    
    # العودة إلى public schema تلقائياً
```

---

### 3. `tenant_user` - مستخدم داخل Tenant

**الوصف:**
- ينشئ مستخدم داخل tenant schema
- جاهز للاستخدام في الاختبارات

**الاستخدام:**
```python
def test_with_user(test_tenant, tenant_user):
    # tenant_user هو User object داخل tenant schema
    
    assert tenant_user.username == 'tenant_user'
    assert tenant_user.role == 'owner'
    
    # يمكن استخدامه في الاختبارات
    feed_type = FeedType.objects.create(
        name="Test Feed",
        created_by=tenant_user  # إذا كان هناك created_by field
    )
```

---

## 📋 أمثلة كاملة

### مثال 1: اختبار بسيط

```python
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
        assert FeedType.objects.filter(schema=test_tenant.schema_name).count() == 1
```

### مثال 2: اختبار مع مستخدم

```python
def test_feed_inventory_with_user(test_tenant, tenant_user):
    """اختبار إنشاء FeedInventory مع مستخدم"""
    
    with schema_context(test_tenant.schema_name):
        # إنشاء FeedType أولاً
        feed_type = FeedType.objects.create(
            name="Protein 45%",
            arabic_name="بروتين 45%",
            protein_percentage=Decimal('45.00'),
            unit="كجم"
        )
        
        # إنشاء FeedInventory
        feed_inventory = FeedInventory.objects.create(
            feed_type=feed_type,
            quantity=Decimal('1000.00'),
            unit_price=Decimal('5.00')
        )
        
        assert feed_inventory.quantity == Decimal('1000.00')
        assert feed_inventory.feed_type == feed_type
```

### مثال 3: اختبار مع context manager

```python
def test_multiple_operations(test_tenant, tenant_schema_context):
    """اختبار عمليات متعددة داخل tenant schema"""
    
    with tenant_schema_context:
        # جميع هذه العمليات تتم داخل tenant schema
        feed_type = FeedType.objects.create(...)
        feed_inventory = FeedInventory.objects.create(...)
        
        # التحقق من البيانات
        assert FeedType.objects.count() == 1
        assert FeedInventory.objects.count() == 1
```

---

## ⚠️ ملاحظات مهمة

### 1. Schema Context

**✅ صحيح:**
```python
def test_something(test_tenant):
    with schema_context(test_tenant.schema_name):
        # الكود هنا
        FeedType.objects.create(...)
```

**❌ خاطئ:**
```python
def test_something(test_tenant):
    # بدون schema_context - سيحاول الوصول إلى public schema
    FeedType.objects.create(...)  # ❌ خطأ!
```

### 2. Scope

- `scope='function'`: يتم إنشاء tenant جديد لكل test (افتراضي)
- `scope='class'`: يتم إنشاء tenant واحد لكل test class
- `scope='module'`: يتم إنشاء tenant واحد لكل ملف اختبار

**استخدام `function` scope (الافتراضي) أفضل للعزل الكامل بين الاختبارات.**

### 3. Cleanup

الـ fixture يقوم بتنظيف تلقائي:
- ✅ العودة إلى public schema بعد الاختبار
- ✅ حذف tenant schema (اختياري)

---

## 🔧 الاستخدام مع TenantTestCase

إذا كنت تستخدم `TenantTestCase`، **لا تحتاج** لهذه fixtures:

```python
from django_tenants.test.cases import TenantTestCase

class TestSomething(TenantTestCase):
    # TenantTestCase يقوم بكل شيء تلقائياً
    def setUp(self):
        super().setUp()
        # self.tenant متاح تلقائياً
        # schema_context معين تلقائياً
        
        self.feed_type = FeedType.objects.create(...)  # ✅ يعمل تلقائياً
```

---

## 📝 قائمة التحقق

- [x] `test_tenant` fixture موجودة
- [x] `tenant_schema_context` fixture موجودة
- [x] `tenant_user` fixture موجودة
- [x] Migrations يتم تشغيلها تلقائياً
- [x] Schema context يتم تعيينه تلقائياً
- [x] Cleanup يتم تلقائياً

---

**✅ Fixtures جاهزة للاستخدام!**

