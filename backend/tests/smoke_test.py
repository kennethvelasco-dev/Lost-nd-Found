import urllib.request
import urllib.parse
import json
import time

BASE_URL = "http://127.0.0.1:5000/api"

def api_call(path, method="GET", data=None, headers=None):
    url = f"{BASE_URL}{path}"
    req_headers = {"Content-Type": "application/json"}
    if headers: req_headers.update(headers)
    
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=req_headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            return response.getcode(), json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8"))
        except:
            return e.code, e.reason
    except Exception as e:
        return 0, str(e)

def run_smoke_test():
    print("🚀 Starting Production Readiness Smoke Test (Zero-Dependency)...")
    
    # 1. Test Auth Flow
    print("\n--- Testing Authentication ---")
    ts = int(time.time())
    test_user = f"smoke_user_{ts}"
    auth_data = {
        "username": test_user, 
        "password": "Password123!", 
        "role": "user",
        "name": "Smoke Test User",
        "email": f"smoke_{ts}@example.com"
    }
    
    # Try registration first
    print(f"Registering test user: {test_user}...")
    reg_code, reg_resp = api_call("/auth/register", method="POST", data=auth_data)
    if reg_code in [201, 200, 400]: # 400 if already exists
        print("✅ User Ready (Registered or Exists)")
    else:
        print(f"❌ Registration Failed (Code {reg_code}): {reg_resp}")

    print("Logging in...")
    code, resp = api_call("/auth/login", method="POST", data={"username": test_user, "password": "Password123!"})
    
    if code == 200:
        print("✅ Login Successful")
        token = resp["data"]["access_token"]
    else:
        print(f"❌ Login Failed (Code {code}): {resp}")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Test Fetch Arrays (The Crash Point Check)
    print("\n--- Testing Data Integrity (Listings) ---")
    endpoints = ["/items/lost", "/items/found", "/items/my-activities"]
    for ep in endpoints:
        code, resp = api_call(ep, headers=headers)
        if code == 200:
            data = resp.get("data", {})
            if ep == "/items/my-activities":
                if "reports" in data and "claims" in data:
                    print(f"✅ {ep}: Structure Verified (Combined Object)")
                else:
                    print(f"❌ {ep}: Missing reports/claims keys")
            else:
                if "items" in data and "pagination" in data:
                    print(f"✅ {ep}: Structure Verified (Paginated List)")
                else:
                    print(f"❌ {ep}: Missing pagination/items wrapper")
        else:
            print(f"❌ {ep} returned {code}")

    # 3. Test Validation Safeguards
    print("\n--- Testing Guardrails ---")
    bad_report = {"category": "Electronics"} # Missing many fields
    code, resp = api_call("/items/lost", method="POST", data=bad_report, headers=headers)
    
    if code == 400 or (isinstance(resp, dict) and resp.get("success") == False):
        print("✅ Validation Guardrail: Rejection Caught correctly (Status 400)")
    else:
        print(f"❌ Validation Guardrail: Failed to reject bad input (Status {code})")

    print("\n✨ Smoke Test Completed.")

if __name__ == "__main__":
    run_smoke_test()
