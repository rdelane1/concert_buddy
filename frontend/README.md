# Concert Buddy Frontend

Modern Next.js chat interface for the Concert Buddy AI assistant.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create a local environment file from [`frontend/.env.example`](frontend/.env.example):
```bash
cp .env.example .env.local
```

3. Ensure [`BACKEND_URL`](frontend/.env.example) points to your backend:
```env
BACKEND_URL=http://localhost:8000
```

4. Start the development server:
```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser

## Prerequisites

Make sure the Python FastAPI backend is running on `http://localhost:8000` before using the frontend.

To start the backend:
```bash
cd ..
uv run uvicorn server:app --reload
```

## Cloud Run deployment

The frontend now proxies browser requests through [`/api/chat`](frontend/app/api/chat/route.ts:33) and [`/api/events`](frontend/app/api/events/route.ts:38).

- **Local development:** set [`BACKEND_URL`](frontend/.env.example) to `http://localhost:8000`. The proxy forwards requests without Google authentication.
- **Cloud Run production:** set [`BACKEND_URL`](frontend/.env.example) to your private backend Cloud Run URL. The proxy uses [`GoogleAuth`](frontend/app/api/chat/route.ts:1) to mint an ID token for service-to-service authentication.

For production, deploy the frontend with a service account that has `roles/run.invoker` on the backend service.

## Features

- 🎨 Modern, responsive design with Tailwind CSS
- 🌙 Dark mode support
- 💬 Real-time chat interface
- 🎵 Concert search, ticket info, and playlist creation
- ✨ Smooth animations and transitions
