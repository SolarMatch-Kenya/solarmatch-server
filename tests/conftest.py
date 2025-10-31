# tests/conftest.py
import pytest
import time # Import the time module
import random
import os
from dotenv import load_dotenv

# Load test environment variables BEFORE creating the app
load_dotenv('.env.test')

# Now import your app factory and extensions
from app import create_app
from extensions import db as _db # Use alias to avoid pytest conflicts
from models.user import User # Import User model
from flask_jwt_extended import create_access_token

@pytest.fixture(scope='session')
def app():
    """Session-wide test `Flask` application."""
    # Override config for testing
    config_override = {
        "TESTING": True,
        # Read directly from loaded env vars
        "SQLALCHEMY_DATABASE_URI": os.getenv("DATABASE_URL"),
        "SECRET_KEY": os.getenv("SECRET_KEY"),
        "JWT_SECRET_KEY": os.getenv("SECRET_KEY"),
        "WTF_CSRF_ENABLED": False,
        "MAIL_SUPPRESS_SEND": True,
        # Ensure Celery uses test settings too if needed
        "CELERY_BROKER_URL": os.getenv("REDIS_URL"),
        "CELERY_RESULT_BACKEND": os.getenv("REDIS_URL"),
    }
    _app = create_app(config_override=config_override)

    # Establish an application context before running tests
    with _app.app_context():
        yield _app

@pytest.fixture(scope='session')
def db(app):
    """Session-wide test database."""
    _db.app = app
    _db.create_all()

    yield _db

    _db.drop_all()

@pytest.fixture(scope='function')
def session(db):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    sess = db._make_scoped_session(options=options)

    # Establish SAVEPOINT
    sess.begin_nested()


    # Overwrite the session used by the extension
    db.session = sess

    yield sess

    # Rollback nested SAVEPOINT
    sess.rollback()
    # Close connection
    transaction.rollback()
    connection.close()
    sess.remove()


@pytest.fixture(scope='function')
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(scope='function')
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

# --- User Fixtures ---

@pytest.fixture(scope='function')
def admin_user(session):
    """Create an admin user."""
    # Add a timestamp or random element to make username unique per test run
    unique_suffix = int(time.time() * 1000) # milliseconds timestamp
    admin = User(
        full_name="Admin User",
        email=f"admin{unique_suffix}@test.com", # Make email unique too
        password_hash=bcrypt.generate_password_hash("password").decode("utf-8"),
        user_name=f"ADM-Admin-{unique_suffix}", # Make username unique
        role="admin"
    )
    session.add(admin)
    session.flush()
    return admin

@pytest.fixture(scope='function')
def customer_user(session):
    """Create a customer user."""
    unique_suffix = int(time.time() * 1000) + random.randint(1, 1000) # Add randomness
    customer = User(
        full_name="Customer User",
        email=f"customer{unique_suffix}@test.com",
        password_hash=bcrypt.generate_password_hash("password").decode("utf-8"),
        user_name=f"CUS-Customer-{unique_suffix}",
        role="customer"
    )
    session.add(customer)
    session.flush()
    return customer

@pytest.fixture(scope='function')
def installer_user(session):
    """Create an installer user."""
    unique_suffix = int(time.time() * 1000) + random.randint(1, 1000)
    installer = User(
        full_name="Installer User",
        email=f"installer{unique_suffix}@test.com",
        password_hash=bcrypt.generate_password_hash("password").decode("utf-8"),
        user_name=f"INS-Installer-{unique_suffix}",
        role="installer",
        installer_category="Residential",
        county="Nairobi",
        phone_number="0712345678"
    )
    session.add(installer)
    session.flush()
    return installer

# --- Auth Header Fixtures ---

@pytest.fixture(scope='function')
def admin_auth_headers(app, admin_user):
    """Returns headers with a valid JWT token for the admin user."""
    with app.app_context(): # Need context to create token
        access_token = create_access_token(identity=str(admin_user.id))
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture(scope='function')
def customer_auth_headers(app, customer_user):
    """Returns headers with a valid JWT token for the customer user."""
    with app.app_context():
        access_token = create_access_token(identity=str(customer_user.id))
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture(scope='function')
def installer_auth_headers(app, installer_user):
    """Returns headers with a valid JWT token for the installer user."""
    with app.app_context():
        access_token = create_access_token(identity=str(installer_user.id))
    return {"Authorization": f"Bearer {access_token}"}

# Import bcrypt here AFTER app context might be needed by fixtures
from extensions import bcrypt