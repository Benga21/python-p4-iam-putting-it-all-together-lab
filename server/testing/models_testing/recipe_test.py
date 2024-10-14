import pytest
from sqlalchemy.exc import IntegrityError
from app import app
from models import db, Recipe, User  # Import User for user creation

class TestRecipe:
    '''Tests for Recipe model in models.py'''

    def test_has_attributes(self):
        '''Test that Recipe has attributes title, instructions, and minutes_to_complete.'''
        
        with app.app_context():
            Recipe.query.delete()  # Clean previous Recipe entries
            User.query.delete()  # Clean previous User entries
            db.session.commit()

            # Create a user first
            user = User(username="example_user")
            user.password = "password123"  # Set password using setter
            db.session.add(user)
            db.session.commit()  # Commit to ensure user is saved and has id

            # Create a recipe with sufficient instructions
            recipe = Recipe(
                title="Delicious Shed Ham",
                instructions="Or kind rest bred with am shed then it turned out to be the best golden, succulent, oh so juicy ham you ever had in your life.",
                minutes_to_complete=60,
                user_id=user.id  # Link to the user
            )

            db.session.add(recipe)
            db.session.commit()

            new_recipe = Recipe.query.filter(Recipe.title == "Delicious Shed Ham").first()

            assert new_recipe.title == "Delicious Shed Ham"
            assert new_recipe.instructions == "Or kind rest bred with am shed then it turned out to be the best golden, succulent, oh so juicy ham you ever had in your life."
            assert new_recipe.minutes_to_complete == 60