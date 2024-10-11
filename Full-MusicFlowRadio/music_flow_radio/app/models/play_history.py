from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class PlayHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey("song.id"), nullable=False)
    dj_id = db.Column(db.Integer, db.ForeignKey("dj.id"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # Duration in seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    song = db.relationship("Song", backref="play_history")
    dj = db.relationship("DJ", backref="play_history")

    def __repr__(self):
        return f"<PlayHistory {self.song.title} by {self.dj.name}>"
