from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio
from pathlib import Path

router = APIRouter()


@router.get("/api/logs/stream")
async def log_stream():
    async def event_generator():
        log_path = Path("logs/scrawlnews.log")
        # Stage 3 stub: stream last 20 lines if exists, then dummy event
        if log_path.exists():
            lines = log_path.read_text().splitlines()[-20:]
            for line in lines:
                yield f"data: {line}\n\n"
                await asyncio.sleep(0.01)
        yield "data: [health] SSE connected\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
