"""
سكريبت اختبار شامل للميزات
"""
"""
سكريبت اختبار شامل للميزات - AquaERP
"""
import sys
import os

# محاولة استيراد requests
try:
    import requests
    import json
except ImportError:
    print("⚠️  requests غير مثبت. قم بتثبيته باستخدام:")
    print("   pip install requests")
    print("\nأو استخدم الاختبارات اليدوية من 🧪_TESTING_INSTRUCTIONS.md")
    sys.exit(1)

BASE_URL = "http://localhost:8000/api"

def test_health():
    """اختبار Health Check"""
    print("\n🔍 اختبار Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/dashboard/health")
        if response.status_code == 200:
            print("✅ Health Check: نجح")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health Check: فشل (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Health Check: خطأ - {str(e)}")
        return False

def test_login():
    """اختبار تسجيل الدخول"""
    print("\n🔍 اختبار تسجيل الدخول...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "username": "admin",
                "password": "Admin123!"
            }
        )
        if response.status_code == 200:
            data = response.json()
            token = data.get("access")
            print("✅ Login: نجح")
            print(f"   Token received: {token[:20]}...")
            return token
        else:
            print(f"❌ Login: فشل (Status: {response.status_code})")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login: خطأ - {str(e)}")
        return None

def test_authenticated_endpoint(token):
    """اختبار endpoint محمي"""
    print("\n🔍 اختبار Dashboard Stats...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/dashboard/stats", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("✅ Dashboard Stats: نجح")
            print(f"   Total Ponds: {data.get('total_ponds', 0)}")
            print(f"   Active Batches: {data.get('active_batches', 0)}")
            print(f"   Total Biomass: {data.get('total_biomass', 0)}")
            return True
        else:
            print(f"❌ Dashboard Stats: فشل (Status: {response.status_code})")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Dashboard Stats: خطأ - {str(e)}")
        return False

def test_species_list(token):
    """اختبار قائمة الأنواع"""
    print("\n🔍 اختبار قائمة الأنواع...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/species/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Species List: نجح ({len(data)} نوع)")
            return True
        else:
            print(f"❌ Species List: فشل (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Species List: خطأ - {str(e)}")
        return False

def test_batches_list(token):
    """اختبار قائمة الدفعات مع Pagination"""
    print("\n🔍 اختبار قائمة الدفعات (مع Pagination)...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/batches/",
            headers=headers,
            params={"page": 1, "page_size": 10}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Batches List: نجح ({len(data)} دفعة)")
            return True
        else:
            print(f"❌ Batches List: فشل (Status: {response.status_code})")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Batches List: خطأ - {str(e)}")
        return False

def test_accounts_list(token):
    """اختبار قائمة الحسابات"""
    print("\n🔍 اختبار قائمة الحسابات...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/accounting/accounts", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Accounts List: نجح ({len(data)} حساب)")
            return True
        elif response.status_code == 403:
            print("⚠️ Accounts List: لا توجد صلاحية (متوقع للـ non-accountant)")
            return None
        else:
            print(f"❌ Accounts List: فشل (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Accounts List: خطأ - {str(e)}")
        return False

def test_audit_logs(token):
    """اختبار سجلات التدقيق"""
    print("\n🔍 اختبار سجلات التدقيق...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/audit/logs", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Audit Logs: نجح ({len(data)} سجل)")
            return True
        elif response.status_code == 403:
            print("⚠️ Audit Logs: لا توجد صلاحية (يتطلب owner/manager)")
            return None
        else:
            print(f"❌ Audit Logs: فشل (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Audit Logs: خطأ - {str(e)}")
        return False

def main():
    """تشغيل جميع الاختبارات"""
    print("="*60)
    print("🧪 اختبار شامل للميزات - AquaERP")
    print("="*60)
    
    results = {
        "health": False,
        "login": False,
        "dashboard": False,
        "species": False,
        "batches": False,
        "accounts": None,
        "audit": None,
    }
    
    # 1. Health Check
    results["health"] = test_health()
    
    if not results["health"]:
        print("\n❌ Health Check فشل. تأكد من أن الخدمة تعمل.")
        return
    
    # 2. Login
    token = test_login()
    results["login"] = token is not None
    
    if not token:
        print("\n❌ Login فشل. لا يمكن المتابعة.")
        return
    
    # 3. Authenticated Endpoints
    results["dashboard"] = test_authenticated_endpoint(token)
    results["species"] = test_species_list(token)
    results["batches"] = test_batches_list(token)
    results["accounts"] = test_accounts_list(token)
    results["audit"] = test_audit_logs(token)
    
    # Summary
    print("\n" + "="*60)
    print("📊 ملخص النتائج:")
    print("="*60)
    for test_name, result in results.items():
        if result is True:
            print(f"✅ {test_name}: نجح")
        elif result is False:
            print(f"❌ {test_name}: فشل")
        elif result is None:
            print(f"⚠️ {test_name}: غير متاح (صلاحيات)")
    
    passed = sum(1 for r in results.values() if r is True)
    total = sum(1 for r in results.values() if r is not None)
    
    print(f"\n✅ النجاح: {passed}/{total}")
    print("="*60)

if __name__ == "__main__":
    main()

