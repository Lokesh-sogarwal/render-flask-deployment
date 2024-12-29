from flask import Flask, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect


db = SQLAlchemy()
DB_NAME = "majdoorindia"  # Use the actual database name
mail = Mail()

def create_app():
    app = Flask(__name__)
    csrf = CSRFProtect(app)

    # Configuration for app
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://root@localhost/{DB_NAME}'  # Corrected key
    app.config['SECRET_KEY'] = '--majdoor@india@-@2580#1234--'
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Or use another mail service
    app.config['MAIL_PORT'] = 587  # Typically 587 for TLS
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = 'noreply.educonnect551@gmail.com'
    app.config['MAIL_PASSWORD'] = "hivz kuvf zkeq yobg"
    app.config['MAIL_DEFAULT_SENDER'] = 'noreply.educonnect551@gmail.com'

    # Initialize the extensions
    db.init_app(app)
    mail.init_app(app)

    # Register blueprints
    from .views import views
    from website.auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth/')

    # Import User model and create tables
    from .models import User  # Ensure User model is imported
    create_tables(app)

    # Initialize LoginManager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'  # Define the login route for Flask-Login
    login_manager.init_app(app)

    # User loader function
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app

def create_tables(app):
    with app.app_context():
        db.create_all()
        print("Database tables created!")
