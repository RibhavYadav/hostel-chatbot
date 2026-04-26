from pydantic import BaseModel


class DocumentInfo(BaseModel):
    """
    Metadata for an uploaded PDF document.
    Returned by the list documents endpoint.
    """

    filename: str
    size: int
    uploadedAt: str


class IntentSuggestion(BaseModel):
    """
    A single suggestion generated from a PDF sentence.
    sentence is the raw text extracted from the PDF.
    suggestedIntent is the closest matching intent tag.
    similarity is the cosine similarity score between the sentence
    and the intent centroid, between 0.0 and 1.0.
    type indicates whether the sentence reads as a question (pattern)
    or a statement (response).
    accepted is set by the admin during review.
    """

    sentence: str
    suggestedIntent: str
    similarity: float
    type: str
    accepted: bool = False


class SuggestionResult(BaseModel):
    """
    The full output of the PDF analysis pipeline.
    totalSuggestions is the count of all suggestions above threshold.
    intents maps each intent tag to its list of suggestions.
    """

    totalSuggestions: int
    intents: dict


class ApplySuggestionsRequest(BaseModel):
    """
    Request body for applying reviewed suggestions to intents.json.
    suggestions is the full list including both accepted and rejected.
    Only entries with accepted=True are written to intents.json.
    suggestedIntent and type may have been edited by the admin
    before submission, so the values in this list are used, not
    the original pipeline output.
    """

    suggestions: list[IntentSuggestion]
