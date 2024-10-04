# Music Flow Radio

## Project Overview

Music Flow Radio is an AI-powered internet streaming radio service. It uses AI to generate engaging introductions for songs, create a dynamic playlist, and even produce AI-generated commercials. This project aims to transform the proof-of-concept local radio station into a full-fledged web-based streaming service.

## System Architecture

The system will consist of the following components:

1. **Backend (Flask)**

   - Handles audio streaming
   - Manages the playlist and song database
   - Integrates with many LLMs for AI-generated content
     - Ollama
     - OpenAI
     - Anthropic
     - More to come!
   - Provides RESTful API for frontend communication

2. **Frontend (React)**

   - User interface for listeners and admins alike
   - Admin panel for managing songs, playlists, and station settings
   - Real-time display of current song and AI-generated introductions

3. **Database (SQLite)**

   - Stores song metadata, playlists, and user information

4. **Audio Processing**

   - Handles audio file manipulation and streaming

5. **AI Integration**

   - Generates song introductions and commercial content
   - Text-to-Speech for natural-sounding DJ voice

6. **Streaming Server**
   - Broadcasts audio stream to listeners

## Detailed Component Design

### 1. Backend (Flask)

#### Key Features:

- RESTful API for song management, playlist creation, and station control
- WebSocket for real-time updates (current song, listener count)
- Integrates with many LLMs for AI-generated content
- Audio file processing and streaming

#### Main Routes:

- `/api/songs` - CRUD operations for songs
- `/api/playlists` - Manage playlists
- `/api/stream` - Audio streaming endpoint
- `/api/station` - Station control (start, stop, skip)

#### Libraries:

- Flask
- Flask-RESTful
- Flask-SocketIO
- SQLAlchemy
- PyDub

### 2. Frontend (React)

#### Key Features:

- Responsive design for desktop and mobile
- Real-time display of current song and next up
- User authentication for admin features
- Admin panel for song and playlist management

#### Main Components:

- `Player` - Audio player with controls
- `NowPlaying` - Displays current song and AI introduction
- `Playlist` - Shows upcoming songs
- `Admin` - Song and playlist management interface

#### Libraries:

- React
- Redux for state management
- Material-UI for styling
- Axios for API calls

### 3. Database (SQLite)

#### Tables:

- `Songs` - Stores song metadata
- `Playlists` - Manages playlists
- `Users` - User authentication for admin access

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
    songs TEXT  -- JSON string of song IDs
);

CREATE TABLE Users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,
    is_admin BOOLEAN
);
```

### 4. Audio Processing

- Use PyDub for audio file manipulation
- Implement a custom audio streaming solution or integrate with existing libraries

### 5. AI Integration

#### Language Models (LLMs)

- To reduce cost during development, we will initially use Ollama
- After initial product development is complete, we will add other LLMs as soon as possible:
  - OpenAI
  - Anthropic
  - More to come!

#### Text-to-Speech (TTS)

- For a more natural-sounding DJ voice, we will incorporate various TTS options:
  - Initially: OpenVoice2 TTS hosted locally with a Gradio frontend
  - Future additions:
    - ElevenLabs
    - Other high-quality TTS services

#### Integration Strategy

- Implement a modular design to easily switch between different LLMs and TTS services
- Develop a caching mechanism to reduce API calls and improve performance
- Create a fallback system to ensure continuous operation if a primary service is unavailable

#### Cost Management

- Implement usage tracking and limits for third-party services
- Optimize prompt engineering to reduce token usage with LLMs
- Explore batch processing for TTS generation during low-usage periods

#### Customization

- Allow admin users to select preferred LLM and TTS combinations for different types of content
- Implement voice customization options where available (e.g., pitch, speed, emotion)

#### Future Enhancements

- Explore multi-modal AI models for generating accompanying visuals or sound effects
- Implement AI-driven content scheduling and playlist generation based on listener preferences and trends

### 6. Streaming Server

- Implement using Flask-SocketIO or a dedicated streaming server like Icecast

## Docker Configuration

Create separate containers for:

1. Flask backend
2. React frontend
3. SQLite database
4. Streaming server

Docker-compose file to orchestrate the containers:

```yaml
version: "3"
services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    volumes:
      - ./backend:/app
    environment:
      - FLASK_ENV=development
      - OPENAI_API_KEY=${OPENAI_API_KEY}

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
    depends_on:
      - backend

  database:
    image: keinos/sqlite3
    volumes:
      - ./data:/data

  streaming:
    image: moul/icecast
    ports:
      - "8000:8000"
    environment:
      - ICECAST_SOURCE_PASSWORD=${ICECAST_SOURCE_PASSWORD}
      - ICECAST_ADMIN_PASSWORD=${ICECAST_ADMIN_PASSWORD}
```

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

   - Implement or integrate a streaming solution
   - Develop audio processing pipeline for seamless playback

4. **Phase 4: AI Integration and Optimization**

   - Implement OpenVoice2 TTS integration
   - Refine AI-generated content
   - Implement caching and optimization strategies

5. **Phase 5: Docker and Deployment**

   - Create Dockerfiles for each component
   - Develop docker-compose configuration
   - Set up CI/CD pipeline for automated deployment

6. **Phase 6: Testing and Refinement**

   - Conduct thorough testing of all components
   - Optimize performance and user experience
   - Gather user feedback and iterate on the design

7. **Phase 7: Launch and Monitoring**
   - Deploy to production environment
   - Set up monitoring and logging
   - Develop a plan for ongoing maintenance and updates

## Conclusion

Music Flow Radio aims to revolutionize internet radio by leveraging AI to create a unique and engaging listening experience. This design document outlines the key components and development steps needed to bring this project to life. As development progresses, this document should be updated to reflect any changes or refinements to the overall design.

## Note on Licensing

All music broadcast on Music Flow Radio will be original content created by the project owner. This simplifies licensing concerns and allows for full control over the content and its presentation.
