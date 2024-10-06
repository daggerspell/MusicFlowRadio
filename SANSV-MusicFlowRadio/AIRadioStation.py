import random
import time
import pygame
import os
import sqlite3
from ollama import Client
import gtts
from typing import List, Dict, Tuple
from dotenv import load_dotenv
import mutagen
import re
from objects.Song import Song  # Import the Song class directly
from objects.Commercial import Commercial
from elevenlabs import Voice, VoiceSettings, save
from elevenlabs.client import ElevenLabs
from collections import deque
import threading


class AIRadioStation:
    def __init__(self):
        self.music_library: Dict[str, Song] = {}
        self.commercials: List[Commercial] = []
        self.playlist_queue: deque = deque()
        self.queue_lock = threading.Lock()
        # Load from .env file OPENAI_API_KEY
        load_dotenv()
        # client = Open(api_key=os.getenv("OPENAI_API_KEY"))
        self.host = "http://localhost:11434"
        self.client = Client(self.host)
        self.tts = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

        # Connect to SQLite database
        self.conn = sqlite3.connect("musicflowradio.db")
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.load_data()

    def create_tables(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS songs (
                title TEXT PRIMARY KEY,
                artist TEXT,
                file_path TEXT,
                theme TEXT,
                style TEXT,
                lyrics TEXT,
                twitter_post TEXT
            )
        """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS commercials (
                name TEXT PRIMARY KEY,
                file_path TEXT
            )
        """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS intros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                song_title TEXT,
                intro_text TEXT,
                intro_file_path TEXT,
                play_count INTEGER DEFAULT 0,
                archived INTEGER DEFAULT 0,
                FOREIGN KEY(song_title) REFERENCES songs(title)
            )
        """
        )
        self.conn.commit()

    def load_data(self):
        self.cursor.execute("SELECT * FROM songs")
        songs = self.cursor.fetchall()
        for song in songs:
            title, artist, file_path, theme, style, lyrics, twitter_post = song
            self.music_library[title] = Song(
                title, artist, file_path, theme, style, lyrics, twitter_post
            )

        self.cursor.execute("SELECT * FROM commercials")
        commercials = self.cursor.fetchall()
        for commercial in commercials:
            name, file_path = commercial
            self.commercials.append(Commercial(name, file_path))

        self.cursor.execute("SELECT * FROM intros WHERE archived = 0")
        intros = self.cursor.fetchall()
        for intro in intros:
            _, song_title, intro_text, intro_file_path, play_count, archived = intro
            if song_title in self.music_library:
                self.music_library[song_title].previous_intros.append(
                    (intro_text, intro_file_path, play_count)
                )

    def add_song(self, file_path: str):
        song_info = self.extract_song_info(file_path)
        if song_info:
            self.music_library[song_info.title] = song_info
            self.cursor.execute(
                """
                INSERT OR REPLACE INTO songs (title, artist, file_path, theme, style, lyrics, twitter_post)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    song_info.title,
                    song_info.artist,
                    song_info.file_path,
                    song_info.theme,
                    song_info.style,
                    song_info.lyrics,
                    song_info.twitter_post,
                ),
            )
            self.conn.commit()
            print(f"Added song: {song_info.title} by {song_info.artist}")
        else:
            print("Failed to add song. Insufficient information.")

    def extract_song_info(self, file_path: str) -> Song:
        # Extract metadata from audio file
        print(f"Extracting metadata from {file_path}...")
        audio = mutagen.File(file_path, easy=True)
        title = audio.get("title", [os.path.splitext(os.path.basename(file_path))[0]])[
            0
        ]
        artist = audio.get("artist", ["Dagger Spell"])[0]

        print(f"looking for markdown file in the same directory as {file_path}...")
        # Look for markdown file in the same directory
        dir_path = os.path.dirname(file_path)
        md_files = [f for f in os.listdir(dir_path) if f.endswith(".md")]

        theme = style = lyrics = twitter_post = None

        if md_files:
            md_content = self.parse_markdown_file(os.path.join(dir_path, md_files[0]))
            song_section = self.find_song_section(md_content, title)
            if song_section:
                theme = self.extract_info(song_section, "Theme:")
                style = self.extract_info(song_section, "Musical Style:")
                lyrics = self.extract_lyrics(song_section)
                twitter_post = self.extract_info(song_section, "Twitter Post:")

        new_song = Song(title, artist, file_path, theme, style, lyrics, twitter_post)

        print(f"Found the following information for {title}: {new_song}")
        # need to check with the user if the information is correct if not ask them to put in the correct information
        user_input = input("Is the information correct? (y/n): ")
        if user_input.lower() == "n":
            new_song.title = input("Enter the title of the song: ")
            new_song.artist = input("Enter the artist of the song: ")
            new_song.theme = input("Enter the theme of the song: ")
            new_song.style = input("Enter the musical style of the song: ")
            new_song.lyrics = input("Enter the lyrics of the song: ")
            new_song.twitter_post = input("Enter the twitter post of the song: ")
        return new_song

    def parse_markdown_file(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

    def find_song_section(self, content: str, song_title: str) -> str:
        pattern = re.compile(f"## {re.escape(song_title)}.*?(?=\n## |\Z)", re.DOTALL)
        match = pattern.search(content)
        return match.group(0) if match else None

    def extract_info(self, section: str, key: str) -> str:
        pattern = re.compile(f"{key}(.+)")
        match = pattern.search(section)
        return match.group(1).strip() if match else None

    def extract_lyrics(self, section: str) -> str:
        pattern = re.compile(r"```(.*?)```", re.DOTALL)
        match = pattern.search(section)
        return match.group(1).strip() if match else None

    def remove_song(self, title: str):
        if title in self.music_library:
            del self.music_library[title]
            self.cursor.execute("DELETE FROM songs WHERE title = ?", (title,))
            self.cursor.execute("DELETE FROM intros WHERE song_title = ?", (title,))
            self.conn.commit()

    def add_commercial(self, name: str, file_path: str):
        self.commercials.append(Commercial(name, file_path))
        self.cursor.execute(
            """
            INSERT OR REPLACE INTO commercials (name, file_path)
            VALUES (?, ?)
        """,
            (name, file_path),
        )
        self.conn.commit()

    def generate_ai_speech(
        self, prompt: str, song: Song, include_dark_joke: bool = False
    ):
        if len(song.previous_intros) >= 5:
            intro_text, intro_file_path, play_count = random.choice(
                song.previous_intros
            )
            print(f"Using existing intro: {intro_text}")

            # Increment play count
            play_count += 1
            self.cursor.execute(
                """
                UPDATE intros
                SET play_count = ?
                WHERE intro_file_path = ?
            """,
                (play_count, intro_file_path),
            )
            self.conn.commit()

            # Archive intro if it has been played 10 times
            if play_count >= 10:
                self.cursor.execute(
                    """
                    UPDATE intros
                    SET archived = 1
                    WHERE intro_file_path = ?
                """,
                    (intro_file_path,),
                )
                self.conn.commit()
                song.previous_intros = [
                    intro
                    for intro in song.previous_intros
                    if intro[1] != intro_file_path
                ]

            return intro_file_path

        previous_intros = ", ".join(
            [intro[0] for intro in song.previous_intros[-3:]]
        )  # Last 3 intros for context

        system_message = (
            "You are Nadya Nadell 'The Russian Mistress' a radio DJ for DSFM (Dagger Spell FM), which only plays music by the artist 'Dagger Spell'. "
            "Your introductions should be short and witty, and occasionally include dark humor related to the next song's subject."
            "You are known for your gothic style and seductive word play."
            "You speak in Russian, and English with a Russian accent."
            "Avoid repeating previous introductions."
        )

        user_message = (
            f"Introduce the song '{song.title}' by {song.artist}. "
            f"Theme: {song.theme}. Style: {song.style}. "
            f"Previous intros: [{previous_intros}]. "
            f"{'Include a dark joke related to the songs subject.' if include_dark_joke else ''}"
        )

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ]
        print(f"Messages:{messages}")
        # Switch to using Ollama API for AI responses to reduce costs in development
        response = self.client.chat(
            model="llama3.2:latest", messages=messages, stream=False
        )
        # response = client.chat.completions.create(
        #     model="gpt-4o-mini", messages=messages, max_tokens=150
        # )
        # intro_text = response.choices[0].message.content.strip()
        intro_text = response["message"]["content"]
        print(f"AI: {intro_text}")

        # Generate a unique file name using the song name and a timestamp
        timestamp = int(time.time())
        intro_file_path = self.text_to_speech(
            intro_text, f"intros/{song.title}_{timestamp}.mp3"
        )
        song.previous_intros.append((intro_text, intro_file_path, 0))

        self.cursor.execute(
            """
            INSERT INTO intros (song_title, intro_text, intro_file_path, play_count)
            VALUES (?, ?, ?, ?)
        """,
            (song.title, intro_text, intro_file_path, 0),
        )
        self.conn.commit()

        return intro_file_path

    def text_to_speech(self, text: str, file_path: str = "ai_speech.mp3"):
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # use elevenlabs API for text to speech
        data = self.tts.generate(
            text=text,
            voice=Voice(voice_id="GCPLhb1XrVwcoKUJYcvz"),
            model="eleven_multilingual_v2",
        )
        # raise the pitch of the voice by 2 semitones

        save(data, file_path)
        # tts = gtts.gTTS(text)
        # do we need to give this a full path? so we know where it is saved?
        # tts.save(file_path)
        return file_path

    def play_audio(self, audio):
        pygame.mixer.init()
        pygame.init()

        pygame.mixer.music.load(audio)

        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    def build_playlist(self):
        while True:
            with self.queue_lock:
                if (
                    len(self.playlist_queue) < 9
                ):  # Ensure there are at least 3 songs in the queue
                    songs = list(self.music_library.values())
                    random.shuffle(songs)
                    selected_songs = []
                    while len(selected_songs) < 3:
                        song = songs.pop()
                        if song not in selected_songs:
                            selected_songs.append(song)
                    for song in selected_songs:
                        include_dark_joke = (
                            random.random() < 0.2
                        )  # 20% chance for a dark joke
                        intro_file_path = self.generate_ai_speech(
                            f"Introduce the song {song.title}", song, include_dark_joke
                        )
                        self.playlist_queue.append(intro_file_path)
                        self.playlist_queue.append(song.file_path)
                        if (
                            len(self.commercials) > 0 and random.random() < 0.2
                        ):  # 20% chance for a commercial
                            commercial = random.choice(self.commercials)
                            self.playlist_queue.append(commercial.file_path)
            time.sleep(1)  # Sleep for a short time before checking the queue again

    def run_station(self):
        playlist_thread = threading.Thread(target=self.build_playlist)
        playlist_thread.daemon = True
        playlist_thread.start()

        while True:
            with self.queue_lock:
                if self.playlist_queue:
                    audio = self.playlist_queue.popleft()
                else:
                    audio = None
            if audio:
                self.play_audio(audio)
            # tenth of a second delay between songs
            time.sleep(0.01)
