from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate 
from flask_mail import Mail
from dotenv import load_dotenv
from os import path, environ

db = SQLAlchemy()
load_dotenv()
mail = Mail()
DB_NAME = "database.db"
BASE_DIR = path.abspath(path.dirname(__file__))
DB_PATH = path.join(BASE_DIR, DB_NAME)

def create_app(test_config=None):
    app = Flask(__name__)

    if test_config is not None:
        app.config.update(test_config)
    else:
        app.config["SECRET_KEY"] = environ.get('SECRET_KEY')
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
        # app.config["SQLALCHEMY_ECHO"] = True
        app.config['MAIL_SERVER'] = 'smtp.gmail.com'
        app.config['MAIL_PORT'] = 587
        app.config['MAIL_USE_TLS'] = True
        app.config['MAIL_USERNAME'] = environ.get('MAIL_USERNAME')
        app.config['MAIL_PASSWORD'] = environ.get('MAIL_PASSWORD')
        app.config['MAIL_DEFAULT_SENDER'] = environ.get('MAIL_USERNAME')

    db.init_app(app)
    mail.init_app(app)
    migrate = Migrate(app, db)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Quiz, Score, Reward, Rating

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

# This function can be removed if you are using Flask-Migrate
# def create_database(app):
#     if not path.exists(DB_PATH):
#         with app.app_context():
#             try:
#                 db.create_all()
#                 print('Created Database!')
#             except Exception as e:
#                 print(f"Error creating tables: {e}")




        
