"""
llm_service.py

Gemini → Granite fallback
Using new Google Gen AI SDK (google-genai)
"""

import os
import asyncio
from dotenv import load_dotenv
from logger import logger
from google import genai

import ollama

load_dotenv()

MODEL_NAME = "granite3.2:8b"
GEMINI_MODEL = "gemini-2.5-flash"

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


def build_prompt(processed_text: str) -> str:
    return f"""
STRICT RULES:
- Output ONLY markdown
- Each bullet MUST start with "- "
- No nested bullets
- Use headings like ## Patient Overview

You are NeuroNote.

{processed_text}

Generate summary:
"""


# ---------------- GEMINI ----------------
async def gemini_stream(processed_text: str):
    """
    Gemini sync SDK is blocking — run in executor to keep
    the event loop free to flush WebSocket messages.
    """

    prompt = build_prompt(processed_text)

    try:
        loop = asyncio.get_event_loop()

        response = await loop.run_in_executor(
            None,
            lambda: client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt
            )
        )

        text = response.text

        # Simulate streaming word by word
        for chunk in text.split(" "):
            yield chunk + " "

    except Exception as e:
        logger.error(f"[Gemini Error]: {e}")
        raise e


# ---------------- GRANITE (REAL STREAMING) ----------------
async def granite_stream(processed_text: str):
    prompt = build_prompt(processed_text)

    try:
        ollama_client = ollama.AsyncClient()

        chat_gen = await ollama_client.chat(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )

        async for chunk in chat_gen:
            if "message" in chunk and "content" in chunk["message"]:
                yield chunk["message"]["content"]

    except Exception as e:
        logger.error(f"[Granite Error]: {e}")
        raise e


# ---------------- MAIN ----------------
async def generate_summary_stream(processed_text: str):

    try:
        async for chunk in gemini_stream(processed_text):
            yield chunk
        return
    except Exception:
        logger.warning("Gemini failed → switching to Granite")

    try:
        async for chunk in granite_stream(processed_text):
            yield chunk
        return
    except Exception:
        logger.error("Both models failed")

    yield "[Error]: Could not generate summary"