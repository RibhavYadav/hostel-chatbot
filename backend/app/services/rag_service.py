import json
import os
import pickle
from pathlib import Path

import numpy as np
from pypdf.errors import PyPdfError

# Path definition
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOCUMENTS_DIR = os.path.join(BASE_DIR, "app", "knowledge_base", "documents")
INDEX_DIR = os.path.join(BASE_DIR, "app", "knowledge_base", "index")
INTENTS_PATH = os.path.join(BASE_DIR, "app", "knowledge_base", "intents.json")
FAISS_INDEX_PATH = os.path.join(INDEX_DIR, "faiss.index")
CHUNKS_PATH = os.path.join(INDEX_DIR, "chunks.pkl")

# Configuration
CHUNK_SIZE = 300
CHUNK_OVERLAP = 50
SIMILARITY_THRESHOLD = 0.35
TOP_K_CHUNKS = 3
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def _load_embedding_model():
    """
    Loads the sentence-transformers embedding model.
    Called once at the module level to be loaded into memory
    on the server startup.
    Reused for every query.
    """
    from sentence_transformers import SentenceTransformer

    print(f"Loading embedding model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)
    print("Loaded embedding model.")
    return model


# State container
_rag_state = {
    "model": _load_embedding_model(),
    "index": None,
    "chunks": [],
}


def _extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts all text from a PDF file using pypdf.
    Returns the full text as a single string with pages
    separated by newlines.
    """
    from pypdf import PdfReader

    reader = PdfReader(pdf_path)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text


def _chunk_text(text: str) -> list[str]:
    """
    Splits text into overlapping chunks of CHUNK_SIZE characters.
    Overlap preserves context at chunk boundaries, a sentence
    split across two chunks is still retrievable from either.
    Filters out chunks that are too short to be meaningful.
    """
    chunks = []
    start = 0

    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end].strip()
        if len(chunk) > 50:
            chunks.append(chunk)
        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


def build_index() -> str:
    """
    Reads all PDF files from the documents directory, extracts text,
    splits into chunks, embeds each chunk using the sentence transformer,
    and saves the FAISS index and chunk list to the index directory.
    Called by the admin re-index endpoint and on first startup
    if no index exists.
    Returns a status message string.
    """
    import faiss

    os.makedirs(INDEX_DIR, exist_ok=True)
    pdf_files = list(Path(DOCUMENTS_DIR).glob("*.pdf"))

    if not pdf_files:
        return "No PDF fields found in documents directory. Index is not built."

    all_chunks = []
    for pdf_path in pdf_files:
        print(f"Processing: {pdf_path.name}")
        text = _extract_text_from_pdf(str(pdf_path))
        chunks = _chunk_text(text)
        all_chunks.extend(chunks)
        print(f" {len(chunks)} chunks extracted.")

    if not all_chunks:
        return "No text could be extracted from the PDF files. Index is not built."

    print(f"Embedding {len(all_chunks)} chunks")
    embeddings = _rag_state["model"].encode(all_chunks, show_progress_bar=True)
    embeddings = np.array(embeddings, dtype=np.float32)

    # Vector normalization for cosine similarity search
    faiss.normalize_L2(embeddings)
    dimension = embeddings.shape[1]

    # FAISS index
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    # Saving index and chunks
    faiss.write_index(index, FAISS_INDEX_PATH)
    with open(CHUNKS_PATH, "wb") as f:
        pickle.dump(all_chunks, f)

    print(f"Index built: {len(all_chunks)} chunks across {len(pdf_files)} documents.")
    return f"Index built: {len(all_chunks)} chunks across {len(pdf_files)} documents."


def _load_index() -> dict:
    """
    Loads the FAISS index and chunk list from disk into the RAG state.
    Called on startup if index files exist, and after build_index completes.
    Returns a dict with keys: index, chunks.
    Returns None values if no index exists yet.
    """
    import faiss

    if not os.path.exists(FAISS_INDEX_PATH) or not os.path.exists(CHUNKS_PATH):
        print("No RAG index found. Add PDF files and call build_index() first.")
        return {"index": None, "chunks": []}

    index = faiss.read_index(FAISS_INDEX_PATH)
    with open(CHUNKS_PATH, "rb") as f:
        chunks = pickle.load(f)

    print(f"RAG index loaded: {len(chunks)} chunks.")
    return {"index": index, "chunks": chunks}


# Loading existing index if available
_index_data = _load_index()
_rag_state["index"] = _index_data["index"]
_rag_state["chunks"] = _index_data["chunks"]


def reload_index() -> str:
    """
    Reloads the FAISS index and chunks from disk into _rag_state.
    Called after build_index completes so the running server
    immediately uses the new index without restart.
    Returns a status message string.
    """
    data = _load_index()
    _rag_state["index"] = data["index"]
    _rag_state["chunks"] = data["chunks"]
    return f"RAG index reloaded: {len(_rag_state['chunks'])} chunks."


def retrieve(query: str) -> str | None:
    """
    Searches the vector index for the most relevant document chunks
    matching the query. Converts the query to a vector, searches the
    FAISS index for the closest chunk vectors, and returns the top
    results concatenated if their similarity exceeds the threshold.
    Returns None if no index is loaded or no sufficiently similar
    chunks are found, signaling the caller for fallback response.
    """
    import faiss

    if _rag_state["index"] is None or not _rag_state["chunks"]:
        return None

    # Embed and normalize query vector
    query_vector = _rag_state["model"].encode([query])
    query_vector = np.array(query_vector, dtype=np.float32)
    faiss.normalize_L2(query_vector)

    # Search the index for the top K most similar chunks
    scores, indices = _rag_state["index"].search(query_vector, TOP_K_CHUNKS)

    # Filter by similarity threshold
    results = []
    for score, idx in zip(scores[0], indices[0]):
        if score >= SIMILARITY_THRESHOLD and idx < len(_rag_state["chunks"]):
            results.append(_rag_state["chunks"][idx])

    if not results:
        return None

    return " ".join(results)


def list_documents() -> list[dict]:
    """
    Returns metadata for all PDF files in the documents directory.
    Used by the admin documents endpoint to show uploaded files.
    """
    os.makedirs(DOCUMENTS_DIR, exist_ok=True)
    documents = []
    for pdf_path in Path(DOCUMENTS_DIR).glob("*.pdf"):
        stat = pdf_path.stat()
        documents.append({"filename": pdf_path.name, "size": stat.st_size, "uploadedAt": str(stat.st_mtime)})
    return documents


def analyze_document(filename: str) -> dict:
    """
    Runs the intent suggestion pipeline on a single PDF file.
    Extracts text, splits into sentences, embeds each sentence,
    and finds the closest existing intent by semantic similarity.
    Returns grouped suggestions for admin review.
    Raises FileNotFoundError if the PDF does not exist.
    Raises RuntimeError if intents or classes files are missing.
    """
    import pickle
    import re

    import faiss

    pdf_path = os.path.join(DOCUMENTS_DIR, filename)
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"{filename} not found in documents directory.")

    classes_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "ml",
        "trained",
        "classes.pkl",
    )
    if not os.path.exists(classes_path):
        raise RuntimeError("classes.pkl not found. Run train.py first.")

    with open(INTENTS_PATH, "r") as f:
        intents_data = json.load(f)

    with open(classes_path, "rb") as f:
        classes = pickle.load(f)

    # Extract and split text
    text = _extract_text_from_pdf(pdf_path)
    raw_sentences = re.split(r"(?<=[.!?])\s+|\n+", text)
    sentences = [s.strip() for s in raw_sentences if 20 <= len(s.strip()) <= 200]

    if not sentences:
        return {"totalSuggestions": 0, "intents": {}}

    # Build intent centroids
    intent_centroids = {}
    for intent in intents_data["intents"]:
        if intent["patterns"]:
            vectors = _rag_state["model"].encode(intent["patterns"])
            centroid = np.mean(vectors, axis=0)
            intent_centroids[intent["tag"]] = centroid

    centroid_tags = list(intent_centroids.keys())
    centroid_matrix = np.array([intent_centroids[t] for t in centroid_tags], dtype=np.float32)
    faiss.normalize_L2(centroid_matrix)

    # Embed sentences
    sentence_vectors = _rag_state["model"].encode(sentences)
    sentence_vectors = np.array(sentence_vectors, dtype=np.float32)
    faiss.normalize_L2(sentence_vectors)

    # Classify each sentence
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

    # Group by intent
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
    The suggestedIntent and type values from the suggestion are used
    directly, so admin edits made during review are preserved.
    Skips duplicates, never adds the same text twice to a list.
    Calls reload_intents after writing so changes are immediately active.
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

    # Reload intents in nlp_service so changes are immediately active
    from app.services.nlp_service import reload_intents

    reload_intents()

    return {"patternsAdded": patterns_added, "responsesAdded": responses_added, "skipped": skipped}
