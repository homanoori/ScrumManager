from models import db, PBI, Sprint, Task


def login(client, username, password):
    return client.post("/auth/login", data={
        "username": username,
        "password": password,
    })


# ── Backlog (atena_routes) ──────────────────────────────────────────────────

def test_backlog_page_loads(client, seeded_users):
    login(client, "dev_user", "devpass123")
    response = client.get("/backlog")
    assert response.status_code == 200


def test_add_pbi(client, seeded_users, app):
    login(client, "dev_user", "devpass123")
    response = client.post("/backlog/add", data={
        "title": "Test PBI",
        "priority": "H",
        "effort": "5",
    }, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        pbi = PBI.query.filter_by(title="Test PBI").first()
        assert pbi is not None
        assert pbi.priority == "H"
        assert pbi.effort == 5.0


def test_client_cannot_add_pbi(client, seeded_users, app):
    login(client, "client_user", "clientpass123")
    client.post("/backlog/add", data={
        "title": "Should Not Exist",
        "priority": "H",
        "effort": "3",
    }, follow_redirects=True)
    with app.app_context():
        pbi = PBI.query.filter_by(title="Should Not Exist").first()
        assert pbi is None


# ── Sprint (homa_routes) ────────────────────────────────────────────────────

def test_sprint_page_loads(client, seeded_users):
    login(client, "dev_user", "devpass123")
    response = client.get("/sprint")
    assert response.status_code == 200


def test_create_sprint(client, seeded_users, app):
    login(client, "dev_user", "devpass123")
    # First add a PBI to assign to the sprint
    with app.app_context():
        pbi = PBI(title="Sprint PBI", priority="H", effort=5.0, status="Incomplete")
        db.session.add(pbi)
        db.session.commit()
        pbi_id = pbi.id

    response = client.post("/sprint/create", data={
        "capacity": "10",
        "pbi_ids": str(pbi_id),
    }, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        sprint = Sprint.query.first()
        assert sprint is not None
        assert sprint.capacity == 10.0


# ── Tasks (setayesh_routes) ─────────────────────────────────────────────────

def test_update_task_status(client, seeded_users, app):
    login(client, "dev_user", "devpass123")
    with app.app_context():
        pbi = PBI(title="Task PBI", priority="M", effort=3.0, status="Incomplete")
        db.session.add(pbi)
        db.session.flush()
        task = Task(title="Test Task", estimated_effort=2.0, pbi_id=pbi.id)
        db.session.add(task)
        db.session.commit()
        task_id = task.id

    response = client.post("/tasks/update_status", data={
        "task_id": str(task_id),
        "status": "In Progress",
    }, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        task = Task.query.get(task_id)
        assert task.status == "In Progress"


def test_tasks_page_loads(client, seeded_users):
    login(client, "dev_user", "devpass123")
    response = client.get("/tasks")
    assert response.status_code == 200


# ── Reports (hamed_routes) ──────────────────────────────────────────────────

def test_reports_page_loads(client, seeded_users):
    login(client, "dev_user", "devpass123")
    response = client.get("/reports")
    assert response.status_code == 200