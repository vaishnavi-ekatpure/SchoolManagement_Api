

from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def configure_mysql(app):
    DB_DATABASE= os.getenv("DB_DATABASE")
    DB_USERNAME= os.getenv("DB_USERNAME")
    DB_PASSWORD= os.getenv("DB_PASSWORD")

    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{DB_USERNAME}:{DB_PASSWORD}@localhost/{DB_DATABASE}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
    
    db.init_app(app) 

