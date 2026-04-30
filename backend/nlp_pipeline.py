"""
nlp_pipeline.py

Dynamic NLP preprocessing for NeuroNote.

Pipeline:
- Text cleaning
- LLM-based medical NER (Gemini)
- Validation + deduplication
- Structured context creation
"""

import os
import json
import re
from dotenv import load_dotenv
from google import genai
from logger import logger

# ---------------- ENV ----------------
load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
GEMINI_MODEL = "gemini-2.5-flash"


# ---------------- TEXT CLEANING ----------------
def clean_text(text: str) -> str:
    """
    Normalize whitespace and clean text.
    """
    return " ".join(text.split()).strip()


# ---------------- ENTITY VALIDATION ----------------
def validate_entities(entities: dict) -> dict:
    """
    Remove noisy / garbage entities.
    """

    def is_valid(item: str) -> bool:
        item = item.strip()

        # Remove very short junk
        if len(item) < 3:
            return False

        # Remove generic useless words
        junk = ["daily", "patient", "history", "complaint"]
        if item.lower() in junk:
            return False

        return True

    for key in entities:
        seen = set()
        cleaned_list = []

        for item in entities[key]:
            item = item.strip()

            if not is_valid(item):
                continue

            if item not in seen:
                seen.add(item)
                cleaned_list.append(item)

        entities[key] = cleaned_list

    return entities


# ---------------- LLM ENTITY EXTRACTION ----------------
def extract_entities(text: str) -> dict:
    """
    Extract structured medical entities using Gemini.
    """

    prompt = f"""
You are a clinical NLP system.

Extract structured medical entities STRICTLY in JSON.

Rules:
- Persons → FULL names only (e.g., "Rajesh Kumar", "Dr. Meena Rao")
- Medications → include dosage (e.g., "Amlodipine 5mg")
- Conditions → diseases only
- Labs → medical tests
- Dates → FULL dates only (e.g., "12th October 2025")
- Vitals → include values (e.g., "BP 148/96 mmHg")

STRICTLY DO NOT INCLUDE:
- single words like "October", "daily"
- units alone like "mg", "dL"
- split names like "Rajesh", "Kumar"

Return ONLY this JSON with no markdown, no backticks, no explanation:

{{
  "persons": [],
  "medications": [],
  "conditions": [],
  "labs": [],
  "dates": [],
  "vitals": []
}}

EHR:
{text}
"""

    try:
        print("=== NER CALLED ===")
        print("TEXT:", text[:100])

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )

        raw = response.text.strip()
        print("=== RAW NER RESPONSE ===", raw[:300])

        # Step 1: try direct JSON parse
        try:
            entities = json.loads(raw)

        except Exception:
            # Step 2: strip markdown code fences (```json ... ``` or ``` ... ```)
            raw_clean = re.sub(r"```(?:json)?", "", raw).strip()
            raw_clean = raw_clean.replace("```", "").strip()

            try:
                entities = json.loads(raw_clean)
            except Exception:
                # Step 3: extract JSON object with regex
                match = re.search(r"\{.*\}", raw_clean, re.DOTALL)
                entities = json.loads(match.group(0)) if match else {}

    except Exception as e:
        logger.error(f"[NER Error]: {e}")
        print("=== NER EXCEPTION ===", e)
        entities = {}

    # Ensure structure
    default = {
        "persons": [],
        "medications": [],
        "conditions": [],
        "labs": [],
        "dates": [],
        "vitals": []
    }

    for k in default:
        entities.setdefault(k, [])

    # Clean entities
    entities = validate_entities(entities)

    print("=== FINAL ENTITIES ===", entities)

    return entities


# ---------------- MAIN NLP PIPELINE ----------------
def preprocess_ehr(ehr_text: str):
    """
    Full NLP pipeline.

    Returns:
        (structured_context, entities)
    """

    cleaned = clean_text(ehr_text)

    # Extract entities
    entities = extract_entities(cleaned)

    # Build structured context
    structured = "STRUCTURED CONTEXT:\n"

    if entities["persons"]:
        structured += f"Patients: {', '.join(entities['persons'])}\n"

    if entities["medications"]:
        structured += f"Medications: {', '.join(entities['medications'])}\n"

    if entities["conditions"]:
        structured += f"Conditions: {', '.join(entities['conditions'])}\n"

    if entities["labs"]:
        structured += f"Labs: {', '.join(entities['labs'])}\n"

    if entities["vitals"]:
        structured += f"Vitals: {', '.join(entities['vitals'])}\n"

    if entities["dates"]:
        structured += f"Dates: {', '.join(entities['dates'])}\n"

    return structured + "\n\n" + cleaned, entities