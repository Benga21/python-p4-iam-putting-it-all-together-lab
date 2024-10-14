from flask import Flask
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'  # Default database URI for production
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'  # Ensure this is kept secret
    JSON_COMPACT = False

class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Use in-memory database for testing

# Choose which configuration to use based on your environment
app = Flask(__name__)
app.config.from_object(TestingConfig)  # Change to Config for production
app.secret_key = app.config['SECRET_KEY']
app.json.compact = app.config['JSON_COMPACT']

# Set up SQLAlchemy with a naming convention for foreign keys
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})
db = SQLAlchemy(metadata=metadata)

# Initialize Flask-Migrate and the database
migrate = Migrate(app, db)
db.init_app(app)

# Initialize Flask-Bcrypt for password hashing
bcrypt = Bcrypt(app)

# Set up Flask-Restful for API management
api = Api(app)
