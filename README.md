# Music Flow Radio

## Project Overview

Music Flow Radio is an AI-powered internet streaming radio service. It uses AI to generate engaging introductions for songs, create dynamic playlists, and even produce AI-generated commercials. This project aims to create a full-fledged web-based streaming service, moving beyond the initial proof-of-concept.

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

3. **Database (SQLite)**

   - Stores song metadata, playlists, and user information
   - Maintains DJ schedules and preferences
   - Records detailed play history

4. **Audio Processing**

   - Handles audio file manipulation and streaming

5. **AI Integration**

   - Generates song introductions and commercial content
   - Creates DJ-specific content, including show intros and outros
   - Text-to-Speech for natural-sounding DJ voices

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
- PyDub
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

### 3. Database (SQLite)

#### Tables:

- `Songs` - Stores song metadata
- `Playlists` - Manages playlists
- `Users` - User authentication for admin access
- `DJs` - Stores DJ information and preferences
- `Schedules` - Manages DJ schedules
- `PlayHistory` - Records detailed play history

#### Schema (simplified):

```sql
CREATE TABLE Songs (
    id INTEGER PRIMARY KEY,
    title TEXT,
    artist TEXT,
    file_path TEXT,
    theme TEXT,
    style TEXT,
    lyrics TEXT,
    twitter_post TEXT
);

CREATE TABLE Playlists (
    id INTEGER PRIMARY KEY,
    name TEXT,
    dj_id INTEGER,
    songs TEXT,  -- JSON string of song IDs
    FOREIGN KEY(dj_id) REFERENCES DJs(id)
);

CREATE TABLE Users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,
    is_admin BOOLEAN
);

CREATE TABLE DJs (
    id INTEGER PRIMARY KEY,
    name TEXT,
    voice_id TEXT,
    show_name TEXT,
    preferences TEXT  -- JSON string of DJ preferences
);

CREATE TABLE Schedules (
    id INTEGER PRIMARY KEY,
    dj_id INTEGER,
    day_of_week TEXT,
    start_time TEXT,
    end_time TEXT,
    FOREIGN KEY(dj_id) REFERENCES DJs(id)
);

CREATE TABLE PlayHistory (
    id INTEGER PRIMARY KEY,
    file_path TEXT,
    dj_id INTEGER,
    start_time DATETIME,
    duration INTEGER,
    FOREIGN KEY(dj_id) REFERENCES DJs(id)
);
```

### 4. Audio Processing

- Use PyDub for audio file manipulation
- Implement streaming solution using Icecast or similar free alternative

### 5. AI Integration

#### Language Models (LLMs)

- Initially use Ollama for development
- Plan to add support for:
  - OpenAI
  - Anthropic
  - Other LLMs as needed

#### Text-to-Speech (TTS)

- Initially: OpenVoice2 TTS hosted locally
- Future additions:
  - ElevenLabs
  - Other high-quality TTS services

#### Integration Strategy

- Modular design for easy switching between LLMs and TTS services
- Caching mechanism to reduce API calls
- Fallback system for service unavailability

#### DJ-Specific Content

- Generate show intros and outros
- Create personalized song introductions based on DJ preferences

### 6. Streaming Server

- Implement using Icecast or similar free streaming solution
- Ensure compatibility with various client players

## Development Roadmap

1. **Phase 1: Backend Development**

   - Set up Flask project structure
   - Implement database models and migrations
   - Develop RESTful API for song and playlist management
   - Integrate Ollama for content generation
   - Implement basic audio streaming

2. **Phase 2: Frontend Development**

   - Set up React project
   - Develop main components (Player, NowPlaying, Playlist)
   - Implement admin interface for song and playlist management
   - Integrate with backend API

3. **Phase 3: Streaming and Audio Processing**

   - Implement or integrate a streaming solution (Icecast)
   - Develop audio processing pipeline for seamless playback

4. **Phase 4: AI Integration and Optimization**

   - Implement OpenVoice2 TTS integration
   - Refine AI-generated content
   - Implement caching and optimization strategies

5. **Phase 5: DJ System Implementation**

   - Develop DJ scheduling system
   - Implement DJ-specific playlist building
   - Create show intro and outro generation

6. **Phase 6: History and Analytics**

   - Implement detailed play history recording
   - Develop basic analytics features

7. **Phase 7: Testing and Refinement**

   - Conduct thorough testing of all components
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

## Conclusion

Music Flow Radio aims to create a unique and engaging internet radio experience by leveraging AI technology and personalized DJ content. This README outlines the key components and development steps needed to bring this project to life. As development progresses, this document should be updated to reflect any changes or refinements to the overall design.

## Note on Music Licensing

Users of this software must have rights to broadcast music. The software was developed for personal use with self-created music.
