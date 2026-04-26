import json
import os
from pathlib import Path

import numpy as np

from app.config import DOCUMENTS_DIR, INTENTS_PATH
from app.services.embedding_service import get_embedding_model


def _extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts all text from a PDF file using pypdf.
    Each page is separated by a PAGE_BREAK marker so that
    _chunk_text can split on page boundaries before character
    chunking, preventing chunks from spanning across pages.
    Returns the full text as a single string.
    """
    from pypdf import PdfReader

    reader = PdfReader(pdf_path)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n\n<<<PAGE_BREAK>>>\n\n"

    return text


def list_documents() -> list[dict]:
    """
    Returns metadata for all PDF files in the documents directory.
    Used by the admin documents endpoint to show uploaded files.
    """
    os.makedirs(DOCUMENTS_DIR, exist_ok=True)
    documents = []
    for pdf_path in Path(DOCUMENTS_DIR).glob("*.pdf"):
        stat = pdf_path.stat()
        documents.append(
            {
                "filename": pdf_path.name,
                "size": stat.st_size,
                "uploadedAt": str(stat.st_mtime),
            }
        )
    return documents


def _extract_sentences(text: str) -> list[str]:
    """
    Extracts meaningful complete sentences from PDF text.
    Joins lines that do not end with terminal punctuation into
    the next line before splitting, preventing mid-sentence splits
    caused by PDF line wrapping. Filters out fragments shorter
    than 30 characters and longer than 300 characters.
    """
    import re

    text = text.replace("<<<PAGE_BREAK>>>", "\n")
    lines = text.split("\n")
    joined_lines = []
    buffer = ""

    for line in lines:
        line = line.strip()
        if not line:
            if buffer:
                joined_lines.append(buffer)
                buffer = ""
            continue
        if buffer:
            buffer += " " + line
        else:
            buffer = line
        if re.search(r"[.!?:]$", line):
            joined_lines.append(buffer)
            buffer = ""

    if buffer:
        joined_lines.append(buffer)

    sentences = []
    for line in joined_lines:
        parts = re.split(r"(?<=[.!?])\s+", line)
        for part in parts:
            part = part.strip()
            if 30 <= len(part) <= 300:
                sentences.append(part)

    return sentences


def analyze_document(filename: str) -> dict:
    """
    Runs the intent suggestion pipeline on a single PDF file.
    Extracts text, splits into sentences, embeds each sentence,
    and finds the closest existing intent by semantic similarity
    against intent pattern centroids.
    Returns grouped suggestions for admin review.
    Raises FileNotFoundError if the PDF does not exist.
    Raises RuntimeError if classes.pkl is missing.
    """
    import re

    import faiss

    pdf_path = os.path.join(DOCUMENTS_DIR, filename)
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"{filename} not found in documents directory.")

    with open(INTENTS_PATH, "r") as f:
        intents_data = json.load(f)

    text = _extract_text_from_pdf(pdf_path)
    raw_sentences = re.split(r"(?<=[.!?])\s+|\n+", text)
    sentences = [s.strip() for s in raw_sentences if 20 <= len(s.strip()) <= 200]

    if not sentences:
        return {"totalSuggestions": 0, "intents": {}}

    intent_centroids = {}
    for intent in intents_data["intents"]:
        if intent["patterns"]:
            vectors = get_embedding_model().encode(intent["patterns"])
            centroid = np.mean(vectors, axis=0)
            intent_centroids[intent["tag"]] = centroid

    centroid_tags = list(intent_centroids.keys())
    centroid_matrix = np.array([intent_centroids[t] for t in centroid_tags], dtype=np.float32)
    faiss.normalize_L2(centroid_matrix)

    sentence_vectors = get_embedding_model().encode(sentences)
    sentence_vectors = np.array(sentence_vectors, dtype=np.float32)
    faiss.normalize_L2(sentence_vectors)

    suggestions = []
    for sentence, vector in zip(sentences, sentence_vectors):
        scores = np.dot(centroid_matrix, vector)
        best_idx = int(np.argmax(scores))
        best_score = float(scores[best_idx])
        best_tag = centroid_tags[best_idx]

        if best_score >= 0.40:
            is_question = "?" in sentence or sentence.lower().startswith(
                ("what", "when", "how", "where", "who", "can", "is", "are", "do", "does", "will", "should")
            )
            suggestions.append(
                {
                    "sentence": sentence,
                    "suggestedIntent": best_tag,
                    "similarity": round(best_score, 3),
                    "type": "pattern" if is_question else "response",
                    "accepted": False,
                }
            )

    suggestions.sort(key=lambda x: x["similarity"], reverse=True)

    grouped = {}
    for s in suggestions:
        tag = s["suggestedIntent"]
        if tag not in grouped:
            grouped[tag] = []
        grouped[tag].append(s)

    return {"totalSuggestions": len(suggestions), "intents": grouped}


def apply_suggestions(suggestions: list[dict]) -> dict:
    """
    Applies accepted suggestions to intents.json.
    Only suggestions with accepted=True are written.
    Skips duplicates - never adds the same text twice to a list.
    Calls reload_intents after writing so changes are immediately
    active in the running server without restart.
    Returns counts of patterns added, responses added, and duplicates skipped.
    """
    with open(INTENTS_PATH, "r") as f:
        intents_data = json.load(f)

    intent_lookup = {i["tag"]: i for i in intents_data["intents"]}

    patterns_added = 0
    responses_added = 0
    skipped = 0

    for suggestion in suggestions:
        if not suggestion.get("accepted", False):
            continue

        tag = suggestion["suggestedIntent"]
        text = suggestion["sentence"]
        suggestion_type = suggestion["type"]

        if tag not in intent_lookup:
            continue

        intent = intent_lookup[tag]

        if suggestion_type == "pattern":
            if text not in intent["patterns"]:
                intent["patterns"].append(text)
                patterns_added += 1
            else:
                skipped += 1
        elif suggestion_type == "response":
            if text not in intent["responses"]:
                intent["responses"].append(text)
                responses_added += 1
            else:
                skipped += 1

    with open(INTENTS_PATH, "w") as f:
        json.dump(intents_data, f, indent=2)

    from app.services.nlp_service import reload_intents

    reload_intents()

    return {"patternsAdded": patterns_added, "responsesAdded": responses_added, "skipped": skipped}
