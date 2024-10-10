from app import db
from datetime import datetime


class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    album_id = db.Column(db.Integer, db.ForeignKey("album.id"))
    track_number = db.Column(db.Integer)
    file_path = db.Column(db.String(255), nullable=False)
    youtube_url = db.Column(db.String(255))
    duration = db.Column(db.Integer, nullable=False)
    times_played = db.Column(db.Integer, default=0)
    release_date = db.Column(db.Date)
    theme = db.Column(db.String(100))
    style = db.Column(db.String(100))
    lyrics = db.Column(db.Text)
    twitter_post = db.Column(db.String(280))
    song_art_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Song {self.title} by {self.artist}>"
