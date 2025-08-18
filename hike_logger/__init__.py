from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY']='dev'
    app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite://hike_logger.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    from . import routes
    app.register_blueprint(routes.bp)

    return app

