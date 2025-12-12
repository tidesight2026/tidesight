"""
سكريبت اختبار سريع للنظام
"""
import requests
import json

BASE_URL = "http://farm1.localhost:8000/api"

def test_health():
    """اختبار Health Check"""
    print("🔍 اختبار Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/dashboard/health")
        if response.status_code == 200:
            print("✅ Health Check: OK")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health Check: Failed ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Health Check Error: {e}")
        return False

def test_login():
    """اختبار تسجيل الدخول"""
    print("\n🔍 اختبار Login...")
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
            print("✅ Login: OK")
            print(f"   Access Token: {data.get('access', '')[:20]}...")
            return data.get('access')
        else:
            print(f"❌ Login: Failed ({response.status_code})")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login Error: {e}")
        return None

def test_dashboard_stats(token):
    """اختبار Dashboard Stats"""
    print("\n🔍 اختبار Dashboard Stats...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/dashboard/stats", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("✅ Dashboard Stats: OK")
            print(f"   Total Ponds: {data.get('total_ponds', 0)}")
            print(f"   Active Batches: {data.get('active_batches', 0)}")
            print(f"   Total Biomass: {data.get('total_biomass', 0)}")
            return True
        else:
            print(f"❌ Dashboard Stats: Failed ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Dashboard Stats Error: {e}")
        return False

def test_endpoints(token):
    """اختبار Endpoints مختلفة"""
    print("\n🔍 اختبار Endpoints...")
    endpoints = [
        "/ponds",
        "/batches",
        "/inventory/feeds",
        "/inventory/medicines",
        "/operations/feeding",
        "/operations/mortality",
        "/accounting/accounts",
        "/accounting/journal-entries",
        "/sales/harvests",
        "/sales/sales-orders",
        "/sales/invoices",
    ]
    
    headers = {"Authorization": f"Bearer {token}"}
    success = 0
    failed = 0
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            if response.status_code in [200, 201]:
                print(f"✅ {endpoint}: OK")
                success += 1
            else:
                print(f"❌ {endpoint}: Failed ({response.status_code})")
                failed += 1
        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")
            failed += 1
    
    print(f"\n📊 النتيجة: {success} نجح، {failed} فشل")
    return success, failed

def main():
    print("=" * 60)
    print("🧪 AquaERP - Quick Test")
    print("=" * 60)
    
    # 1. Health Check
    if not test_health():
        print("\n❌ Health Check فشل. تحقق من أن Backend يعمل.")
        return
    
    # 2. Login
    token = test_login()
    if not token:
        print("\n❌ Login فشل. تحقق من بيانات المستخدم.")
        return
    
    # 3. Dashboard Stats
    test_dashboard_stats(token)
    
    # 4. Test Endpoints
    test_endpoints(token)
    
    print("\n" + "=" * 60)
    print("✅ الاختبارات اكتملت!")
    print("=" * 60)

if __name__ == "__main__":
    main()

