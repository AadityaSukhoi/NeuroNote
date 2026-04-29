"""
summarization_api.py

REST API for summarization.
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel

from logger import logger
from llm_service import generate_summary_stream

router = APIRouter()


class SummarizationRequest(BaseModel):
    ehr_text: str
    patient_id: str | None = None
    stream: bool = False


async def stream_response(ehr_text: str):
    async for chunk in generate_summary_stream(ehr_text):
        yield chunk


async def get_full_summary(ehr_text: str) -> str:
    result = ""
    async for chunk in generate_summary_stream(ehr_text):
        result += chunk
    return result


@router.post("/")
async def summarize(request: SummarizationRequest):
    logger.info(f"Request received for patient_id={request.patient_id}")

    try:
        if request.stream:
            return StreamingResponse(stream_response(request.ehr_text))
        else:
            summary = await get_full_summary(request.ehr_text)
            return JSONResponse({"summary": summary})

    except Exception as e:
        logger.error(f"Error: {e}")
        return JSONResponse({"error": "Failed"}, status_code=500)