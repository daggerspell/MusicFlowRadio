from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from . import db


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False, default="listener")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    playlists = db.relationship("Playlist", back_populates="created_by_user")


class Song(db.Model):
    __tablename__ = "songs"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    artist = db.Column(db.String, nullable=False)
    album = db.Column(db.String, nullable=True)
    genre = db.Column(db.String, nullable=True)
    duration = db.Column(db.Integer, nullable=False)  # Duration in seconds
    file_path = db.Column(
        db.String, nullable=False
    )  # should this be an upload file field?
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    play_count = db.Column(db.Integer, default=0)
    theme = db.Column(db.String, nullable=True)
    style = db.Column(db.String, nullable=True)
    lyrics = db.Column(db.Text, nullable=True)
    twitter_post = db.Column(db.String, nullable=True)
    track_number = db.Column(db.Integer, nullable=True)

    play_histories = relationship("PlayHistory", back_populates="song")
    ai_contents = relationship("AIContent", back_populates="song")
    playlists = relationship(
        "Playlist", secondary="playlist_songs", back_populates="songs"
    )


class Playlist(db.Model):
    __tablename__ = "playlists"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    created_by = db.Column(db.Integer, ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    created_by_user = relationship("User", back_populates="playlists")
    songs = relationship("Song", secondary="playlist_songs", back_populates="playlists")


class PlaylistSongs(db.Model):
    __tablename__ = "playlist_songs"

    playlist_id = db.Column(db.Integer, ForeignKey("playlists.id"), primary_key=True)
    song_id = db.Column(db.Integer, ForeignKey("songs.id"), primary_key=True)


class AIContent(db.Model):
    __tablename__ = "ai_contents"

    id = db.Column(db.Integer, primary_key=True)
    content_type = db.Column(
        db.String, nullable=False
    )  # e.g., "song_intro", "commercial"
    text = db.Column(db.Text, nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    audio_path = db.Column(db.String, nullable=True)
    song_id = db.Column(db.Integer, ForeignKey("songs.id"), nullable=True)

    song = relationship("Song", back_populates="ai_contents")


class Commercial(db.Model):
    __tablename__ = "commercials"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    text = db.Column(db.Text, nullable=False)
    audio_path = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class RadioStation(db.Model):
    __tablename__ = "radio_stations"

    id = db.Column(db.Integer, primary_key=True)
    station_name = db.Column(db.String, nullable=False)
    current_playlist = db.Column(db.Integer, ForeignKey("playlists.id"), nullable=True)
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    playlist = relationship("Playlist")


class PlayHistory(db.Model):
    __tablename__ = "play_histories"

    id = db.Column(db.Integer, primary_key=True)
    song_id = db.Column(db.Integer, ForeignKey("songs.id"), nullable=False)
    played_at = db.Column(db.DateTime, default=datetime.utcnow)
    ai_content_id = db.Column(db.Integer, ForeignKey("ai_contents.id"), nullable=True)

    song = relationship("Song", back_populates="play_histories")
    ai_content = relationship("AIContent")


class TTSVoice(db.Model):
    __tablename__ = "tts_voices"

    id = db.Column(db.Integer, primary_key=True)
    voice_name = db.Column(db.String, nullable=False)
    language = db.Column(db.String, nullable=False)
    gender = db.Column(db.String, nullable=True)
    model_type = db.Column(db.String, nullable=False)  # e.g., "Coqui TTS", "Piper"
    model_name = db.Column(db.String, nullable=False)
    generation_url = db.Column(db.String, nullable=False)
