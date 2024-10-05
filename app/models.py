from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="listener")
    created_at = Column(DateTime, default=datetime.utcnow)

    playlists = relationship("Playlist", back_populates="created_by_user")


class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    album = Column(String, nullable=True)
    genre = Column(String, nullable=True)
    duration = Column(Integer, nullable=False)  # Duration in seconds
    file_path = Column(String, nullable=False)  # should this be an upload file field?
    created_at = Column(DateTime, default=datetime.utcnow)
    play_count = Column(Integer, default=0)
    theme = Column(String, nullable=True)
    style = Column(String, nullable=True)
    lyrics = Column(Text, nullable=True)
    twitter_post = Column(String, nullable=True)
    track_number = Column(Integer, nullable=True)

    play_histories = relationship("PlayHistory", back_populates="song")
    ai_contents = relationship("AIContent", back_populates="song")


class Playlist(Base):
    __tablename__ = "playlists"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    created_by_user = relationship("User", back_populates="playlists")
    songs = relationship("Song", secondary="playlist_songs", back_populates="playlists")


class PlaylistSongs(Base):
    __tablename__ = "playlist_songs"

    playlist_id = Column(Integer, ForeignKey("playlists.id"), primary_key=True)
    song_id = Column(Integer, ForeignKey("songs.id"), primary_key=True)


class AIContent(Base):
    __tablename__ = "ai_contents"

    id = Column(Integer, primary_key=True)
    content_type = Column(String, nullable=False)  # e.g., "song_intro", "commercial"
    text = Column(Text, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)
    audio_path = Column(String, nullable=True)
    song_id = Column(Integer, ForeignKey("songs.id"), nullable=True)

    song = relationship("Song", back_populates="ai_contents")


class Commercial(Base):
    __tablename__ = "commercials"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    audio_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class RadioStation(Base):
    __tablename__ = "radio_stations"

    id = Column(Integer, primary_key=True)
    station_name = Column(String, nullable=False)
    current_playlist = Column(Integer, ForeignKey("playlists.id"), nullable=True)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    playlist = relationship("Playlist")


class PlayHistory(Base):
    __tablename__ = "play_histories"

    id = Column(Integer, primary_key=True)
    song_id = Column(Integer, ForeignKey("songs.id"), nullable=False)
    played_at = Column(DateTime, default=datetime.utcnow)
    ai_content_id = Column(Integer, ForeignKey("ai_contents.id"), nullable=True)

    song = relationship("Song", back_populates="play_histories")
    ai_content = relationship("AIContent")


class TTSVoice(Base):
    __tablename__ = "tts_voices"

    id = Column(Integer, primary_key=True)
    voice_name = Column(String, nullable=False)
    language = Column(String, nullable=False)
    gender = Column(String, nullable=True)
    model_type = Column(String, nullable=False)  # e.g., "Coqui TTS", "Piper"
    model_name = Column(String, nullable=False)
    generation_url = Column(String, nullable=False)
