import pytest
from app import app as _app
from models import db as _db
from models import User


@pytest.fixture(scope="function")
def app():
    _app.config["TESTING"] = True
    _app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    _app.config["WTF_CSRF_ENABLED"] = False
    _app.config["SECRET_KEY"] = "test-secret"
    _app.config["LOGIN_DISABLED"] = False

    with _app.app_context():
        _db.create_all()
        yield _app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def seeded_users(app):
    developer = User(username="dev_user", role="developer")
    developer.set_password("devpass123")

    client_user = User(username="client_user", role="client")
    client_user.set_password("clientpass123")

    _db.session.add(developer)
    _db.session.add(client_user)
    _db.session.commit()

    return {"developer": "dev_user", "client": "client_user"}