"""
nlp_pipeline.py

Dynamic NLP preprocessing using spaCy.
"""

import spacy

nlp = spacy.load("en_core_web_sm")


def clean_text(text: str) -> str:
    """Normalize text."""
    return " ".join(text.split())


def extract_entities(text: str) -> dict:
    """Extract dynamic entities."""
    doc = nlp(text)

    entities = {
        "persons": [],
        "dates": [],
        "medical_terms": []
    }

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            entities["persons"].append(ent.text)
        elif ent.label_ == "DATE":
            entities["dates"].append(ent.text)

    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"] and len(token.text) > 4:
            entities["medical_terms"].append(token.text)

    return entities


def preprocess_ehr(ehr_text: str) -> str:
    """Full NLP pipeline."""
    cleaned = clean_text(ehr_text)
    entities = extract_entities(cleaned)

    structured = f"""
STRUCTURED CONTEXT:
Persons: {entities['persons']}
Dates: {entities['dates']}
Key Terms: {list(set(entities['medical_terms']))[:20]}
"""

    return structured + "\n\n" + cleaned