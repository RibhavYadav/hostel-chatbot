import json
import os
import pickle
import random
import numpy
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem.lancaster import LancasterStemmer
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

# Loading intents, vocabulary, classes and the model
stemmer = LancasterStemmer()

with open(INTENTS_PATH, "r") as f:
    intents_data = json.load(f)

with open(WORDS_PATH, "rb") as f:
    vocabulary = pickle.load(f)

with open(CLASSES_PATH, "rb") as f:
    classes = pickle.load(f)

model = load_model(MODEL_PATH)
print(f"NLP service loaded: {len(vocabulary)} words, {len(classes)} intents")

# Inference
CONFIDENCE_THRESHOLD = 0.65
ignore_characters = {"?", "!", ".", ",", "'", '"', "-"}


def _bag_of_words(sentence: str) -> numpy.ndarray:
    """Convert a sentence into a bag of words vector matching the vocabulary."""
    tokens = word_tokenize(sentence.lower())
    stemmed = [stemmer.stem(w) for w in tokens if w not in ignore_characters]
    bag = [1 if word in stemmed else 0 for word in vocabulary]
    return numpy.array(bag)


def predict_intent(sentence: str) -> dict:
    """
    Run the sentence through the model and return the predicted intent.
    Returns a dict with keys: tag, confidence
    Falls back to 'unknown' if confidence is below threshold.
    """
    bow = _bag_of_words(sentence)
    input_data = numpy.array([bow])

    predictions = model.predict(input_data, verbose=0)[0]

    best_index = int(numpy.argmax(predictions))
    best_confidence = float(predictions[best_index])

    if best_confidence < CONFIDENCE_THRESHOLD:
        return {"tag": "unknown", "confidence": best_confidence}

    return {"tag": classes[best_index], "confidence": best_confidence}


def get_response(tag: str) -> str:
    """
    Search for the intent tag in intents.json and return a random response.
    Falls back to a default message if the tag is not found.
    """
    for intent in intents_data["intents"]:
        if intent["tag"] == tag:
            if intent["responses"]:
                return random.choice(intent["responses"])

    return "I'm not sure how to help with that. Please contact the hostel office directly."
