# Concert Buddy

Concert Buddy is an AI-powered concert planning assistant that helps you prep for your next live concert experience. Whether you want to find upcoming concerts, compare ticket options, or build a playlist based on likely setlists, Concert Buddy gives you one place to do it.

- :robot: **Discover upcoming concerts** with AI-assisted search
- :ticket: **Find ticket information** from trusted ticket sources
- :musical_note: **Generate Spotify playlists automatically** based on recent live setlists

## How It Works

Concert Buddy is powered by a team of specialized agents built using the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/).

These agents are integrated with external music and live-event services:
- [setlist.fm](https://www.setlist.fm/) is used to retreive data for recent live performance setlists.
- Currently supports [Spotify](https://open.spotify.com/) integration for automatic Spotify playlist creation.

Together, these pieces let Concert Buddy move from a simple user request to a practical concert-preparation workflow: discover a show, gather ticket info, and generate a playlist based on recent live performances.

## Getting Started

Before getting started, you will need to setup and gather your credentials for the following APIs:
  - [OpenAI](https://platform.openai.com/)
  - [setlist.fm](https://api.setlist.fm/docs/1.0/index.html)
  - [Spotify](https://developer.spotify.com/documentation/web-api)

The repository includes an example environment file at [`.env.example`](.env.example).

### 1. Copy the example file

From the project root, run:

```bash
cp .env.example .env
```

### 2. Fill in your credentials

Edit [`.env`](.env) and provide real values for all required keys:

```env
OPENAI_API_KEY=sk-your-openai-api-key
SETLIST_FM_API_KEY=your-setlistfm-api-key
SPOTIFY_CLIENT_ID=your-spotify-client-id
SPOTIFY_CLIENT_SECRET=your-spotify-client-secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:3000
```

### 3. Run with Docker

From the project root, run:

```bash
docker compose up --build
```

### 4. Stop the containers

To stop the app:

```bash
docker compose down
```

## Local Development Without Docker

### 1. Install backend dependencies

This project uses [`uv`](pyproject.toml) for Python dependency management.

Install dependencies from the project root:

```bash
uv sync
```

### 2. Install frontend dependencies

From [`frontend/`](frontend):

```bash
npm install
```

### 3. Setup environment files

From the project root, run:

```bash
cp .env.example .env
```

From [`frontend/`](frontend), run:

```bash
cp .env.example .env
```

Populate both files.

### 4. Run the backend

From the project root:

```bash
uv run uvicorn src.concert_buddy.server:app --reload --port 8000
```

The backend will be available at:

- `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 5. Run the frontend

From [`frontend/`](frontend):

```bash
npm run dev
```

The frontend will be available at:

- `http://localhost:3000`


## Notes

- :rotating_light: Keep [`.env`](.env) private and never commit real secrets
