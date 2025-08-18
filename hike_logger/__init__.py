from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY']='dev'
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        'sqlite:///' + os.path.join(app.instance_path, 'hike_logger.db')
        )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

     # Create instance folder if it doesn't exist
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    db.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    return app

