def test_protected_endpoint_requires_token(client):
    response = client.get("/api/admin/users")
    assert response.status_code == 401


def test_register_validates_password_length(client):
    response = client.post("/api/auth/register", json={"username": "bad", "email": "bad@example.com", "password": "123"})
    assert response.status_code == 422
