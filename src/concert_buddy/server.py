"""FastAPI server for Concert Buddy agent workflow."""

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from agents import Runner
from .progress import sse_event_stream

from .agents.manager_agent import manager_agent

load_dotenv(override=True)

app = FastAPI(title="Concert Buddy API")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    previous_response_id: str | None = None
    session_id: str | None = None


class ChatResponse(BaseModel):
    output: str
    last_response_id: str | None = None


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Handle chat messages and return agent responses."""
    # Prepend session context so the manager can call progress tools with the right id
    prefixed_input = (
        f"SESSION_ID: {req.session_id}\n" + req.message
        if req.session_id
        else req.message
    )
    result = await Runner.run(
        starting_agent=manager_agent,
        input=prefixed_input,
        previous_response_id=req.previous_response_id,
    )
    return ChatResponse(
        output=str(result.final_output),
        last_response_id=result.last_response_id,
    )


@app.get("/events")
async def events(session_id: str):
    """Server-Sent Events stream for real-time progress updates."""
    return StreamingResponse(
        sse_event_stream(session_id), media_type="text/event-stream"
    )


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.concert_buddy.server:app", host="0.0.0.0", port=8000, reload=True)
