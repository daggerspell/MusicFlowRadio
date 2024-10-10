# Music Flow Radio

## Project Overview

Music Flow Radio is an AI-powered internet streaming radio service. It uses AI to generate engaging introductions for songs and create dynamic playlists. This project aims to create a full-fledged web-based streaming service, moving beyond the initial proof-of-concept, primarily for personal use as a 24/7 AI-driven Twitch radio station.

## System Architecture

The system will consist of the following components:

1. **Backend (Flask)**

   - Handles audio streaming using Icecast or a similar free solution
   - Manages the playlist and song database
   - Integrates with multiple LLMs for AI-generated content
   - Provides RESTful API for frontend communication
   - Implements DJ scheduling system
   - Manages DJ-specific playlist building
   - Records detailed play history

2. **Frontend (React)**

   - Web-based user interface for listeners and admins
   - Admin panel for managing songs, playlists, and station settings
   - Real-time display of current song and AI-generated introductions
   - DJ management interface

3. **Database (PostgreSQL)**

   - Stores song metadata, playlists, and user information
   - Maintains DJ schedules and preferences
   - Records detailed play history

4. **Audio Processing**

   - Handles audio file manipulation and streaming
   - Primary tool: PyDub (with alternatives like pydub-stubs or pydub-next as backup options)

5. **AI Integration**

   - Generates song introductions
   - Creates DJ-specific content, including show intros and outros
   - Text-to-Speech for natural-sounding DJ voices
   - Implements cost-saving measures for ElevenLabs usage

6. **Streaming Server**
   - Broadcasts audio stream to listeners using Icecast or similar

## Detailed Component Design

### 1. Backend (Flask)

#### Key Features:

- RESTful API for song management, playlist creation, and station control
- WebSocket for real-time updates (current song, listener count)
- Integration with multiple LLMs for AI-generated content
- Audio file processing and streaming
- DJ scheduling system
- DJ-specific playlist building
- Detailed play history recording

#### Main Routes:

- `/api/songs` - CRUD operations for songs
- `/api/playlists` - Manage playlists
- `/api/stream` - Audio streaming endpoint
- `/api/station` - Station control (start, stop, skip)
- `/api/djs` - Manage DJ schedules and preferences
- `/api/history` - Access play history

#### Libraries:

- Flask
- Flask-RESTful
- Flask-SocketIO
- SQLAlchemy
- PyDub (with alternatives like pydub-stubs or pydub-next as backup)
- Icecast-py (or similar for streaming)

### 2. Frontend (React)

#### Key Features:

- Responsive web-based design for desktop and mobile
- Real-time display of current song and next up
- User authentication for admin features
- Admin panel for song and playlist management
- DJ management interface
- Station analytics and history viewer

#### Main Components:

- `Player` - Audio player with controls
- `NowPlaying` - Displays current song and AI introduction
- `Playlist` - Shows upcoming songs
- `Admin` - Song, playlist, and DJ management interface
- `Analytics` - Display station statistics and play history

#### Libraries:

- React
- Redux for state management
- Material-UI or Tailwind CSS for styling
- Axios for API calls

### 3. Database (PostgreSQL)

#### Tables:

- `Albums` - Stores album metadata
- `Songs` - Stores song metadata
- `Playlists` - Manages playlists
- `Users` - User authentication for admin access
- `DJs` - Stores DJ information and preferences
- `Schedules` - Manages DJ schedules
- `PlayHistory` - Records detailed play history
- `Intros` - Stores AI-generated song introductions

#### Schema (simplified):

```sql
CREATE TABLE Albums (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    artist TEXT NOT NULL,
    release_date DATE,
    album_art_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Songs (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    artist TEXT NOT NULL,
    album_id INTEGER,
    track_number INTEGER,
    file_path TEXT NOT NULL,
    youtube_url TEXT,
    duration INTEGER NOT NULL,
    times_played INTEGER DEFAULT 0,
    release_date DATE,
    theme TEXT,
    style TEXT,
    lyrics TEXT,
    twitter_post TEXT,
    song_art_url TEXT,  -- For singles or songs without an album
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(album_id) REFERENCES Albums(id)
);

CREATE TABLE Playlists (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    dj_id INTEGER,
    songs JSONB,  -- JSON array of song IDs
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(dj_id) REFERENCES DJs(id)
);

CREATE TABLE Users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE DJs (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    voice_id TEXT NOT NULL,
    show_name TEXT NOT NULL,
    preferences JSONB,  -- JSON object of DJ preferences
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Schedules (
    id SERIAL PRIMARY KEY,
    dj_id INTEGER NOT NULL,
    day_of_week TEXT NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(dj_id) REFERENCES DJs(id)
);

CREATE TABLE PlayHistory (
    id SERIAL PRIMARY KEY,
    song_id INTEGER NOT NULL,
    dj_id INTEGER NOT NULL,
    start_time TIMESTAMP NOT NULL,
    duration INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(song_id) REFERENCES Songs(id),
    FOREIGN KEY(dj_id) REFERENCES DJs(id)
);

CREATE TABLE Intros (
    id SERIAL PRIMARY KEY,
    song_id INTEGER NOT NULL,
    intro_text TEXT NOT NULL,
    intro_audio_path TEXT NOT NULL,
    times_used INTEGER DEFAULT 0,
    is_retired BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(song_id) REFERENCES Songs(id)
);
```

