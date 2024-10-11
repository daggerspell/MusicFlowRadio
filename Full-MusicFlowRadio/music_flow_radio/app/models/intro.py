from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class Intro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey("song.id"), nullable=False)
    intro_text = db.Column(db.Text, nullable=False)
    intro_audio_path = db.Column(db.String(255), nullable=False)
    times_used = db.Column(db.Integer, default=0)
    is_retired = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    song = db.relationship("Song", backref="intros")

    def __repr__(self):
        return f"<Intro for {self.song.title}>"
