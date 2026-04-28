import json
import os
import pickle

import nltk
import numpy
from nltk.stem.lancaster import LancasterStemmer
from nltk.tokenize import word_tokenize
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.losses import CategoricalCrossentropy
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam

# NLTK setup download
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTENTS_PATH = os.path.join(BASE_DIR, "app", "knowledge_base", "intents.json")
TRAINED_DIR = os.path.join(BASE_DIR, "ml", "trained")

# Loading data
with open(INTENTS_PATH, "r") as f:
    intents = json.load(f)["intents"]
print(f"Loaded {len(intents)} intents from intents.json")

# Building vocabulary
stemmer = LancasterStemmer()
ignore_characters = {"?", "!", ".", ",", "'", '"', "-"}
vocabulary = []
classes = []

for intent in intents:
    # Collecting unique intent tags
    if intent["tag"] not in classes:
        classes.append(intent["tag"])

    # Tokenizing and stemming every pattern
    for text in intent["patterns"]:
        tokens = word_tokenize(text.lower())
        for word in tokens:
            if word not in ignore_characters:
                vocabulary.append(stemmer.stem(word))

vocabulary = sorted(list(set(vocabulary)))
classes = sorted(list(set(classes)))
print(f"\nNumber of intents: {len(classes)}")
print(f"Classes: {classes}")
print(f"Vocabulary size: {len(vocabulary)}")

# Preparing training arrays
training_sentences = []
training_labels = []

for intent in intents:
    for text in intent["patterns"]:
        # Tokenization and stemmed words of individual patterns
        tokens = word_tokenize(text.lower())
        stemmed = [stemmer.stem(w) for w in tokens if w not in ignore_characters]

        # Bag of words 1 if vocabulary word is in the pattern, else 0
        bag = [1 if word in stemmed else 0 for word in vocabulary]
        training_sentences.append(bag)

        # One hot label
        label = [0] * len(classes)
        label[classes.index(intent["tag"])] = 1
        training_labels.append(label)

X_train = numpy.array(training_sentences)
y_train = numpy.array(training_labels)
print(f"\nX_train shape: {X_train.shape}")
print(f"y_train shape: {y_train.shape}")

# Model definition
model = Sequential(
    [
        Dense(128, input_shape=(len(vocabulary),), activation="relu"),
        Dropout(0.5),
        Dense(64, activation="relu"),
        Dropout(0.5),
        Dense(len(classes), activation="softmax"),
    ]
)

model.compile(optimizer=Adam(learning_rate=0.001), loss=CategoricalCrossentropy(), metrics=["accuracy"])
model.summary()

# Model training
print("\nModel training has begun")
history = model.fit(X_train, y_train, epochs=200, batch_size=8, verbose=15)
final_accuracy = history.history["accuracy"][-1]
print(f"\nFinal accuracy: {final_accuracy:.4f}")

# Saving model, words and classes
os.makedirs(TRAINED_DIR, exist_ok=True)
model.save(os.path.join(TRAINED_DIR, "chatbot_model.h5"))

with open(os.path.join(TRAINED_DIR, "words.pkl"), "wb") as f:
    pickle.dump(vocabulary, f)

with open(os.path.join(TRAINED_DIR, "classes.pkl"), "wb") as f:
    pickle.dump(classes, f)

print(f"Saved: chatbot_model.h5, words.pkl, classes.pkl, to {TRAINED_DIR}:")
