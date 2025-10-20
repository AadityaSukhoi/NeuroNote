"""
Summarization API Routes for NeuroNote
Author: Aaditya Ranjan Moitra
Description:
    FastAPI route to handle EHR summarization requests.
    Supports streaming responses and full JSON responses.
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from logger import logger
from llm_service import generate_summary_stream

router = APIRouter()

# -------------------- Request Schema --------------------
class SummarizationRequest(BaseModel):
    ehr_text: str
    patient_id: str | None = None
    stream: bool = False  # stream or full response

# -------------------- Streaming Helper --------------------
async def stream_response(ehr_text: str):
    """Yield chunks from LLM as streaming response."""
    async for chunk in generate_summary_stream(ehr_text):
        yield chunk

# -------------------- POST Endpoint --------------------
@router.post("/")
async def summarize(request: SummarizationRequest):
    logger.info(f"Summarization request received for patient_id={request.patient_id}")

    try:
        if request.stream:
            return StreamingResponse(
                stream_response(request.ehr_text),
                media_type="text/plain"
            )
        else:
            summary = await generate_summary_stream(request.ehr_text, stream=False)
            return JSONResponse({"summary": summary})

    except Exception as e:
        logger.error(f"Error during summarization: {str(e)}")
        return JSONResponse({"error": "Failed to summarize EHR"}, status_code=500)
