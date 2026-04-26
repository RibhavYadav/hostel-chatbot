import json
import os
import pickle

import nltk
import numpy
from nltk.stem.lancaster import LancasterStemmer
from nltk.tokenize import word_tokenize
from tensorflow.keras.models import load_model

from app.config import CLASSES_PATH, INTENTS_PATH, MODEL_PATH, WORDS_PATH
from app.constants import HOSTEL_KEYWORDS, OFF_TOPIC_PATTERNS

nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
ignore_characters = {"?", "!", ".", ",", "'", '"', "-"}
CONFIDENCE_THRESHOLD = 0.65
stemmer = LancasterStemmer()


def _is_hostel_related(query: str) -> bool:
    """
    Checks if a query contains at least one hostel-related keyword.
    Used as a filter on unknown intent responses to avoid returning
    a generic hostel reply to clearly off-topic questions.
    Returns True if any keyword from HOSTEL_KEYWORDS appears in
    the lowercased query, False otherwise.
    """
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in HOSTEL_KEYWORDS)


def _load_assets() -> dict:
    """
    Loads the TensorFlow model, vocabulary, classes, and intents
    from disk into a dict. Called once on startup and again on
    admin-triggered reloads. Raises an exception if any file
    is missing or corrupted so the caller can handle gracefully.
    Returns a dict with keys: model, vocabulary, classes, intents_data.
    """
    with open(INTENTS_PATH, "r") as f:
        intents_data = json.load(f)

    with open(WORDS_PATH, "rb") as f:
        vocabulary = pickle.load(f)

    with open(CLASSES_PATH, "rb") as f:
        classes = pickle.load(f)

    model = load_model(MODEL_PATH)

    return {
        "model": model,
        "vocabulary": vocabulary,
        "classes": classes,
        "intents_data": intents_data,
    }


_state = _load_assets()
print(f"NLP service loaded: {len(_state['vocabulary'])} words, {len(_state['classes'])} intents.")


def reload_model() -> str:
    """
    Reloads all NLP assets from disk into _state.
    Called by the admin retrain endpoint after train.py completes.
    The previous model remains active if loading fails so the
    server never enters a broken state mid-reload.
    Returns a status message string.
    """
    global _state

    try:
        new_state = _load_assets()
        _state = new_state
        print(f"NLP service reloaded: {len(_state['vocabulary'])} words, {len(_state['classes'])} intents.")
        return (
            f"Model reloaded successfully. "
            f"{len(_state['vocabulary'])} words, "
            f"{len(_state['classes'])} intents."
        )
    except Exception as e:
        print(f"NLP reload failed: {e}")
        return f"Model reload failed: {str(e)}. Previous model remains active."


def _bag_of_words(sentence: str) -> numpy.ndarray:
    """
    Converts a sentence into a binary bag-of-words vector.
    Tokenizes and stems the sentence, then sets position i to 1
    if vocabulary word i appears in the stemmed token set.
    Vector length always matches the current vocabulary size in _state
    so it is compatible with the loaded model's input layer.
    """
    tokens = word_tokenize(sentence.lower())
    stemmed = set()
    bag = []

    for token in tokens:
        if token not in ignore_characters:
            stemmed.add(stemmer.stem(token))

    for word in _state["vocabulary"]:
        bag.append(1) if word in stemmed else bag.append(0)

    return numpy.array(bag)


def predict_intent(sentence: str) -> dict:
    """
    Runs the sentence through the TensorFlow model and returns
    the predicted intent tag and confidence score.
    Converts the sentence to a bag-of-words vector, runs model.predict,
    and picks the class with the highest softmax probability.
    Returns tag 'unknown' if confidence is below CONFIDENCE_THRESHOLD
    so callers can handle low-confidence predictions separately.
    Returns a dict with keys: tag, confidence.
    """
    bag_of_words = _bag_of_words(sentence)
    input_data = numpy.array([bag_of_words])

    predictions = _state["model"].predict(input_data, verbose=0)[0]
    best_index = int(numpy.argmax(predictions))
    best_confidence = float(predictions[best_index])

    if best_confidence < CONFIDENCE_THRESHOLD:
        return {"tag": "unknown", "confidence": best_confidence}

    return {"tag": _state["classes"][best_index], "confidence": best_confidence}


def _sanitize_response(text: str) -> str:
    """
    Fixes common encoding corruption in stored response strings.
    Replaces known UTF-8 mojibake sequences that appear when text
    containing em dashes or smart quotes was stored with incorrect
    encoding. Applied to all responses before returning to the student.
    """
    replacements = {
        "â€": "–",
        "â€™": "'",
        "â€œ": '"',
        "â€": '"',
        "â€˜": "'",
        "Â": "",
    }
    for corrupted, fixed in replacements.items():
        text = text.replace(corrupted, fixed)
    return text.strip()


def get_response(tag: str, original_query: str = "") -> str:
    """
    Returns the most relevant response for the given intent tag.
    Uses semantic similarity ranking via rank_responses() to select
    the best response from the matched intent rather than random choice.
    If rank_responses returns None (score below threshold), falls back
    to the first response in the intent list.
    Falls back to an off-topic message if the tag is unknown and the
    query contains no hostel-related keywords.
    Falls back to a contact message if the tag has no responses.
    All responses are sanitized for encoding corruption before returning.
    Returns a plain string in all cases - never raises.
    """
    if tag == "unknown":
        if original_query and not _is_hostel_related(original_query):
            return (
                "I can only help with hostel-related questions such as "
                "mess timings, curfew rules, laundry, leave requests, "
                "and hostel facilities."
            )

    for intent in _state["intents_data"]["intents"]:
        if intent["tag"] == tag:
            if intent["responses"]:
                if original_query and len(intent["responses"]) > 1:
                    from app.services.embedding_service import rank_responses

                    ranked = rank_responses(original_query, intent["responses"])
                    response = ranked if ranked is not None else intent["responses"][0]
                    return _sanitize_response(response)
                return _sanitize_response(intent["responses"][0])

    return "I'm not sure how to help with that. Please contact the hostel office directly."


def get_intents() -> dict:
    """
    Returns the full intents data currently loaded in _state.
    Used by the admin intents endpoint to return the live knowledge base.
    """
    return _state["intents_data"]


def reload_intents() -> None:
    """
    Reloads intents.json from disk into _state without touching
    the model, vocabulary, or classes.
    Called after admin edits to intents or after apply_suggestions
    so new responses are immediately active without a full retrain.
    """
    with open(INTENTS_PATH, "r") as f:
        _state["intents_data"] = json.load(f)
    print("Intents reloaded successfully from disk.")


def is_off_topic(query: str) -> bool:
    """
    Returns True if the query matches a known non-hostel question pattern.
    Checked before intent classification so the NLP model never scores
    queries that are structurally unrelated to hostel topics.
    Runs after a lowercase conversion so casing variants are caught.
    """
    query_lower = query.lower()
    return any(pattern in query_lower for pattern in OFF_TOPIC_PATTERNS)
