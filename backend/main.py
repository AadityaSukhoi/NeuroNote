"""
main.py

Description:
    Entry point for NeuroNote FastAPI backend.
    Includes REST + WebSocket streaming.

Author: Aaditya Ranjan Moitra
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from summarization_api import router as summarization_router
from llm_service import generate_summary_stream
from logger import logger

app = FastAPI(
    title="NeuroNote EHR Summarizer API",
    description="AI-powered summarization of Electronic Health Records (EHRs).",
    version="2.0.0"
)

# CORS (important for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    logger.info("Root endpoint accessed.")
    return {"message": "Welcome to NeuroNote API!"}


# REST routes
app.include_router(summarization_router, prefix="/summarize")


# ------------------ WebSocket Streaming ------------------
@app.websocket("/ws/summarize")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for streaming summaries.
    """
    await websocket.accept()

    try:
        while True:
            ehr_text = await websocket.receive_text()

            logger.info(f"WebSocket request received ({len(ehr_text)} chars)")

            async for token in generate_summary_stream(ehr_text):
                await websocket.send_text(token)

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected.")
        await websocket.close()


# ------------------ Error Handler ------------------
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(status_code=500, content={"error": str(exc)})