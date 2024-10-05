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
    ):
        self.title = title
        self.artist = artist
        self.file_path = file_path
        self.previous_intros: List[str] = []
        self.theme = theme
        self.style = style
        self.lyrics = lyrics
        self.twitter_post = twitter_post

    def __str__(self):
        return f"Title: {self.title}, Artist: {self.artist}, Theme: {self.theme}, Style: {self.style}, Lyrics: {self.lyrics}, Twitter Post: {self.twitter_post}"
