from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dj_id = db.Column(db.Integer, db.ForeignKey("dj.id"))
    songs = db.Column(db.JSON)  # JSON array of song IDs
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Playlist {self.name}>"
