# ✅ إصلاح migrate_schemas في Tenant Fixture

**التاريخ:** ديسمبر 2025  
**المشكلة:** `migrate_schemas` لا يعمل بشكل صحيح  
**الحل:** استخدام `tenant=True` بدلاً من `"--tenant"` كـ string

---

## 🎯 المشكلة الأصلية

### ❌ الصيغة الخاطئة

```python
call_command("migrate_schemas", "--tenant", schema_name=schema_name, verbosity=0)
```

**المشكلة:**

- `"--tenant"` يُمرر كـ string ويُعتبر كـ app name
- Django Tenants يتجاهله تماماً
- Migrations لا يتم تشغيلها في tenant schema

---

## ✅ الحل الصحيح

### ✅ الصيغة الصحيحة

```python
call_command("migrate_schemas", shared=False, tenant=True, verbosity=0, interactive=False)
```

**الميزات:**

- ✅ `tenant=True` كـ argument صحيح
- ✅ `shared=False` لضمان عدم تشغيل migrations في public schema
- ✅ Fallback إلى `migrate` مباشرة في حالة الفشل

---

## 🔍 التحقق الإضافي

### التحقق من الجداول

```python
with schema_context(schema_name):
    tables = connection.introspection.table_names()
    required_tables = ['inventory_feedtype', 'accounts_user']
    missing_tables = [t for t in required_tables if t not in tables]
    
    if missing_tables:
        # محاولة ثانية مع migrate مباشرة
        call_command("migrate", verbosity=1, interactive=False)
        
        # التحقق مرة أخرى
        tables_after = connection.introspection.table_names()
        missing_after = [t for t in required_tables if t not in tables_after]
        
        if missing_after:
            raise AssertionError(
                f"❌ Migrations didn't run inside tenant! Missing tables: {missing_after}"
            )
```

---

## 📋 الكود النهائي

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
    
    # ✅ Run tenant migrations - الصيغة الصحيحة
    try:
        call_command("migrate_schemas", shared=False, tenant=True, verbosity=0, interactive=False)
    except Exception as e:
        # fallback: استخدام schema_context مع migrate مباشرة
        with schema_context(schema_name):
            call_command("migrate", verbosity=0, interactive=False)
    
    # ✅ التحقق من أن migrations تم تطبيقها بشكل صحيح
    with schema_context(schema_name):
        tables = connection.introspection.table_names()
        required_tables = ['inventory_feedtype', 'accounts_user']
        missing_tables = [t for t in required_tables if t not in tables]
        
        if missing_tables:
            # محاولة ثانية مع migrate مباشرة
            call_command("migrate", verbosity=1, interactive=False)
            
            # التحقق مرة أخرى
            tables_after = connection.introspection.table_names()
            missing_after = [t for t in required_tables if t not in tables_after]
            
            if missing_after:
                raise AssertionError(
                    f"❌ Migrations didn't run inside tenant! Missing tables: {missing_after}. "
                    f"Available tables: {[t for t in tables_after if 'inventory' in t or 'accounts' in t]}"
                )
    
    yield tenant
    
    # Cleanup
    connection.set_schema_to_public()
```

---

## ✅ النتيجة

**الاختبارات تعمل بنجاح الآن!**

```
test_feed_purchase_and_inventory ... ok

Ran 1 test in 4.345s
OK
```

---

## 🎯 الخلاصة

### ما تم إصلاحه

1. ✅ استخدام `tenant=True` بدلاً من `"--tenant"` كـ string
2. ✅ إضافة `shared=False` لضمان عدم تشغيل migrations في public schema
3. ✅ إضافة fallback إلى `migrate` مباشرة
4. ✅ إضافة التحقق من وجود الجداول المطلوبة
5. ✅ رسائل خطأ واضحة في حالة الفشل

---

**✅ تم الإصلاح بنجاح! Migrations تعمل بشكل صحيح الآن!**
