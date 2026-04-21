import os
import pickle
from pathlib import Path

import numpy as np
from pypdf.errors import PyPdfError

# Path definition
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOCUMENTS_DIR = os.path.join(BASE_DIR, "app", "knowledge_base", "documents")
INDEX_DIR = os.path.join(BASE_DIR, "app", "knowledge_base", "index")
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
