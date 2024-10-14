import pytest
from server.app import app, db

@pytest.fixture(scope='module')
def client():
    """Set up a test client for the Flask application."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Set up the database
            yield client
            db.drop_all()  # Clean up after tests

@pytest.fixture(scope='module')
def init_database():
    """Set up the database and create a user for tests."""
    with app.app_context():
        db.create_all()  # Set up the database
        # You can add initial data here if needed
        yield
        db.drop_all()  # Clean up after tests

def pytest_itemcollected(item):
    """Customizes test item names in the output."""
    par = item.parent.obj
    node = item.obj
    pref = par.__doc__.strip() if par.__doc__ else par.__class__.__name__
    suf = node.__doc__.strip() if node.__doc__ else node.__name__
    if pref or suf:
        item._nodeid = ' '.join((pref, suf))
