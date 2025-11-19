# Concert Buddy Frontend

Modern Next.js chat interface for the Concert Buddy AI assistant.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

## Prerequisites

Make sure the Python FastAPI backend is running on http://localhost:8000 before using the frontend.

To start the backend:
```bash
cd ..
uv run uvicorn server:app --reload
```

## Features

- 🎨 Modern, responsive design with Tailwind CSS
- 🌙 Dark mode support
- 💬 Real-time chat interface
- 🎵 Concert search, ticket info, and playlist creation
- ✨ Smooth animations and transitions
