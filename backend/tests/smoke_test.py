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
    print("Starting Production Readiness Smoke Test (Zero-Dependency)...")
    
    # 1. Test Auth Flow
    print("\n--- Testing Authentication ---")
    ts = int(time.time())
    test_user = f"smoke_user_{ts}"
    # Using a very strong password to satisfy zxcvbn and length requirements
    test_pass = "V3ryStr0ng!P@ssw0rd#2026"
    
    auth_data = {
        "username": test_user, 
        "password": test_pass, 
        "role": "user",
        "name": "Smoke Test User",
        "email": f"smoke_{ts}@gmail.com"
    }
    
    # Try registration first
    print(f"Registering test user: {test_user}...")
    reg_code, reg_resp = api_call("/auth/register", method="POST", data=auth_data)
    
    if reg_code in [201, 200]:
        print("OK: User Registered")
    elif reg_code == 400:
        msg = reg_resp.get("message", "") if isinstance(reg_resp, dict) else str(reg_resp)
        if "exists" in msg.lower():
            print("OK: User Already Exists")
        else:
            print(f"FAIL: Registration Validation Error (Status 400): {msg}")
            return
    else:
        print(f"FAIL: Registration Failed (Code {reg_code}): {reg_resp}")
        return

    print("Logging in...")
    code, resp = api_call("/auth/login", method="POST", data={"username": test_user, "password": test_pass})
    
    if code == 200:
        print("OK: Login Successful")
        token = resp["data"]["access_token"]
    else:
        msg = resp.get("message", "") if isinstance(resp, dict) else str(resp)
        print(f"FAIL: Login Failed (Code {code}): {msg}")
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
                    print(f"OK: {ep}: Structure Verified (Combined Object)")
                else:
                    print(f"FAIL: {ep}: Missing reports/claims keys")
            elif "items" in data and "pagination" in data:
                print(f"OK: {ep}: Structure Verified (Paginated List)")
            else:
                print(f"FAIL: {ep}: Missing pagination/items wrapper")
        else:
            print(f"FAIL: {ep} returned {code}")

    # 3. Test Validation Safeguards
    print("\n--- Testing Guardrails ---")
    bad_report = {"category": "Electronics"} # Missing many fields
    code, resp = api_call("/items/lost", method="POST", data=bad_report, headers=headers)
    
    if code == 400 or (isinstance(resp, dict) and resp.get("success") == False):
        print("OK: Validation Guardrail: Rejection Caught correctly (Status 400)")
    else:
        print(f"FAIL: Validation Guardrail: Failed to reject bad input (Status {code})")

    print("\nSmoke Test Completed.")

if __name__ == "__main__":
    run_smoke_test()
