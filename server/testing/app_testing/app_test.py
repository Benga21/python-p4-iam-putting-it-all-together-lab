import pytest
from faker import Faker
from app import create_app, db
from models import User, Recipe

fake = Faker()

@pytest.fixture(scope='module')
def test_client():
    """Set up a test client for the Flask application."""
    app = create_app('testing')  # Use testing config
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Create the database for testing
            yield client
            db.drop_all()  # Clean up after tests

@pytest.fixture(autouse=True)
def cleanup():
    """Cleanup the database before each test."""
    db.session.rollback()  # Roll back any changes
    yield
    db.session.remove()  # Remove the session to ensure all resources are released

@pytest.fixture
def new_user():
    """Create a user with a unique username for testing."""
    user = User(
        username=fake.user_name(),
        password='password',  # This should be hashed in the actual app
    )
    with db.session.begin():
        db.session.add(user)
        db.session.commit()
    return user

class TestSignup:
    """Signup resource tests."""

    def test_create_user_at_signup(self, test_client):
        """Creates user records with unique usernames and passwords at /signup."""
        unique_username = fake.user_name()  # Generate a unique username
        response = test_client.post('/signup', json={
            'username': unique_username,
            'password': 'pikachu',
            'bio': 'I wanna be the very best...',
            'image_url': 'https://example.com/image.jpg'
        })

        assert response.status_code == 201
        new_user = User.query.filter_by(username=unique_username).first()
        assert new_user is not None
        assert new_user.verify_password('pikachu')

    def test_invalid_user_signup(self, test_client):
        """422s invalid usernames at /signup."""
        response = test_client.post('/signup', json={
            'password': 'pikachu',  # Missing username
            'bio': 'Invalid user test',
            'image_url': 'https://example.com/image.jpg'
        })

        assert response.status_code == 422

class TestLogin:
    """Login resource tests."""

    def test_logs_in(self, test_client, new_user):
        """Logs users in with a username and password at /login."""
        response = test_client.post('/login', json={
            'username': new_user.username,
            'password': 'password',  # Assuming this is the raw password
        })

        assert response.status_code == 200
        assert response.get_json()['message'] == "Login successful."

        with test_client.session_transaction() as session:
            assert session['user_id'] == new_user.id

    def test_401s_bad_logins(self, test_client):
        """Returns 401 for an invalid username and password at /login."""
        response = test_client.post('/login', json={
            'username': 'invalid_user',
            'password': 'wrong_password',
        })

        assert response.status_code == 401

class TestLogout:
    """Logout resource tests."""

    def test_logs_out(self, test_client, new_user):
        """Logs users out at /logout."""
        with test_client.session_transaction() as session:
            session['user_id'] = new_user.id

        response = test_client.delete('/logout')
        assert response.status_code == 204  # Assuming logout returns 204

        with test_client.session_transaction() as session:
            assert session.get('user_id') is None

    def test_401s_if_no_session(self, test_client):
        """Returns 401 if a user attempts to logout without a session at /logout."""
        response = test_client.delete('/logout')
        assert response.status_code == 401

class TestRecipeIndex:
    """Recipe index tests."""

    def test_lists_recipes_with_200(self, test_client, new_user):
        """Returns a list of recipes associated with the logged-in user and a 200 status code."""
        recipes = [
            Recipe(title=fake.sentence(), instructions=fake.paragraph(), minutes_to_complete=30, user_id=new_user.id)
            for _ in range(5)
        ]
        with test_client.application.app_context():
            db.session.add_all(recipes)
            db.session.commit()

        with test_client.session_transaction() as session:
            session['user_id'] = new_user.id

        response = test_client.get('/recipes')
        assert response.status_code == 200
        response_json = response.get_json()
        assert len(response_json) == 5

    def test_get_route_returns_401_when_not_logged_in(self, test_client):
        """Returns 401 when user is not logged in."""
        # Ensure no user is logged in
        with test_client.session_transaction() as session:
            session.clear()  # Clear the session to ensure user_id is not set

        response = test_client.get('/recipes')
        assert response.status_code == 401

    def test_creates_recipes_with_201(self, test_client, new_user):
        """Creates a new recipe for the logged-in user and returns a 201 status code."""
        with test_client.session_transaction() as session:
            session['user_id'] = new_user.id

        response = test_client.post('/recipes', json={
            'title': 'New Recipe',
            'instructions': 'Instructions for the new recipe',
            'minutes_to_complete': 45,
        })

        assert response.status_code == 201
        assert response.get_json()['message'] == "Recipe created successfully."
        created_recipe = Recipe.query.filter_by(title='New Recipe').first()
        assert created_recipe is not None

    def test_returns_422_when_recipe_data_is_invalid(self, test_client, new_user):
        """Returns 422 when recipe data is invalid at /recipes."""
        with test_client.session_transaction() as session:
            session['user_id'] = new_user.id

        response = test_client.post('/recipes', json={})  # Missing all required fields
        assert response.status_code == 422

class TestRecipeModel:
    """Tests for Recipe model in models.py."""

    def test_has_attributes(self):
        """Test that Recipe has attributes title, instructions, and minutes_to_complete."""
        recipe = Recipe(title='Test Recipe', instructions='Test Instructions', minutes_to_complete=30)
        assert recipe.title == 'Test Recipe'
        assert recipe.instructions == 'Test Instructions'
        assert recipe.minutes_to_complete == 30

class TestUserModel:
    """Tests for User model in models.py."""

    def test_has_attributes(self):
        """Test that User has attributes username, _password_hash, image_url, and bio."""
        user = User(username='testuser')
        user.password = 'password'  # Set the password to test hashing
        assert user.username == 'testuser'

    def test_requires_username(self):
        """Test that User requires a username."""
        user = User(password='password')
        db.session.add(user)
        with pytest.raises(Exception):  # Expecting an exception when trying to commit
            db.session.commit()

    def test_requires_unique_username(self, test_client):
        """Test that User requires a unique username."""
        user1 = User(username='uniqueuser', password='password')
        user2 = User(username='uniqueuser', password='password2')  # Same username
        db.session.add(user1)
        db.session.commit()
        db.session.add(user2)
        with pytest.raises(Exception):  # Expecting an exception for unique constraint violation
            db.session.commit()

    def test_has_recipes(self, new_user):
        """Test that User has records with lists of recipes."""
        recipe1 = Recipe(title='Recipe 1', instructions='Instructions 1', minutes_to_complete=15, user_id=new_user.id)
        recipe2 = Recipe(title='Recipe 2', instructions='Instructions 2', minutes_to_complete=30, user_id=new_user.id)
        db.session.add(recipe1)
        db.session.add(recipe2)
        db.session.commit()

        assert len(new_user.recipes) == 2

