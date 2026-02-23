import json
import os
import numpy as np
import nltk
from nltk.stem import LancasterStemmer

nltk.download('punkt')

stemmer = LancasterStemmer()

KNOWLEDGE_BASE_PATH = os.getenv("KNOWLEDGE_BASE_PATH", "app/knowledge_base/intents.json")

with open(KNOWLEDGE_BASE_PATH) as f:
    intents_data = json.load(f)


def preprocess_input(sentence: str) -> list:
    tokens = nltk.word_tokenize(sentence.lower())
    return [stemmer.stem(word) for word in tokens]


def predict_intent(sentence: str) -> dict:
    # Placeholder until TensorFlow model is trained
    return {}



def get_response(tag: str) -> str:
    for intent in intents_data["intents"]:
        if intent["tag"] == tag:
            return np.random.choice(intent["responses"])
    return ""
