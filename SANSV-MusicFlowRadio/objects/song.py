from typing import List


class Song:
    def __init__(
        self,
        title: str,
        artist: str,
        file_path: str,
        theme: str = None,
        style: str = None,
        lyrics: str = None,
        twitter_post: str = None,
        play_count: int = 0,
    ):
        self.title = title
        self.artist = artist
        self.file_path = file_path
        self.theme = theme
        self.style = style
        self.lyrics = lyrics
        self.twitter_post = twitter_post
        self.play_count = play_count
        self.previous_intros: List[str] = []

    def __repr__(self):
        return f"Song(title={self.title}, artist={self.artist}, play_count={self.play_count})"
