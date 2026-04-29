"""
llm_service.py

Description:
    Handles LLM inference for NeuroNote.
    Uses Granite (Ollama) as primary and Gemini as fallback.

Author: Aaditya Ranjan Moitra
"""

import os
from dotenv import load_dotenv
from logger import logger

import ollama
from google import genai

from nlp_pipeline import preprocess_ehr

load_dotenv()

MODEL_NAME = "granite3.2:8b"
GEMINI_MODEL = "gemini-1.5-flash"


def build_prompt(processed_text: str) -> str:
    """Build strict prompt."""
    return f"""
STRICT RULES:
- Output ONLY bullet points
- Each line MUST start with "- "
- No "*"
- No paragraphs

You are NeuroNote, an AI clinical assistant summarizing EHRs.

{processed_text}

Generate summary:
"""


async def granite_stream(ehr_text: str):
    """Stream from Granite."""
    processed = preprocess_ehr(ehr_text)
    prompt = build_prompt(processed)

    try:
        client = ollama.AsyncClient()

        chat_gen = await client.chat(
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


async def gemini_stream(ehr_text: str):
    """Fallback Gemini."""
    processed = preprocess_ehr(ehr_text)
    prompt = build_prompt(processed)

    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )

        yield response.text

    except Exception as e:
        logger.error(f"[Gemini Error]: {e}")
        raise e


async def generate_summary_stream(ehr_text: str):
    """
    Main pipeline:
    Granite → Gemini → fallback error.
    """
    try:
        async for chunk in granite_stream(ehr_text):
            yield chunk
        return
    except Exception:
        logger.warning("Granite failed. Switching to Gemini.")

    try:
        async for chunk in gemini_stream(ehr_text):
            yield chunk
        return
    except Exception:
        logger.error("Gemini also failed.")

    yield "[Error]: Unable to generate summary."