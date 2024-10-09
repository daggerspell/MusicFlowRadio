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
from objects.Personality import Nadya, Guss, Jules, Lenny, Perta
from datetime import datetime, timedelta


class AIRadioStation:
    def __init__(self):
        self.music_library: Dict[str, Song] = {}
        self.commercials: List[Commercial] = []
        self.playlist_queue: deque = deque()
        self.queue_lock = threading.Lock()
        self.host_schedule: List[Dict] = []
        self.hosts = {
            "Nadya": Nadya(),
            "Guss": Guss(),
            "Jules": Jules(),
            "Lenny": Lenny(),
            "Perta": Perta(),
        }
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
        self.generate_host_schedule()
        self.current_host = self.get_current_host()
        self.generate_and_store_show_intros()

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
                twitter_post TEXT,
                play_count INTEGER DEFAULT 0
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
                host_name TEXT,
                FOREIGN KEY(song_title) REFERENCES songs(title)
            )
        """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS host_schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                host_name TEXT,
                start_time TEXT,
                end_time TEXT,
                day_of_week TEXT
            )
        """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS show_intros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                host_name TEXT,
                show_name TEXT,
                intro_text TEXT,
                audio_file_path TEXT,
                created_at TIMESTAMP
            )
        """
        )
        self.conn.commit()

    def load_data(self):
        self.cursor.execute("SELECT * FROM songs")
        songs = self.cursor.fetchall()
        for song in songs:
            title, artist, file_path, theme, style, lyrics, twitter_post, play_count = (
                song
            )
            self.music_library[title] = Song(
                title, artist, file_path, theme, style, lyrics, twitter_post, play_count
            )

        self.cursor.execute("SELECT * FROM commercials")
        commercials = self.cursor.fetchall()
        for commercial in commercials:
            name, file_path = commercial
            self.commercials.append(Commercial(name, file_path))

        current_host = self.get_current_host()
        if current_host:
            self.cursor.execute(
                "SELECT * FROM intros WHERE archived = 0 AND host_name = ?",
                (current_host,),
            )
        else:
            self.cursor.execute("SELECT * FROM intros WHERE archived = 0")

        intros = self.cursor.fetchall()
        for intro in intros:
            (
                _,
                song_title,
                intro_text,
                intro_file_path,
                play_count,
                archived,
                host_name,
            ) = intro
            if song_title in self.music_library:
                self.music_library[song_title].previous_intros.append(
                    (intro_text, intro_file_path, play_count, host_name)
                )

        self.cursor.execute("SELECT * FROM host_schedule")
        schedule = self.cursor.fetchall()
        for entry in schedule:
            _, host_name, start_time, end_time, day_of_week = entry
            self.host_schedule.append(
                {
                    "host_name": host_name,
                    "start_time": start_time,
                    "end_time": end_time,
                    "day_of_week": day_of_week,
                }
            )

    def generate_host_schedule(self):
        # get the schedule from the database and store it in the host_schedule list
        self.cursor.execute("SELECT * FROM host_schedule")
        schedule = self.cursor.fetchall()

        # # Clear existing schedule
        # self.cursor.execute("DELETE FROM host_schedule")

        # # Define host schedules
        # hosts = [
        #     {
        #         "name": "Nadya",
        #         "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        #         "shifts": [("22:00", "05:00"), ("00:00", "05:00")],
        #     },
        #     {
        #         "name": "Guss",
        #         "days": ["Wed", "Thu", "Fri", "Sat"],
        #         "shifts": [("16:00", "00:00")],
        #     },
        #     {
        #         "name": "Lenny",
        #         "days": ["Wed", "Thu", "Fri", "Sat"],
        #         "shifts": [("14:00", "16:00")],
        #     },
        # ]

        # # Add Nadya's, Guss's, and Lenny's shifts to the schedule
        # for host in hosts:
        #     for day in host["days"]:
        #         for shift in host["shifts"]:
        #             start_time = datetime.strptime(shift[0], "%H:%M")
        #             end_time_str = shift[1]
        #             if end_time_str == "00:00":
        #                 end_time_str = "00:00"
        #                 end_time = datetime.strptime(end_time_str, "%H:%M") + timedelta(
        #                     days=1
        #                 )
        #             else:
        #                 end_time = datetime.strptime(end_time_str, "%H:%M")
        #             if end_time < start_time:
        #                 end_time += timedelta(days=1)
        #             self.cursor.execute(
        #                 """
        #                 INSERT INTO host_schedule (host_name, start_time, end_time, day_of_week)
        #                 VALUES (?, ?, ?, ?)
        #             """,
        #                 (
        #                     host["name"],
        #                     start_time.strftime("%H:%M:%S"),
        #                     end_time.strftime("%H:%M:%S"),
        #                     day,
        #                 ),
        #             )
        #             self.conn.commit()

        # # Define remaining hours for Jules and Lenny
        # remaining_hours = [
        #     {"start_time": "05:00", "end_time": "10:00"},
        #     {"start_time": "10:00", "end_time": "14:00"},
        #     {"start_time": "16:00", "end_time": "22:00"},
        # ]

        # # Assign Jules and Lenny's shifts
        # for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
        #     for i, hours in enumerate(remaining_hours):
        #         start_time = datetime.strptime(hours["start_time"], "%H:%M")
        #         end_time = datetime.strptime(hours["end_time"], "%H:%M")
        #         if end_time < start_time:
        #             end_time += timedelta(days=1)

        #         # Check if the time slot is already covered
        #         self.cursor.execute(
        #             """
        #             SELECT COUNT(*) FROM host_schedule
        #             WHERE day_of_week = ? AND (
        #                 (start_time <= ? AND end_time > ?) OR
        #                 (start_time < ? AND end_time >= ?)
        #             )
        #         """,
        #             (
        #                 day,
        #                 start_time.strftime("%H:%M:%S"),
        #                 start_time.strftime("%H:%M:%S"),
        #                 end_time.strftime("%H:%M:%S"),
        #                 end_time.strftime("%H:%M:%S"),
        #             ),
        #         )
        #         count = self.cursor.fetchone()[0]
        #         if count == 0:
        #             # Alternate between Jules and Lenny
        #             host_name = "Lenny" if i % 2 == 0 else "Jules"
        #             self.cursor.execute(
        #                 """
        #                 INSERT INTO host_schedule (host_name, start_time, end_time, day_of_week)
        #                 VALUES (?, ?, ?, ?)
        #             """,
        #                 (
        #                     host_name,
        #                     start_time.strftime("%H:%M:%S"),
        #                     end_time.strftime("%H:%M:%S"),
        #                     day,
        #                 ),
        #             )
        #             self.conn.commit()

    def get_current_host(self):
        # This should return the personality object of the current host
        now = datetime.now()
        current_time = now.time()
        current_day = now.strftime("%a")
        previous_day = (now - timedelta(days=1)).strftime("%a")

        # print(f"Current time: {current_time}, Current day: {current_day}")
        # print(f"Host schedule: {self.host_schedule}")

        for entry in self.host_schedule:
            start_time = datetime.strptime(entry["start_time"], "%H:%M:%S").time()
            end_time = datetime.strptime(entry["end_time"], "%H:%M:%S").time()

            # Check if the current time falls within the shift
            if entry["day_of_week"] == current_day:
                if start_time <= end_time:
                    if start_time <= current_time <= end_time:
                        return self.hosts.get(entry["host_name"])
                else:  # Overnight shift
                    if current_time >= start_time or current_time <= end_time:
                        return self.hosts.get(entry["host_name"])

            # Check if the current time falls within an overnight shift from the previous day
            if entry["day_of_week"] == previous_day and start_time > end_time:
                if current_time <= end_time:
                    return self.hosts.get(entry["host_name"])

        return None

    def add_song(self, file_path: str):
        song_info = self.extract_song_info(file_path)
        if song_info:
            self.music_library[song_info.title] = song_info
            self.cursor.execute(
                """
                INSERT OR REPLACE INTO songs (title, artist, file_path, theme, style, lyrics, twitter_post, play_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    song_info.title,
                    song_info.artist,
                    song_info.file_path,
                    song_info.theme,
                    song_info.style,
                    song_info.lyrics,
                    song_info.twitter_post,
                    song_info.play_count,
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
        self, prompt: str, song: Song, include_dark_joke: bool, cursor, conn
    ):
        current_host = self.get_current_host()
        if not current_host:
            raise ValueError("No current host found")

        # Filter intros to only include those from the current host
        host_specific_intros = [
            intro for intro in song.previous_intros if intro[3] == current_host.name
        ]

        if len(host_specific_intros) >= 3:
            intro_text, intro_file_path, play_count, host_name = random.choice(
                host_specific_intros
            )
            print(f"Using existing intro: {intro_text}")

            # Increment play count
            play_count += 1
            cursor.execute(
                """
                UPDATE intros
                SET play_count = ?
                WHERE intro_file_path = ?
            """,
                (play_count, intro_file_path),
            )
            conn.commit()

            # Archive intro if it has been played 20 times
            if play_count >= 20:
                cursor.execute(
                    """
                    UPDATE intros
                    SET archived = 1
                    WHERE intro_file_path = ?
                """,
                    (intro_file_path,),
                )
                conn.commit()
                song.previous_intros = [
                    intro
                    for intro in song.previous_intros
                    if intro[1] != intro_file_path
                ]

            return intro_file_path

        previous_intros = ", ".join(
            [intro[0] for intro in host_specific_intros[-3:]]
        )  # Last 3 intros for context

        print(f"Current host: {current_host.name}")
        system_message = current_host.system_message

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
        intro_text = response["message"]["content"]
        print(f"AI: {intro_text}")

        # Generate a unique file name using the song name and a timestamp
        timestamp = int(time.time())
        intro_file_path = self.text_to_speech(
            intro_text, f"intros/{song.title}_{timestamp}.mp3"
        )
        song.previous_intros.append((intro_text, intro_file_path, 0, current_host.name))

        cursor.execute(
            """
            INSERT INTO intros (song_title, intro_text, intro_file_path, play_count, host_name)
            VALUES (?, ?, ?, ?, ?)
        """,
            (song.title, intro_text, intro_file_path, 0, current_host.name),
        )
        conn.commit()

        return intro_file_path

    def generate_and_store_show_intros(self):
        # Ensure the show_intros directory exists
        os.makedirs("show_intros", exist_ok=True)

        for personality in self.hosts.values():
            # Check if there is already a show intro for this personality
            self.cursor.execute(
                "SELECT COUNT(*) FROM show_intros WHERE host_name = ?",
                (personality.name,),
            )
            count = self.cursor.fetchone()[0]
            if count == 0:
                # Generate show intro
                # this can't be done on the personailty class as it needs to be done on the radio station class
                messages = [
                    {"role": "system", "content": personality.system_message},
                    {
                        "role": "user",
                        "content": f"{personality.name}, Generate a show intro for you and your show {personality.show_name}.",
                    },
                ]

                show_intro_response = self.client.chat(
                    model=personality.model, messages=messages, stream=False
                )

                intro_text = show_intro_response["message"]["content"]
                timestamp = int(time.time())
                audio_file_path = f"show_intros/{personality.name}-{personality.show_name}_{timestamp}.mp3"

                # Generate the audio file
                self.text_to_speech(intro_text, audio_file_path, personality.voice_id)

                # Store the intro in the database
                self.cursor.execute(
                    """
                    INSERT INTO show_intros (host_name, show_name, intro_text, audio_file_path, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        personality.name,
                        personality.show_name,
                        intro_text,
                        audio_file_path,
                        datetime.now(),
                    ),
                )
                self.conn.commit()

    def text_to_speech(
        self, text: str, file_path: str = "ai_speech.mp3", voice_id: str = None
    ):
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if voice_id is None:
            voice_id = self.current_host.voice_id

        # use elevenlabs API for text to speech
        data = self.tts.generate(
            text=text,
            voice=Voice(voice_id=voice_id),
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

        # Increment play count if the audio is a song
        for song in self.music_library.values():
            if song.file_path == audio:
                song.play_count += 1
                self.cursor.execute(
                    "UPDATE songs SET play_count = ? WHERE title = ?",
                    (song.play_count, song.title),
                )
                self.conn.commit()
                break

    def build_playlist(self):
        # Create a new SQLite connection and cursor for this thread
        conn = sqlite3.connect("musicflowradio.db")
        cursor = conn.cursor()

        while True:
            with self.queue_lock:
                if (
                    len(self.playlist_queue) < 9
                ):  # Ensure there are at least 3 songs in the queue
                    songs = list(self.music_library.values())
                    songs.sort(
                        key=lambda song: song.play_count
                    )  # Sort songs by play count
                    selected_songs = []
                    while len(selected_songs) < 3:
                        song = songs.pop(0)  # Select the least played song
                        if song not in selected_songs:
                            selected_songs.append(song)
                    for song in selected_songs:
                        include_dark_joke = (
                            random.random() < 0.2
                        )  # 20% chance for a dark joke
                        intro_file_path = self.generate_ai_speech(
                            f"Introduce the song {song.title}",
                            song,
                            include_dark_joke,
                            cursor,
                            conn,
                        )
                        self.playlist_queue.append(intro_file_path)
                        self.playlist_queue.append(song.file_path)
                        if (
                            len(self.commercials) > 0 and random.random() < 0.2
                        ):  # 20% chance for a commercial
                            commercial = random.choice(self.commercials)
                            self.playlist_queue.append(commercial.file_path)
            time.sleep(1)  # Sleep for a short time before checking the queue again

        # Close the connection when done
        conn.close()

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
