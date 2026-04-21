import json
import os
import pickle
import random

import nltk
import numpy
from nltk.stem.lancaster import LancasterStemmer
from nltk.tokenize import word_tokenize
from tensorflow.keras.models import load_model

# NLTK setup download
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)

# Path definition
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INTENTS_PATH = os.path.join(BASE_DIR, "app", "knowledge_base", "intents.json")
MODEL_PATH = os.path.join(BASE_DIR, "ml", "trained", "chatbot_model.h5")
WORDS_PATH = os.path.join(BASE_DIR, "ml", "trained", "words.pkl")
CLASSES_PATH = os.path.join(BASE_DIR, "ml", "trained", "classes.pkl")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

# Stemmer and ignore list
stemmer = LancasterStemmer()
ignore_characters = {"?", "!", ".", ",", "'", '"', "-"}

# Confidence
CONFIDENCE_THRESHOLD = 0.65


# Model and assets loading
def _load_assets() -> dict:
    """
    Loads the model, vocabulary, classes and intents.
    Returns them as a dict so they can be stored on _state,
    replaced taken values automatically on reload.
    Raises an exception if file is missing or corrupted.
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


# State container, assets can be automatically reloaded without restarting the server
_state = _load_assets()
print(f"NLP service loaded: {len(_state['vocabulary'])} words, {len(_state['classes'])} intents.")


# Model and assets reloading
def reload_model() -> str:
    """
    Reloads all NLP assets into _state.
    Called by the admin after training is completed.
    Existing model remains active if loading fails, error message is returned.
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


# Inference
def _bag_of_words(sentence: str) -> numpy.ndarray:
    """
    Converts a sentence into a bag of words vector by matching the vocabulary.
    Sentence is lowercased and tokenized and built into a binary vector.
    Position i of the vector is 1 if vocabulary word i appears in the sentence.
    Length of the vector matches current vocabulary size in _state.
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
    Runs sentence through the model and returns the predicted intent.
    Converts sentence into a bag of words vector, runs model.predict,
    and returns the tag with the highest softmax probability.
    If confidence is below CONFIDENCE_THRESHOLD, 'unknown' is used.
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


def get_response(tag: str) -> str:
    """
    Intent tag is looked up in intents_data and returns a random response.
    Falls back to default if tag is not found.
    """
    for intent in _state["intents_data"]["intents"]:
        if intent["tag"] == tag and intent["responses"]:
            return random.choice(intent["responses"])

    return "I'm not sure how to help with that. Please contact the hostel office directly."


def get_intents() -> dict:
    """
    Returns full intents data currently loaded into _state.
    Used by admin intents endpoint to return current knowledge base.
    """
    return _state["intents_data"]


def reload_intents() -> None:
    """
    Reloads intents.json from disk into _state without reloading other values.
    Called after admin changes to intent.json are made.
    get_response uses updated responses without requiring a full model retrain.
    """
    with open(INTENTS_PATH, "r") as f:
        _state["intents_data"] = json.load(f)
    print("Intent reloaded successfully from disk.")
