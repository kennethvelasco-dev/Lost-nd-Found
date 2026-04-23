import pytest


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


def test_idor_prevention(client, app):
    # Setup: 2 users, user1 reports, user2 claims
    u1 = {
        "username": "s_user1",
        "password": "Password123!",
        "name": "U1",
        "email": "s1@test.com",
        "role": "user",
    }
    u2 = {
        "username": "s_user2",
        "password": "Password123!",
        "name": "U2",
        "email": "s2@test.com",
        "role": "user",
    }

    resp1 = client.post("/api/auth/register", json=u1)
    assert resp1.status_code == 201
    resp2 = client.post("/api/auth/register", json=u2)
    assert resp2.status_code == 201

    h1 = get_auth_headers(client, "s_user1", "Password123!")
    h2 = get_auth_headers(client, "s_user2", "Password123!")

    # User 1 reports
    item = {
        "category": "Tools",
        "item_type": "Hammer",
        "found_location": "Yard",
        "found_datetime": "2026-03-10T10:00:00",
        "public_description": "Hammer",
    }
    resp = client.post("/api/items/found", json=item, headers=h1)
    assert resp.status_code == 201
    item_id = resp.get_json()["data"]["item_id"]

    # User 2 submits claim (general report)
    # Using the standardized claim submit structure
    claim = {
        "found_item_id": item_id,
        "claimant_name": "U2",
        "claimant_email": "s2@test.com",
        "description": "Mine",
        "declared_value": "10",
        "receipt_proof": "N/A",
    }
    resp = client.post("/api/claims/submit", json=claim, headers=h2)
    assert resp.status_code == 201
    claim_id = resp.get_json()["data"]["claim_id"]

    # IDOR: User 1 tries to access User 2's potential matches
    resp = client.get(f"/api/claims/{claim_id}/potential-matches", headers=h1)
    assert resp.status_code == 403


def test_concurrency_double_approval(client, app):
    # Setup: Admin, 2 claims for 1 item
    admin = {
        "username": "s_admin",
        "password": "Password123!",
        "name": "Admin",
        "email": "sa@test.com",
        "role": "admin",
        "admin_id": "ADM-SEC",
    }
    resp_adm = client.post("/api/auth/register", json=admin)
    assert resp_adm.status_code == 201
    ha = get_auth_headers(client, "s_admin", "Password123!")

    # Create item
    item = {
        "category": "Tools",
        "item_type": "Drill",
        "found_location": "Yard",
        "found_datetime": "2026-03-10T10:00:00",
        "public_description": "Drill",
    }
    resp = client.post("/api/admin/items/found", json=item, headers=ha)
    assert resp.status_code == 201
    item_id = resp.get_json()["data"]["item_id"]

    # 2 different users claim
    claim_ids = []
    for i in range(3, 5):
        u = {
            "username": f"s_user{i}",
            "password": "Password123!",
            "name": f"U{i}",
            "email": f"s{i}@test.com",
            "role": "user",
        }
        resp_reg = client.post("/api/auth/register", json=u)
        assert resp_reg.status_code == 201
        h = get_auth_headers(client, f"s_user{i}", "Password123!")
        claim = {
            "found_item_id": item_id,
            "claimant_name": f"U{i}",
            "claimant_email": f"s{i}@test.com",
            "description": f"Mine {i}",
            "declared_value": "10",
            "receipt_proof": "N/A",
        }
        resp_claim = client.post("/api/claims/submit", json=claim, headers=h)
        assert resp_claim.status_code == 201
        claim_ids.append(resp_claim.get_json()["data"]["claim_id"])

    # Approve first
    c1 = claim_ids[0]
    c2 = claim_ids[1]

    resp_app1 = client.post(
        f"/api/claims/{c1}/verify", json={"decision": "approved"}, headers=ha
    )
    assert resp_app1.status_code == 200

    # Try to approve second
    resp_app2 = client.post(
        f"/api/claims/{c2}/verify", json={"decision": "approved"}, headers=ha
    )
    assert resp_app2.status_code == 400
    assert "Another claim is already approved" in resp_app2.get_json()["message"]
