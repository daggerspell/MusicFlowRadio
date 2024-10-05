from flask import request, jsonify
from . import db, create_app
from .models import Song

app = create_app()


@app.route("/", methods=["GET"])
def home():
    return jsonify(message="Welcome to MusicFlowRadio!"), 200


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify(message="Health check successful!"), 200


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
    return jsonify(message="Song added successfully"), 201


if __name__ == "__main__":
    app.run(debug=True)
