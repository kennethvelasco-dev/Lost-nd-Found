import pytest
from datetime import datetime, timezone


def get_auth_headers(client, username, password):
    resp = client.post(
        "/api/auth/login", json={"username": username, "password": password}
    )
    assert (
        resp.status_code == 200
    ), f"Login failed for {username}: {resp.get_data(as_text=True)}"
    data = resp.get_json()["data"]
    token = data.get("access_token")
    return {"Authorization": f"Bearer {token}"}


def test_full_claim_lifecycle(client, app):
    # 1. Setup: Register Admin and User
    admin_data = {
        "username": "admin8",
        "password": "Password123!",
        "name": "Admin 8",
        "email": "admin8@test.com",
        "role": "admin",
        "admin_id": "ADM-008",
    }
    user_data = {
        "username": "user8",
        "password": "Password123!",
        "name": "User 8",
        "email": "user8@test.com",
        "role": "user",
    }
    resp1 = client.post("/api/auth/register", json=admin_data)
    assert (
        resp1.status_code == 201
    ), f"Admin registration failed: {resp1.get_data(as_text=True)}"
    resp2 = client.post("/api/auth/register", json=user_data)
    assert (
        resp2.status_code == 201
    ), f"User registration failed: {resp2.get_data(as_text=True)}"

    admin_headers = get_auth_headers(client, "admin8", "Password123!")
    user_headers = get_auth_headers(client, "user8", "Password123!")

    # 2. Admin reports found item
    found_item = {
        "category": "Electronics",
        "item_type": "Phone",
        "brand": "Apple",
        "color": "Silver",
        "found_location": "Cafeteria",
        "found_datetime": datetime.now(timezone.utc).isoformat(),
        "public_description": "Silver iPhone found.",
    }
    resp = client.post("/api/admin/items/found", json=found_item, headers=admin_headers)
    assert resp.status_code == 201
    found_item_id = resp.get_json()["data"]["item_id"]

    # 3. User submits claim (general report)
    claim_payload = {
        "category": "Electronics",
        "item_type": "Phone",
        "brand": "Apple",
        "color": "Silver",
        "location": "Cafeteria",
        "datetime": datetime.now(timezone.utc).isoformat(),
        "description": "Lost my silver phone.",
        "declared_value": "500",
        "receipt_proof": "Attached",
    }
    resp = client.post("/api/claims/submit", json=claim_payload, headers=user_headers)
    assert resp.status_code == 201
    claim_id = resp.get_json()["data"]["claim_id"]

    # 4. Fetch matches and link
    resp = client.get(f"/api/claims/{claim_id}/potential-matches", headers=user_headers)
    assert resp.status_code == 200
    matches = resp.get_json()["data"]["matches"]
    assert any(m["id"] == found_item_id for m in matches)

    resp = client.post(
        f"/api/claims/{claim_id}/link",
        json={"found_item_id": found_item_id},
        headers=user_headers,
    )
    assert resp.status_code == 200

    # 5. Admin Approve and Schedule
    resp = client.post(
        f"/api/claims/{claim_id}/verify",
        json={"decision": "approved"},
        headers=admin_headers,
    )
    assert resp.status_code == 200

    schedule_payload = {
        "pickup_datetime": "2026-03-20T10:00:00",
        "pickup_location": "Main Hall",
    }
    resp = client.post(
        f"/api/claims/{claim_id}/schedule", json=schedule_payload, headers=admin_headers
    )
    assert resp.status_code == 200

    # 6. Verify Status
    resp = client.get("/api/claims/pending", headers=user_headers)
    assert resp.status_code == 200
    user_claims = resp.get_json()["data"]
    my_claim = next(c for c in user_claims if c["claim_id"] == claim_id)
    assert my_claim["status"] == "approved"
