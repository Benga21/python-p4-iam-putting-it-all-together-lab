from flask import Flask, request, jsonify, session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Import Flask-Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Recipe  # Import models here

def create_app(config_name):
    app = Flask(__name__)

    # Configure the app
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yourdatabase.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'your_secret_key'

    if config_name == 'testing':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use an in-memory database for tests

    db.init_app(app)

    # Initialize Flask-Migrate
    migrate = Migrate(app, db)

    # Create the database tables only if not testing
    with app.app_context():
        db.create_all()

    # Route for the root URL
    @app.route('/')
    def home():
        return redirect('/plants')  # Redirect to /plants

    # Example plants route (modify as needed)
    @app.route('/plants', methods=['GET'])
    def plants():
        return jsonify({"message": "Welcome to the Plants API!"})  # Sample response for /plants

    # Define user signup route
    @app.route('/signup', methods=['POST'])
    def signup():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"error": "Username and password are required."}), 422

        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already exists."}), 422

        user = User(username=username)
        user.password = password  # Hash the password using setter
        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "User created successfully."}), 201

    # Define user login route
    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.verify_password(password):  # Use verify_password method from User model
            session['user_id'] = user.id  # Store user ID in session
            return jsonify({"message": "Login successful."}), 200
        return jsonify({"error": "Invalid username or password."}), 401

    # Define user logout route
    @app.route('/logout', methods=['DELETE'])
    def logout():
        if 'user_id' not in session:  # Check if user is logged in
            return jsonify({"error": "Unauthorized"}), 401  # Return 401 if no session
        session.pop('user_id', None)  # Clear the user ID from session
        return jsonify({"message": "Logged out successfully."}), 204

    # Define recipe routes
    @app.route('/recipes', methods=['GET', 'POST'])
    def recipes():
        if request.method == 'GET':
            if 'user_id' not in session:  # Check if user is logged in
                return jsonify({"error": "Unauthorized access."}), 401
            all_recipes = Recipe.query.filter_by(user_id=session['user_id']).all()  # Fetch user's recipes
            return jsonify([recipe.to_dict() for recipe in all_recipes]), 200

        if request.method == 'POST':
            if 'user_id' not in session:  # Check if user is logged in
                return jsonify({"error": "Unauthorized access."}), 401
            
            data = request.get_json()
            title = data.get('title')
            instructions = data.get('instructions')
            minutes_to_complete = data.get('minutes_to_complete')

            if not title or not instructions or minutes_to_complete is None:  # Validate input
                return jsonify({"error": "Invalid recipe data."}), 422
            
            new_recipe = Recipe(
                title=title,
                instructions=instructions,
                minutes_to_complete=minutes_to_complete,
                user_id=session['user_id']  # Associate with logged-in user
            )  
            db.session.add(new_recipe)
            db.session.commit()
            return jsonify({"message": "Recipe created successfully."}), 201

    @app.errorhandler(404)
    def not_found(e):
        return jsonify(error="Not found"), 404

    return app

# Create the app instance
app = create_app('development')

if __name__ == '__main__':
    app.run(debug=True)
