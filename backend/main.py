"""
main.py

FastAPI entrypoint with WebSocket streaming + NER push.
Robust version with error handling + debug logging + done signal.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
import json

from llm_service import generate_summary_stream
from nlp_pipeline import preprocess_ehr
from logger import logger

app = FastAPI(title="NeuroNote API")

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- WEBSOCKET ----------------
@app.websocket("/ws/summarize")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            logger.info("Received EHR via WS")

            try:
                parsed = json.loads(data)
                ehr_text = parsed.get("text", "")
            except Exception:
                ehr_text = data 

            # ---------- NLP ----------
            processed, entities = await run_in_threadpool(preprocess_ehr, ehr_text)

            logger.info(f"Entities extracted: {entities}")

            # Send entities FIRST
            await websocket.send_text(json.dumps({
                "type": "entities",
                "data": entities
            }))

            # ---------- LLM STREAM ----------
            logger.info("Starting summary stream...")

            token_sent = False

            try:
                async for token in generate_summary_stream(processed):
                    if token:
                        token_sent = True
                        await websocket.send_text(json.dumps({
                            "type": "token",
                            "data": token
                        }))

                if not token_sent:
                    await websocket.send_text(json.dumps({
                        "type": "token",
                        "data": "[No summary generated]"
                    }))

            except Exception as e:
                logger.error(f"Streaming error: {e}")

                await websocket.send_text(json.dumps({
                    "type": "error",
                    "data": str(e)
                }))

            # ---------- DONE SIGNAL ----------
            await websocket.send_text(json.dumps({
                "type": "done"
            }))

    except WebSocketDisconnect:
        logger.info("WS disconnected")