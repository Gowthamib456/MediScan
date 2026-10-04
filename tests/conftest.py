import pytest
import os

os.environ['DATABASE_URI'] = 'sqlite:///test_mediscan.db'

from app import app as flask_app, db as _db, seed_database_defaults

@pytest.fixture
def app():
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///test_mediscan.db',
        'SECRET_KEY': 'test-secret-key-2026',
        'WTF_CSRF_ENABLED': False
    })

    with flask_app.app_context():
        _db.create_all()
        seed_database_defaults()
        yield flask_app
        _db.session.remove()
        _db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()
