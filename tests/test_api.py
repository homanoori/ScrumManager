from models import db, User


def get_token(client, username="alice", password="password123"):
    response = client.post("/api/auth/login", json={
        "username": username,
        "password": password,
    })
    return response.json["access_token"]


def test_login_returns_token(client, seeded_users):
    response = client.post("/api/auth/login", json={
        "username": "dev_user",
        "password": "devpass123",
    })
    assert response.status_code == 200
    assert "access_token" in response.json
    assert response.json["role"] == "developer"


def test_login_wrong_password(client, seeded_users):
    response = client.post("/api/auth/login", json={
        "username": "dev_user",
        "password": "wrongpassword",
    })
    assert response.status_code == 401


def test_get_pbis_without_token(client, seeded_users):
    response = client.get("/api/pbis/")
    assert response.status_code == 401


def test_get_pbis_with_token(client, seeded_users, app):
    token = get_token(client, "dev_user", "devpass123")
    response = client.get("/api/pbis/", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    assert isinstance(response.json, list)


def test_get_sprints_with_token(client, seeded_users):
    token = get_token(client, "dev_user", "devpass123")
    response = client.get("/api/sprints/", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200


def test_get_tasks_with_token(client, seeded_users):
    token = get_token(client, "dev_user", "devpass123")
    response = client.get("/api/tasks/", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200