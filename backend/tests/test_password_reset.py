import sqlite3
import urllib.request
import urllib.parse
import json
import time

BASE_URL = "http://127.0.0.1:5000/api"
DB_PATH = "lostnfound.db"

def api_call(path, method="GET", data=None):
    url = f"{BASE_URL}{path}"
    req_headers = {"Content-Type": "application/json"}
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

def get_reset_token(email):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT reset_token FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def test_password_reset():
    print("Testing Password Reset Flow...")
    
    # 1. Register a user
    ts = int(time.time())
    email = f"reset_test_{ts}@gmail.com"
    user_data = {
        "username": f"user_{ts}",
        "password": "V3ryStr0ng!P@ssw0rd#2026",
        "role": "user",
        "name": "Reset Tester",
        "email": email
    }
    
    print("Registering user...")
    code, resp = api_call("/auth/register", "POST", user_data)
    if code not in [200, 201]:
        print(f"FAIL: Registration failed ({code}): {resp}")
        return

    # 2. Request reset
    print("Requesting password reset...")
    code, resp = api_call("/auth/forgot-password", "POST", {"email": email})
    if code != 200:
        print(f"FAIL: Forgot password request failed ({code}): {resp}")
        return

    # 3. Extract token from DB (Simulating reading email)
    token = get_reset_token(email)
    if not token:
        print("FAIL: Reset token not found in database")
        return
    print(f"Extracted reset token: {token[:10]}...")

    # 4. Reset password
    new_pass = "N3wStr0ng!P@ssw0rd#999"
    print("Resetting password with new one...")
    code, resp = api_call("/auth/reset-password", "POST", {"token": token, "new_password": new_pass})
    if code != 200:
        print(f"FAIL: Reset password failed ({code}): {resp}")
        return
    print("OK: Password reset successfully")

    # 5. Try login with new password
    print("Attempting login with new password...")
    code, resp = api_call("/auth/login", "POST", {"username": user_data["username"], "password": new_pass})
    if code == 200:
        print("OK: Login with new password successful")
    else:
        print(f"FAIL: Login with new password failed ({code}): {resp}")

if __name__ == "__main__":
    test_password_reset()
