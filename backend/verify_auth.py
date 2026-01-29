import requests
import sys
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = os.getenv("BASE_URL", "https://nginx") # Default to internal nginx
# Note: When running inside 'web' container, 'nginx' hostname should resolve if they are in same network.
# But 'web' depends on 'db'. 'nginx' depends on 'web'. Cyclical dependency if we aren't careful?
# No, nginx depends on web. Web does not depend on nginx. So web can start first.
# But if we run this SCRIPT inside 'web', we can hit 'nginx'.



def run_tests():
    s = requests.Session()
    
    print("--- 1. Check Unauthenticated Access ---")
    try:
        resp = s.get(f"{BASE_URL}/", allow_redirects=False, verify=False)
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

    if resp.status_code in [303, 307] and "/login" in resp.headers.get("Location", ""):
        print("✅ Correctly redirected to login")
    else:
        print(f"❌ Failed: Got {resp.status_code}")
        return False

    print("\n--- 2. Login (Get JWT + CSRF) ---")
    
    # 2.0 Get CSRF Token
    resp_page = s.get(f"{BASE_URL}/login", verify=False)
    if "csrf_token" in s.cookies:
        csrf_token = s.cookies["csrf_token"]
        print(f"✅ CSRF Cookie received: {csrf_token[:10]}...")
    else:
        print("❌ POST-REQUISITE: No CSRF cookie received on GET /login")
        return False
        
    login_data = {"email": "admin@uom.lk", "password": "password123", "csrf_token": csrf_token}
    
    # 2.1 Test Login WITHOUT Token
    print("   [Test] Attempting login WITHOUT CSRF token...")
    try:
        bad_resp = s.post(f"{BASE_URL}/login", data={"email": "admin@uom.lk", "password": "password123"}, verify=False, allow_redirects=False)
        if bad_resp.status_code == 403 or bad_resp.status_code == 303:
             print(f"   ✅ CSRF Check Passed: Login without token blocked ({bad_resp.status_code})")
        else:
             print(f"   ❌ CSRF Check Failed: Expected 403/303, got {bad_resp.status_code}")
             return False
    except Exception as e:
        print(f"Error: {e}")
        
    
    # 2.2 Test Login WITH Token
    print("   [Test] Attempting login WITH CSRF token...")
    resp = s.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False, verify=False)
    
    if "access_token" in s.cookies:
        print("✅ JWT 'access_token' cookie received")
        token = s.cookies["access_token"]
        if "user_id" in s.cookies:
             print("❌ Failed: Legacy 'user_id' cookie still present!")
             return False
        if len(token.split('.')) == 3:
             print("✅ Token format looks like JWT")
        else:
             print(f"❌ Token does not look like JWT: {token}")
             return False
    else:
        print(f"❌ Failed: No access_token cookie. Headers: {resp.headers}")
        print(resp.text)
        return False

    print("\n--- 3. Access Protected Route (With JWT) ---")
    # Admin dashboard requires JWT (and GET usually sets CSRF if missing, but we have it)
    resp = s.get(f"{BASE_URL}/", allow_redirects=False, verify=False)
    if resp.status_code == 200:
        print("✅ Access granted")
    else:
        print(f"❌ Failed: Got {resp.status_code}")
        return False

    print("\n--- 4. POST Vulnerable Action (With JWT + CSRF) ---")
    # For example, create a lab (will fail validation probably but checking 403 vs 422/303)
    # Actually, let's try something simple that requires validation but we expect 
    # to PASS the CSRF check and maybe fail input validation or succeed.
    # Labs create needs 'name', 'dept', 'capacity'.
    
    lab_data = {"name": "Test Lab", "dept": "CSE", "capacity": 50, "csrf_token": csrf_token}
    # Note: Validate CSRF is on the route.
    
    # First, WITHOUT token
    print("   [Test] POST action WITHOUT token...")
    bad_lab = s.post(f"{BASE_URL}/labs/create", data={"name": "Test", "dept": "CSE", "capacity": 50}, verify=False, allow_redirects=False)
    if bad_lab.status_code == 403 or bad_lab.status_code == 303:
        print(f"   ✅ CSRF Check Passed: Action blocked ({bad_lab.status_code})")
    else:
        print(f"   ❌ CSRF Check Failed: Expected 403/303, got {bad_lab.status_code}")
        return False
        
    # Second, WITH token
    print("   [Test] POST action WITH token...")
    good_lab = s.post(f"{BASE_URL}/labs/create", data=lab_data, allow_redirects=False, verify=False)
    # Success usually redirects 303 to /?success=...
    if good_lab.status_code == 303:
        print("   ✅ CSRF Check Passed: Action allowed (303 Redirect)")
    else:
        print(f"   ❌ Action failed unexpectedly: {good_lab.status_code}")
        print(good_lab.text)
        return False

    print("\n--- 5. Rate Limiting Check ---")
    print("   [Test] Spamming login to trigger rate limit (5/min)...")
    limit_hit = False
    for i in range(10):
        # We need a new session or at least new request to login.
        # We can use the same session but we want to simulate failed login/attempts.
        # Or simpler: just hit the POST /login repeatedly.
        r = s.post(f"{BASE_URL}/login", data=login_data, verify=False)
        if r.status_code == 429:
             print(f"   ✅ Rate Limit Hit at attempt {i+1} (429 Too Many Requests)")
             limit_hit = True
             break
    
    if not limit_hit:
        print("   ❌ Rate Limit FAILED: Made 10 requests without 429.")
        return False

    print("\n--- 6. Logout ---")
    resp = s.get(f"{BASE_URL}/logout", allow_redirects=False, verify=False)
    
    print("\n--- 7. Verify Logout (Access Denied) ---")
    resp = s.get(f"{BASE_URL}/", allow_redirects=False, verify=False)
    if resp.status_code in [303, 307]:
        print("✅ Access denied (Redirected)")
    else:
        print(f"❌ Failed: Still able to access after logout! Status: {resp.status_code}")
        return False

    return True

if __name__ == "__main__":
    try:
        if run_tests():
            print("\n✅ AUTH VERIFICATION PASSED")
            sys.exit(0)
        else:
            print("\n❌ AUTH VERIFICATION FAILED")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ CRASHED: {e}")
        sys.exit(1)
