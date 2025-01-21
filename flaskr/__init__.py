import os

from flask import Flask
from flaskr.config.databaseconfig import configure_mysql
from flaskr.config.mailconfig import configure_mail
from flaskr.config.extensions import jwt
from flaskr.views.auth_view import auth_routes
from flaskr.views.admin_view import admin_routes
from datetime import timedelta
from dotenv import load_dotenv

def create_app(test_config=None):
    load_dotenv()

    app = Flask(__name__, instance_relative_config=True)

    #For session storage
    app.secret_key = os.urandom(24)

    #For JWT Token
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    jwt.init_app(app)

    configure_mysql(app)
    configure_mail(app)

    #Register views
    app.register_blueprint(auth_routes)
    app.register_blueprint(admin_routes)
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app