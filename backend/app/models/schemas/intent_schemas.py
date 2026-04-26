from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, field_validator


class IntentModel(BaseModel):
    """
    Used when returning the full intent list to admins.
    Represents a single intent as it exists in intents.json.
    """

    tag: str
    patterns: List[str]
    responses: List[str]


class IntentCreateRequest(BaseModel):
    """
    Request body for adding a new intent.
    All three fields are required, a new intent must have
    at least one pattern and one response to be valid for training.
    """

    tag: str
    patterns: List[str]
    responses: List[str]


class IntentUpdateRequest(BaseModel):
    """
    Request body for updating an existing intent.
    Both fields are optional, the admin may update only patterns,
    only responses, or both in a single request.
    Fields that are None are left unchanged.
    """

    patterns: Optional[List[str]] = None
    responses: Optional[List[str]] = None


class PromoteRequest(BaseModel):
    """
    Request body for promoting a chat log as a training pattern.
    targetTag overrides the predicted tag if the admin wants to
    assign the message to a different intent than the model predicted.
    If omitted the predicted tag is used.
    """

    targetTag: str | None = None
