from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class DJ(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    voice_id = db.Column(db.String(100), nullable=False)
    show_name = db.Column(db.String(100), nullable=False)
    preferences = db.Column(db.JSON)  # JSON object of DJ preferences
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    schedules = db.relationship("Schedule", backref="dj", lazy="dynamic")
    playlists = db.relationship("Playlist", backref="dj", lazy="dynamic")

    def __repr__(self):
        return f"<DJ {self.name}>"
