from models import db, User


def register(client, username, password, role="developer"):
    return client.post("/auth/register", data={
        "username": username,
        "password": password,
        "role": role,
    }, follow_redirects=True)


def login(client, username, password):
    return client.post("/auth/login", data={
        "username": username,
        "password": password,
    }, follow_redirects=True)


def test_register(client, app):
    response = register(client, "newuser", "password123")
    assert response.status_code == 200
    with app.app_context():
        user = User.query.filter_by(username="newuser").first()
        assert user is not None
        assert user.role == "developer"


def test_login_success(client, seeded_users, app):
    response = login(client, "dev_user", "devpass123")
    assert response.status_code == 200


def test_login_fail(client, seeded_users):
    response = login(client, "dev_user", "wrongpassword")
    assert b"Invalid username or password" in response.data


def test_logout(client, seeded_users):
    login(client, "dev_user", "devpass123")
    response = client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200


def test_role_check(client, seeded_users, app):
    register(client, "another_client", "pass123", role="client")
    with app.app_context():
        user = User.query.filter_by(username="another_client").first()
        assert user.role == "client"