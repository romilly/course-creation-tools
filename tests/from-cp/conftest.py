import pytest
from django.db import connections
import threading
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

def _close_db_connections():
    """Close all database connections from the current thread."""
    for conn in connections.all():
        if conn.connection and not conn.is_in_memory_db():
            conn.close_if_unusable_or_obsolete()

@pytest.fixture(scope='session')
def live_server(request):
    """Session-scoped live server"""
    server = request.getfixturevalue('live_server')
    yield server
    # Cleanup
    _close_db_connections()

@pytest.fixture(autouse=True)
def _handle_database():
    """Ensure database connections are cleaned up after each test."""
    yield
    _close_db_connections()

@pytest.fixture(scope='session')
def live_server_url(live_server):
    """Return the live server URL."""
    return live_server.url

@pytest.fixture(scope='session')
def load_test_data(django_db_setup, django_db_blocker):
    """Load test data from fixtures."""
    with django_db_blocker.unblock():
        call_command('loaddata', '../fixtures/initial_data.json')

@pytest.fixture(scope='function')
def hash_user_passwords(load_test_data, db):
    """Hash passwords for all users in the database."""
    User = get_user_model()
    users = User.objects.all()
    for user in users:
        user.password = make_password(user.password)
        user.save()

@pytest.fixture(scope='session')
def live_server_url(live_server):
    """Override the live_server fixture to handle cleanup."""
    yield live_server.url
    # Ensure connections are closed in the main thread
    _close_db_connections()
    # Wait briefly for any background threads to complete
    for thread in threading.enumerate():
        if thread is not threading.current_thread():
            thread.join(timeout=0.5)  # Reduced timeout from 1.0 to 0.5 seconds
