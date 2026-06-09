def _login_admin(client):
    response = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "admin12345"})
    assert response.status_code == 200
    return response.json()["access_token"]


def _login_user(client):
    client.post("/api/auth/register", json={"username": "user1", "email": "user1@example.com", "password": "strongpass123"})
    response = client.post("/api/auth/login", json={"email": "user1@example.com", "password": "strongpass123"})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_user_cannot_access_admin_panel(client):
    token = _login_user(client)
    response = client.get("/api/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_admin_can_manage_sources(client):
    token = _login_admin(client)
    response = client.post(
        "/api/admin/sources",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Test RSS", "url": "https://example.com/rss", "type": "rss", "is_active": True},
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Test RSS"
