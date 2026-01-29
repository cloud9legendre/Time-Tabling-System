# Simple smoke test script
import requests, sys

BASE_URL = "http://localhost:8000"

def test_health():
    try:
        r = requests.get(f"{BASE_URL}/health")
        if r.status_code == 200:
            print("✅ Health Check Passed")
        else:
            print("❌ Health Check Failed")
            sys.exit(1)
    except:
        print("❌ Service unreachable")
        sys.exit(1)

if __name__ == "__main__":
    test_health()
