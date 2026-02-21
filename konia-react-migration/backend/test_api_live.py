import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_live_api():
    print(f"Testing Live API at {BASE_URL}...")
    
    # 1. Test Root
    try:
        r = requests.get(f"{BASE_URL}/")
        if r.status_code == 200:
            print("✅ API Root is accessible")
        else:
            print(f"❌ API Root failed: {r.status_code}")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Is uvicorn running?")
        sys.exit(1)

    # 2. Test Trazabilidad (Public/Protected?)
    # The endpoint is protected, so we expect 401, but that confirms the route exists.
    # To truly test the module loading, we need a valid token or a mock user.
    # For this verification step, getting a 401 is better than 404.
    
    r = requests.get(f"{BASE_URL}/api/dashboard/trazabilidad/test-uuid")
    if r.status_code == 401:
        print("✅ Trazabilidad endpoint exists and is protected (401)")
    elif r.status_code == 404:
        print("❌ Trazabilidad endpoint not found (404)")
        sys.exit(1)
    else:
        print(f"⚠️ Unexpected status for Trazabilidad: {r.status_code}")

    print("Live API verification passed (Infrastructure level).")

if __name__ == "__main__":
    test_live_api()
