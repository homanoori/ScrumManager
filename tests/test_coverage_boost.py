from models import db, PBI, Sprint, Task


def get_token(client):
    response = client.post("/api/auth/login", json={
        "username": "dev_user",
        "password": "devpass123",
    })
    return response.json["access_token"]


def test_stats_endpoint(client, seeded_users):
    token = get_token(client)
    response = client.get("/api/stats/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json
    assert "open_pbis" in data
    assert "tasks_done" in data
    assert "tasks_total" in data
    assert "effort_logged" in data
    assert "velocity" in data


def test_create_pbi_zero_effort(client, seeded_users):
    token = get_token(client)
    response = client.post("/api/pbis/", json={
        "title": "Zero effort PBI",
        "priority": "M",
        "effort": 0,
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400


def test_sprint_propose_no_capacity(client, seeded_users):
    token = get_token(client)
    response = client.post("/api/sprints/propose",
        json={"capacity": 0},
        headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400


def test_sprint_create_empty_pbi_ids(client, seeded_users):
    token = get_token(client)
    response = client.post("/api/sprints/create",
        json={"capacity": 10, "pbi_ids": []},
        headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400


def test_task_status_invalid(client, seeded_users, app):
    token = get_token(client)
    # First create a PBI and task to update
    with app.app_context():
        pbi = PBI(title="Test PBI", priority="H", effort=3, status="Incomplete")
        db.session.add(pbi)
        db.session.commit()
        task = Task(title="Test task", estimated_effort=2, pbi_id=pbi.id)
        db.session.add(task)
        db.session.commit()
        task_id = task.id
    response = client.post(f"/api/tasks/{task_id}/status",
        json={"status": "InvalidStatus"},
        headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400


def test_get_pbis_by_pbi(client, seeded_users):
    token = get_token(client)
    response = client.get("/api/tasks/by-pbi",
        headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200