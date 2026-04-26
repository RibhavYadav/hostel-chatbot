import numpy as np

# Configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
RESPONSE_RANKING_THRESHOLD = 0.30


def _load_embedding_model():
    """
    Loads the sentence-transformers embedding model.
    Called once at module level so the model is in memory
    for the lifetime of the server process.
    Reused for document analysis, suggestion ranking,
    and semantic response selection.
    """
    from sentence_transformers import SentenceTransformer

    print(f"Loading embedding model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)
    print("Loaded embedding model.")
    return model


# State container
_rag_state = {
    "model": _load_embedding_model(),
}


def get_embedding_model():
    """
    Returns the loaded sentence-transformers model from module state.
    Used by document_service to embed sentences during PDF analysis
    without duplicating the model load or exposing _rag_state directly.
    """
    return _rag_state["model"]


def rank_responses(query: str, responses: list[str]) -> str | None:
    """
    Selects the most relevant response for a query using semantic
    similarity rather than random selection.
    Embeds the query and all candidate responses using the loaded
    sentence-transformers model, computes cosine similarity between
    the query vector and each response vector, and returns the
    response with the highest similarity score.
    Returns None if the best score is below RESPONSE_RANKING_THRESHOLD,
    signaling the caller to use the intent fallback response instead.
    Falls back to the first response if embedding fails entirely.
    """
    if len(responses) == 1:
        return responses[0]

    try:
        all_texts = [query] + responses
        vectors = get_embedding_model().encode(all_texts)
        query_vector = vectors[0]
        response_vectors = vectors[1:]

        scores = np.dot(response_vectors, query_vector) / (
            np.linalg.norm(response_vectors, axis=1) * np.linalg.norm(query_vector) + 1e-8
        )

        best_index = int(np.argmax(scores))
        best_score = float(scores[best_index])

        print(f"DEBUG semantic ranking: best response index {best_index}, score {best_score:.3f}")

        if best_score < RESPONSE_RANKING_THRESHOLD:
            print(
                f"DEBUG ranking below threshold ({best_score:.3f} < {RESPONSE_RANKING_THRESHOLD}), using fallback."
            )
            return None

        return responses[best_index]

    except Exception as e:
        print(f"Semantic ranking failed: {e}. Using first response.")
        return responses[0]