### 4. Audio Processing

- Primary tool: PyDub for audio file manipulation
- Backup options: pydub-stubs or pydub-next if issues arise with PyDub
- Implement streaming solution using Icecast or similar free alternative

### 5. AI Integration

#### Language Models (LLMs)

- Initially use Ollama for development, with flexibility to use various models as they become available
- Plan to add support for:
  - OpenAI
  - Anthropic
  - Groq
  - Other LLMs as needed

#### Text-to-Speech (TTS)

- Initially: OpenVoice2 TTS hosted locally
- Future addition: ElevenLabs

#### Integration Strategy

- Modular design for easy switching between LLMs and TTS services
- Caching mechanism to reduce API calls
- Fallback system for service unavailability

#### DJ-Specific Content

- Generate show intros and outros
- Create personalized song introductions based on DJ preferences
- Ensure DJs mention at least once every two hours that the station is run entirely on AI and only occasionally managed by a live person

#### Cost-Saving Measures for ElevenLabs

- Limit the number of intros created per song
- Set a maximum number of uses for each intro before retirement
- Implement a rotation system for intro usage

### 6. Streaming Server

- Implement using Icecast or similar free streaming solution
- Ensure compatibility with various client players

## Development Roadmap

1. **Phase 1: Backend Development**

   - Set up Flask project structure
   - Implement database models and migrations (PostgreSQL)
   - Develop RESTful API for song and playlist management
   - Integrate Ollama for content generation
   - Implement audio file processing with PyDub (test alternatives if needed)
   - Set up Icecast (or alternative) for audio streaming
   - Implement basic TTS functionality with OpenVoice2

2. **Phase 2: Frontend Development**

   - Set up React project
   - Develop main components (Player, NowPlaying, Playlist)
   - Implement admin interface for song and playlist management
   - Integrate with backend API

3. **Phase 3: Streaming and Audio Processing**

   - Integrate Icecast (or chosen alternative) with the Flask backend
   - Develop audio processing pipeline for seamless playback
   - Implement stream metadata updates

4. **Phase 4: AI Integration and Optimization**

   - Refine OpenVoice2 TTS integration
   - Implement ElevenLabs integration with cost-saving measures
   - Refine AI-generated content quality
   - Implement caching and optimization strategies for AI-generated content

5. **Phase 5: DJ System Implementation**

   - Develop DJ scheduling system
   - Implement DJ-specific playlist building
   - Create show intro and outro generation

6. **Phase 6: History and Analytics**

   - Implement detailed play history recording
   - Develop basic analytics features

7. **Phase 7: Testing and Refinement**

   - Conduct thorough testing at the end of each development phase
   - Ensure each phase has a working output before moving to the next
   - Perform final comprehensive testing of all components
   - Optimize performance and user experience
   - Gather user feedback and iterate on the design

8. **Phase 8: Launch and Monitoring**
   - Deploy to production environment
   - Set up monitoring and logging
   - Develop a plan for ongoing maintenance and updates

## Future Enhancements

- Integration with popular streaming services for user requests
- Advanced analytics and listener engagement features
- Mobile app for listeners
- AI-driven content scheduling based on listener preferences

## Note on Project Scope

This project is currently developed as a personal project and is not open for contributions at this stage. The primary goal is to create a 24/7 AI-driven Twitch radio station for personal use.

## Technology Stack

- Backend: Flask
- Frontend: React (Note: Additional assistance may be required for React development)
- Database: PostgreSQL
- Streaming: Icecast

## Scalability

While PostgreSQL has been chosen for better scalability, the current focus is on personal use. Scalability considerations will be kept in mind during development but are not a primary concern at this stage.

## Security and Licensing

Initial development will focus on functionality rather than advanced security measures. Open-source licensing will be applied where legally required. Users of this software must have rights to broadcast music, as it was developed for personal use with self-created music.

## Conclusion

Music Flow Radio aims to create a unique and engaging internet radio experience by leveraging AI technology and personalized DJ content. This README outlines the key components and development steps needed to bring this project to life. As development progresses, this document should be updated to reflect any changes or refinements to the overall design.
