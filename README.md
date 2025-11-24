# Concert Buddy

An AI assistant to help plan for attending live concerts. Concert Buddy helps you discover upcoming shows, find tickets, and create personalized Spotify playlists based on artist setlists.

## Prerequisites

Before getting started, you'll need:

- **Python 3.12+** - Required for the backend server
- **Node.js 18+** - Required for the Next.js frontend
- **uv** - Fast Python package installer and resolver
- **API Keys**:
  - OpenAI API key (for AI agent functionality)
  - Spotify API credentials (Client ID, Client Secret)
  - Setlist.fm API key (for concert setlist data)

## Getting Started with uv

This project uses [uv](https://github.com/astral-sh/uv) for fast and reliable Python dependency management.

### Installing uv

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Setting Up the Environment

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd concert_buddy
```

### 2. Set Up Environment Variables

Copy the example environment file and fill in your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your API credentials:

```env
# OpenAI API Key
# Get your key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your-openai-api-key-here

# Setlist.fm API Key
# Register at: https://api.setlist.fm/docs/1.0/index.html
SETLIST_FM_API_KEY=your-setlistfm-api-key-here

# Spotify API Credentials
# Create an app at: https://developer.spotify.com/dashboard
SPOTIFY_CLIENT_ID=your-spotify-client-id-here
SPOTIFY_CLIENT_SECRET=your-spotify-client-secret-here

# Spotify Redirect URI (for OAuth)
# This can be any valid URI (does not need to be accessible)
SPOTIFY_REDIRECT_URI=http://127.0.0.1:3000
```

### 3. Install Backend Dependencies

Using uv, sync all Python dependencies:

```bash
uv sync
```

This will:
- Create a virtual environment in `.venv/`
- Install all dependencies from `pyproject.toml`
- Generate/update the lock file for reproducible builds

### 4. Install Frontend Dependencies

Navigate to the frontend directory and install dependencies:

```bash
cd frontend
npm install
```

## Running the Application

### Backend Server

From the project root:

```bash
# Run the FastAPI server
uv run uvicorn src.concert_buddy.server:app --reload --port 8000
```

The backend API will be available at `http://localhost:8000`

### Frontend Development Server

In a separate terminal, from the `frontend/` directory:

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## API Documentation

Once the backend is running, you can access the interactive API documentation at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
concert_buddy/
├── src/
│   └── concert_buddy/
│       ├── server.py          # FastAPI application
│       ├── agents/            # AI agent implementations
│       └── config/            # Configuration files
├── frontend/
│   ├── app/                   # Next.js App Router
│   └── package.json           # Frontend dependencies
├── pyproject.toml             # Python dependencies
├── .env.example               # Environment variables template
└── README.md                  # This file
```
