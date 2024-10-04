import random
import time
import pygame
import os
import tempfile
from pydub import AudioSegment
from openai import OpenAI
import gtts
from typing import List, Dict
from dotenv import load_dotenv
import mutagen
import markdown
import re


# Load from .env file OPENAI_API_KEY
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set a custom temp directory to avoid permission issues
tempfile.tempdir = os.path.join(os.getcwd(), "temp_audio")

# Ensure the directory exists
os.makedirs(tempfile.tempdir, exist_ok=True)


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


class Commercial:
    def __init__(self, name: str, file_path: str):
        self.name = name
        self.file_path = file_path


class AIRadioStation:
    def __init__(self):
        self.music_library: Dict[str, Song] = {}
        self.commercials: List[Commercial] = []

    def add_song(self, file_path: str):
        song_info = self.extract_song_info(file_path)
        if song_info:
            self.music_library[song_info.title] = song_info
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

    def add_commercial(self, name: str, file_path: str):
        self.commercials.append(Commercial(name, file_path))

    def generate_ai_speech(
        self, prompt: str, song: Song, include_dark_joke: bool = False
    ):
        previous_intros = ", ".join(
            song.previous_intros[-3:]
        )  # Last 3 intros for context

        system_message = (
            "You are a radio DJ for DSFM (Dagger Spell FM), which only plays music by the artist 'Dagger Spell'. "
            "Your introductions should be witty, engaging, and occasionally include dark humor related to the song's subject. "
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

        response = client.chat.completions.create(
            model="gpt-4o-mini", messages=messages, max_tokens=150
        )

        intro_text = response.choices[0].message.content.strip()
        print(f"AI: {intro_text}")
        song.previous_intros.append(intro_text)
        return intro_text

    def text_to_speech(self, text: str) -> AudioSegment:
        tts = gtts.gTTS(text)
        # do we need to give this a full path? so we know where it is saved?
        tts.save("ai_speech.mp3")
        return "ai_speech.mp3"

    def play_audio(self, audio):
        pygame.mixer.init()
        pygame.init()

        pygame.mixer.music.load(audio)

        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    def run_station(self):
        while True:
            song = random.choice(list(self.music_library.values()))
            song_audio = song.file_path

            include_dark_joke = random.random() < 0.2  # 20% chance for a dark joke
            intro_text = self.generate_ai_speech(
                f"Introduce the song {song.title}", song, include_dark_joke
            )
            intro_audio = self.text_to_speech(intro_text)

            self.play_audio(intro_audio)
            self.play_audio(song_audio)

            if random.random() < 0.2:  # 20% chance for a commercial
                commercial = random.choice(self.commercials)
                commercial_audio = AudioSegment.from_mp3(commercial.file_path)
                self.play_audio(commercial_audio)
            # tenth of a second delay between songs
            time.sleep(0.01)


class RadioStationUI:
    def __init__(self, station: AIRadioStation):
        self.station = station

    def run(self):
        while True:
            print("\nDagger Spell FM Management Console")
            print("1. Add Song")
            print("2. Remove Song")
            print("3. Add Commercial")
            print("4. Start Radio")
            print("5. Exit")

            choice = input("Enter your choice: ")

            if choice == "1":
                file_path = input("Enter file path: ")
                self.station.add_song(file_path)
            elif choice == "2":
                title = input("Enter song title to remove: ")
                self.station.remove_song(title)
            elif choice == "3":
                name = input("Enter commercial name: ")
                file_path = input("Enter file path: ")
                self.station.add_commercial(name, file_path)
            elif choice == "4":
                print("Starting radio station...")
                self.station.run_station()
            elif choice == "5":
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please try again.")


if __name__ == "__main__":
    radio = AIRadioStation()
    ui = RadioStationUI(radio)
    ui.run()
