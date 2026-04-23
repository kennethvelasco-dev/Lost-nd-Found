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


def test_post_found_item_user(client, app):
    # Setup: Register user
    user_data = {
        "username": "itemuser",
        "password": "Password123!",
        "name": "Item User",
        "email": "item@test.com",
        "role": "user",
    }
    resp = client.post("/api/auth/register", json=user_data)
    assert resp.status_code == 201
    headers = get_auth_headers(client, "itemuser", "Password123!")

    found_item = {
        "category": "Electronics",
        "item_type": "Phone",
        "found_location": "Cafeteria",
        "found_datetime": datetime.now(timezone.utc).isoformat(),
        "brand": "Apple",
        "color": "White",
        "public_description": "White iPhone found on table",
    }
    response = client.post("/api/items/found", json=found_item, headers=headers)
    assert response.status_code == 201
    assert "item_id" in response.get_json()["data"]


def test_search_and_pagination(client, app):
    # Setup: Register admin and post multiple items
    admin_data = {
        "username": "adminuser",
        "password": "Password123!",
        "name": "Admin",
        "email": "admin@test.com",
        "role": "admin",
        "admin_id": "ADM-001",
    }
    resp = client.post("/api/auth/register", json=admin_data)
    assert resp.status_code == 201
    headers = get_auth_headers(client, "adminuser", "Password123!")

    # Post 5 items
    for i in range(5):
        item = {
            "category": "Books",
            "item_type": f"Book {i}",
            "found_location": "Library",
            "found_datetime": datetime.now(timezone.utc).isoformat(),
            "public_description": f"Book number {i}",
        }
        resp = client.post("/api/admin/items/found", json=item, headers=headers)
        assert resp.status_code == 201

    # Test Pagination: Limit 2
    response = client.get("/api/items/found?limit=2", headers=headers)
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert len(data["items"]) == 2
    assert data["pagination"]["total"] >= 5
    assert data["pagination"]["limit"] == 2

    # Test Search
    response = client.get("/api/items/search?category=Books&limit=10", headers=headers)
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert len(data["items"]) >= 5
    assert all(item["category"] == "Books" for item in data["items"])
