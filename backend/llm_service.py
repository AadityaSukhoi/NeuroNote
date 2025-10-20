"""
LLM Service for NeuroNote (Granite 3.2 8B streaming & Gemini fallback)
Author: Aaditya Ranjan Moitra
"""

import asyncio
import os
from logger import logger
from dotenv import load_dotenv
load_dotenv()

import ollama

# MODEL_NAME = "granite3.2:8b"

# async def generate_summary_stream(ehr_text: str):
#     """
#     Stream summary from locally installed Granite 3.2 model via Ollama.
#     Streams token-by-token.
#     """
#     system_prompt = """
# You are NeuroNote, an AI clinical assistant specializing in summarizing EHRs (Electronic Health Records).

# Your role:
# - Summarize patient data into clear, concise, and medically relevant bullet points.
# - Include sections like Patient Overview, Diagnosis, Medications, Allergies, Vital Signs, Key Findings/Lab Results, Follow-up Recommendations.
# - Use markdown-style bullets ("- "), short, readable, clinically accurate.
# - Do NOT answer anything unrelated to EHRs.

# Example Input:
# Patient: John Doe
# Age: 56
# Chief Complaint: Chest pain and shortness of breath.
# Diagnosis: Acute myocardial infarction.
# Medications: Aspirin, Atorvastatin, Clopidogrel.
# Lab Results: Elevated Troponin I, ECG shows ST elevation.

# Example Output:
# - **Patient Overview:** 56-year-old male with chest pain and SOB.
# - **Diagnosis:** Acute myocardial infarction (STEMI).
# - **Medications:** Aspirin, Atorvastatin, Clopidogrel.
# - **Key Findings:** Elevated Troponin I, ST elevation on ECG.
# - **Recommendations:** Continuous cardiac monitoring; cardiology consult.
# """
#     prompt = f"{system_prompt}\n\nEHR DATA:\n{ehr_text}\n\nGenerate bullet point summary below:\n"

#     try:
#         client = ollama.AsyncClient()
#         chat_gen = await client.chat(
#             model=MODEL_NAME,
#             messages=[{"role": "user", "content": prompt}],
#             stream=True
#         )

#         async for chunk in chat_gen:
#             if "message" in chunk and "content" in chunk["message"]:
#                 yield chunk["message"]["content"]
#             await asyncio.sleep(0.001)

#     except Exception as e:
#         logger.error(f"[Granite Streaming Error]: {e}")
#         yield "[Error]: Could not generate summary."


# ---------------------- GEMINI (Commented Fallback) ----------------------
# Uncomment to deploy with Gemini API (requires GOOGLE_API_KEY in .env)

from google import genai
import os
async def generate_summary_stream(ehr_text: str):
    """
    Stream EHR summary from Gemini API (fallback)
    """
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    system_prompt = "You are NeuroNote, a medical AI assistant summarizing EHRs into clinical bullet points."
    prompt = f"{system_prompt}\n\nEHR DATA:\n{ehr_text}\n\nGenerate bullet point summary."

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        # yield the whole response once (sync -> async generator)
        yield response.text

    except Exception as e:
        yield f"[Error]: {e}"