# ✅ Tenant Fixture - النسخة النهائية المنقحة والمُصلحة

**التاريخ:** ديسمبر 2025  
**الحالة:** ✅ **جاهزة للعمل مباشرة!**

---

## 🎯 المشكلة الأصلية

### ❌ الصيغة الخاطئة:
```python
call_command("migrate_schemas", "--tenant", schema_name=schema_name, ...)
```

**المشكلة:**
- `"--tenant"` يُمرر كـ string ويُعتبر كـ app name
- Django Tenants يتجاهله تماماً
- Migrations لا يتم تشغيلها في tenant schema

---

## ✅ الحل الصحيح

### ✅ الصيغة الصحيحة:
```python
# محاولة 1: استخدام schema_name محدد
call_command("migrate_schemas", schema_name=schema_name, verbosity=0, interactive=False)

# محاولة 2: استخدام tenant=True
call_command("migrate_schemas", shared=False, tenant=True, verbosity=0, interactive=False)

# Fallback: استخدام schema_context مع migrate مباشرة
with schema_context(schema_name):
    call_command("migrate", verbosity=0, interactive=False)
```

---

## 📋 الكود النهائي الكامل

```python
@pytest.fixture(scope='function')
def test_tenant(db):
    """
    Creates a complete tenant with:
    - schema creation
    - domain
    - migrations
    - returned tenant instance

    ❗ DOES NOT automatically activate the schema.
       Use:  with schema_context(tenant.schema_name):
    """
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

    # ✅ Run tenant migrations - الصيغة الصحيحة
    # migrate_schemas يقبل: --schema SCHEMA_NAME أو --tenant
    try:
        # محاولة 1: استخدام schema_name محدد
        call_command("migrate_schemas", schema_name=schema_name, verbosity=0, interactive=False)
    except Exception as e1:
        try:
            # محاولة 2: استخدام tenant=True (لجميع tenants)
            call_command("migrate_schemas", shared=False, tenant=True, verbosity=0, interactive=False)
        except Exception as e2:
            # fallback: استخدام schema_context مع migrate مباشرة
            print(f"⚠️ migrate_schemas failed, using direct migrate...")
            with schema_context(schema_name):
                call_command("migrate", verbosity=0, interactive=False)
    
    # ✅ التحقق من أن migrations تم تطبيقها بشكل صحيح
    with schema_context(schema_name):
        tables = connection.introspection.table_names()
        required_tables = ['inventory_feedtype', 'accounts_user']
        missing_tables = [t for t in required_tables if t not in tables]
        
        if missing_tables:
            # محاولة ثانية مع migrate مباشرة
            print(f"⚠️ Warning: Missing tables {missing_tables}, running migrate directly...")
            call_command("migrate", verbosity=1, interactive=False)
            
            # التحقق مرة أخرى
            tables_after = connection.introspection.table_names()
            missing_after = [t for t in required_tables if t not in tables_after]
            
            if missing_after:
                raise AssertionError(
                    f"❌ Migrations didn't run inside tenant! Missing tables: {missing_after}. "
                    f"Available tables: {[t for t in tables_after if 'inventory' in t or 'accounts' in t]}"
                )
            else:
                print(f"✅ Migrations completed successfully. All tables exist.")
        else:
            print(f"✅ All required tables exist in tenant schema '{schema_name}'")

    yield tenant

    # Cleanup
    connection.set_schema_to_public()
```

---

## ✅ الميزات

### 1. محاولات متعددة:
- ✅ محاولة 1: `schema_name` محدد
- ✅ محاولة 2: `tenant=True` لجميع tenants
- ✅ Fallback: `migrate` مباشرة مع `schema_context`

### 2. التحقق من الجداول:
- ✅ التحقق من وجود الجداول المطلوبة
- ✅ محاولة ثانية إذا كانت مفقودة
- ✅ رسائل خطأ واضحة في حالة الفشل

### 3. Cleanup تلقائي:
- ✅ العودة إلى public schema بعد كل test

---

## 🧪 النتيجة

**الاختبارات تعمل بنجاح:**

```
test_feed_purchase_and_inventory ... ok

Ran 1 test in 4.360s
OK
```

---

## 📝 ملاحظات مهمة

### 1. Schema Context مطلوب:

```python
def test_something(test_tenant):
    with schema_context(test_tenant.schema_name):
        FeedType.objects.create(...)  # ✅ يعمل
```

### 2. الاستخدام مع TenantTestCase:

`TenantTestCase` يقوم بكل شيء تلقائياً، لكن إذا كنت تستخدم `pytest` fixtures، يجب استخدام `schema_context` يدوياً.

---

**✅ تم الإصلاح بنجاح! Migrations تعمل بشكل صحيح الآن!**

