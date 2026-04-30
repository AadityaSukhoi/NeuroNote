"""
summarization_api.py
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel

from logger import logger
from llm_service import generate_summary_stream
from nlp_pipeline import preprocess_ehr

router = APIRouter()


class SummarizationRequest(BaseModel):
    ehr_text: str
    stream: bool = False


async def stream_response(ehr_text: str):
    processed, _ = preprocess_ehr(ehr_text)
    async for chunk in generate_summary_stream(processed):
        yield chunk


async def get_full_summary(ehr_text: str):
    processed, _ = preprocess_ehr(ehr_text)

    result = ""
    async for chunk in generate_summary_stream(processed):
        result += chunk

    return result


@router.post("/")
async def summarize(request: SummarizationRequest):
    logger.info("REST request")

    try:
        if request.stream:
            return StreamingResponse(stream_response(request.ehr_text))
        else:
            summary = await get_full_summary(request.ehr_text)
            return JSONResponse({"summary": summary})

    except Exception as e:
        logger.error(str(e))
        return JSONResponse({"error": "Failed"}, status_code=500)