import pytest
from sqlalchemy.exc import IntegrityError
from app import app
from models import db, User, Recipe  # Import necessary models

class TestUser:
    '''Tests for User model in models.py'''

    def test_has_attributes(self):
        '''Test that User has attributes username, _password_hash, image_url, and bio.'''

        with app.app_context():
            User.query.delete()
            db.session.commit()

            user = User(
                username="Liz",
                image_url="https://prod-images.tcm.com/Master-Profile-Images/ElizabethTaylor.jpg",
                bio="Dame Elizabeth was a British-American actress..."
            )
            user.password = "whosafraidofvirginiawoolf"  # Use password setter

            db.session.add(user)
            db.session.commit()

            created_user = User.query.filter(User.username == "Liz").first()

            assert created_user.username == "Liz"
            assert created_user.image_url == "https://prod-images.tcm.com/Master-Profile-Images/ElizabethTaylor.jpg"
            assert created_user.bio == "Dame Elizabeth was a British-American actress..."

            # Ensure that password attributes are not directly accessible
            with pytest.raises(AttributeError):
                _ = created_user.password  # This should be behind access control

    def test_requires_username(self):
        '''Test that User requires a username.'''
        with app.app_context():
            User.query.delete()
            db.session.commit()

            user = User()  # User without a username
            with pytest.raises(IntegrityError):
                db.session.add(user)
                db.session.commit()

    def test_requires_unique_username(self):
        '''Test that User requires a unique username.'''
        with app.app_context():
            User.query.delete()
            db.session.commit()

            user_1 = User(username="Ben")
            user_1.password = "securepassword"  # Set the password
            db.session.add(user_1)
            db.session.commit()  # Commit the first user

            user_2 = User(username="Ben")  # Attempt to create another with the same username
            user_2.password = "anothersecurepassword"  # Set a password for the second user

            with pytest.raises(IntegrityError):
                db.session.add(user_2)
                db.session.commit()

    def test_has_list_of_recipes(self):
        '''Test that User has records with lists of recipes.'''
        with app.app_context():
            User.query.delete()
            Recipe.query.delete()  # Clear previous Recipe entries if necessary
            db.session.commit()

            user = User(username="Prabhdip") 
            user.password = "testpassword"  # Set password using setter
            db.session.add(user)
            db.session.commit()  # Commit before adding recipes

            # Create recipes with valid instructions
            recipe_1 = Recipe(
                title="Delicious Shed Ham",
                instructions="Or kind rest bred with am shed then it turned out to be the best golden, succulent, oh so juicy ham you ever had in your life.",
                minutes_to_complete=60,
                user_id=user.id
            )
            recipe_2 = Recipe(
                title="Hasty Party Ham",
                instructions="This dish requires friendship, love, and ham. Blend ingredients in harmony.",
                minutes_to_complete=30,
                user_id=user.id
            )

            db.session.add_all([recipe_1, recipe_2])
            db.session.commit()
            
            # Check that all were created in db
            assert user.id
            assert recipe_1.id
            assert recipe_2.id

            # Check that recipes were saved to user
            assert recipe_1 in user.recipes
            assert recipe_2 in user.recipes