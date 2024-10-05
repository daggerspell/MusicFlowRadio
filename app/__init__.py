from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from .models import Base
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///music_flow_radio.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        # Create the tables in the database
        db.create_all()

    @app.route("/", methods=["GET"])
    def home():
        return jsonify(message="Welcome to MusicFlowRadio!"), 200

    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify(message="Health check successful!")

    @app.route("/songs", methods=["POST"])
    def add_song():
        data = request.get_json()
        new_song = Song(
            title=data["title"],
            artist=data["artist"],
            duration=data["duration"],
            file_path=data["file_path"],
        )
        db.session.add(new_song)
        db.session.commit()
        return jsonify(message="Song added successfully")

    @app.route("/songs", methods=["GET"])
    def get_songs():
        songs = Song.query.all()
        return jsonify([song.title for song in songs])

    return app
