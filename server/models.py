from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    _password_hash = db.Column(db.String(128), nullable=False)
    bio = db.Column(db.String(500), nullable=True)  # Explicitly set nullable=True
    image_url = db.Column(db.String(500), nullable=True)  # Explicitly set nullable=True

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        """Hashes the password and stores it."""
        self._password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """Verifies the provided password against the stored hash."""
        return check_password_hash(self._password_hash, password)

class Recipe(db.Model):
    __tablename__ = 'recipe'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    minutes_to_complete = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationship to link Recipe to User
    user = db.relationship('User', backref='recipes')

    def to_dict(self):
        """Convert the Recipe object to a dictionary for JSON serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'instructions': self.instructions,
            'minutes_to_complete': self.minutes_to_complete,
            'user_id': self.user_id
        }
