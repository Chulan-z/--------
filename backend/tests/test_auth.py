from app.models.log import Log


def test_register_login_refresh_and_me(client):
    response = client.post(
        "/api/auth/register",
        json={"username": "student", "email": "student@example.com", "password": "strongpass123"},
    )
    assert response.status_code == 201
    tokens = response.json()
    assert tokens["access_token"]
    assert tokens["refresh_token"]

    login = client.post("/api/auth/login", json={"email": "student@example.com", "password": "strongpass123"})
    assert login.status_code == 200
    access = login.json()["access_token"]

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {access}"})
    assert me.status_code == 200
    assert me.json()["email"] == "student@example.com"

    refreshed = client.post("/api/auth/refresh", json={"refresh_token": login.json()["refresh_token"]})
    assert refreshed.status_code == 200
    assert refreshed.json()["access_token"] != access


def test_invalid_login_is_logged(client, db_session):
    response = client.post("/api/auth/login", json={"email": "missing@example.com", "password": "wrongpass123"})
    assert response.status_code == 401
    assert db_session.query(Log).filter(Log.action == "login_failed").count() == 1
