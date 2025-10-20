from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
import asyncio

from llm_service import generate_summary_stream
from logger import logger


# ------------------ FastAPI App ------------------
app = FastAPI(
    title="NeuroNote EHR Summarizer API",
    description="AI-powered summarization of Electronic Health Records (EHRs) using Granite 3.2:8b.",
    version="1.0.0"
)


# ------------------ Data Model ------------------
class EHRRequest(BaseModel):
    ehr_text: str


# ------------------ Root Endpoint ------------------
@app.get("/")
async def root():
    logger.info("Root endpoint accessed.")
    return {"message": "Welcome to NeuroNote API! Submit your EHR text to /summarize to get a summary."}


# ------------------ REST API (Streaming) ------------------
@app.post("/summarize")
async def summarize_ehr(request: EHRRequest):
    """
    Summarize EHR data using local Granite 3.2 model via Ollama.
    Streams token-by-token output.
    """

    async def token_streamer():
        async for token in generate_summary_stream(request.ehr_text):
            yield token

    logger.info("Received summarization request.")
    return StreamingResponse(token_streamer(), media_type="text/plain")


# ------------------ WebSocket (Live Streaming) ------------------
@app.websocket("/ws/summarize")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Incoming EHR text over WebSocket: {len(data)} chars")
            async for token in generate_summary_stream(data):
                await websocket.send_text(token)
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected.")
        await websocket.close()


# ------------------ Error Handling ------------------
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(status_code=500, content={"error": str(exc)})


# ------------------ Run App (Development) ------------------
# Command: uvicorn main:app --reload
