from app import db
from datetime import datetime


class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    release_date = db.Column(db.Date)
    album_art_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    songs = db.relationship("Song", backref="album", lazy="dynamic")

    def __repr__(self):
        return f"<Album {self.title} by {self.artist}>"
