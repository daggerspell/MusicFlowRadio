from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .models import Base

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///music_flow_radio.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        # Create the tables in the database
        db.create_all()

    return app
