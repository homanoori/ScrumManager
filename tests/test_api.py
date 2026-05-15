from models import db, PBI, Sprint, Task


def get_token(client, username="dev_user", password="devpass123"):
    response = client.post("/api/auth/login", json={
        "username": username,
        "password": password,
    })
    return response.json["access_token"]


# --- Auth tests ---
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


def test_login_missing_fields(client, seeded_users):
    response = client.post("/api/auth/login", json={"username": "dev_user"})
    assert response.status_code == 400


# --- PBI tests ---
def test_get_pbis_without_token(client, seeded_users):
    response = client.get("/api/pbis/")
    assert response.status_code == 401


def test_get_pbis_with_token(client, seeded_users):
    token = get_token(client)
    response = client.get("/api/pbis/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "pbis" in response.json
    assert "total" in response.json
    assert "page" in response.json


def test_get_pbis_pagination(client, seeded_users):
    token = get_token(client)
    response = client.get("/api/pbis/?page=1&per_page=2", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json["pbis"]) <= 2


def test_create_pbi(client, seeded_users, app):
    token = get_token(client)
    response = client.post("/api/pbis/", json={
        "title": "New API PBI",
        "priority": "H",
        "effort": 5.0,
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    assert response.json["title"] == "New API PBI"


def test_create_pbi_missing_title(client, seeded_users):
    token = get_token(client)
    response = client.post("/api/pbis/", json={
        "priority": "H",
        "effort": 5.0,
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400


def test_create_pbi_invalid_priority(client, seeded_users):
    token = get_token(client)
    response = client.post("/api/pbis/", json={
        "title": "Bad PBI",
        "priority": "X",
        "effort": 5.0,
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400


def test_get_pbi_not_found(client, seeded_users):
    token = get_token(client)
    response = client.get("/api/pbis/99999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404


# --- Sprint tests ---
def test_get_sprints_with_token(client, seeded_users):
    token = get_token(client)
    response = client.get("/api/sprints/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "sprints" in response.json


def test_get_sprint_not_found(client, seeded_users):
    token = get_token(client)
    response = client.get("/api/sprints/99999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404


# --- Task tests ---
def test_get_tasks_with_token(client, seeded_users):
    token = get_token(client)
    response = client.get("/api/tasks/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "tasks" in response.json


def test_get_task_not_found(client, seeded_users):
    token = get_token(client)
    response = client.get("/api/tasks/99999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404