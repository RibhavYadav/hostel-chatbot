import os

from dotenv import load_dotenv

load_dotenv()

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Knowledge base paths
KNOWLEDGE_BASE_DIR = os.path.join(BASE_DIR, "app", "knowledge_base")
DOCUMENTS_DIR = os.path.join(KNOWLEDGE_BASE_DIR, "documents")
INDEX_DIR = os.path.join(KNOWLEDGE_BASE_DIR, "index")
INTENTS_PATH = os.path.join(KNOWLEDGE_BASE_DIR, "intents.json")

# ML paths
ML_DIR = os.path.join(BASE_DIR, "ml")
TRAINED_DIR = os.path.join(ML_DIR, "trained")
TRAIN_SCRIPT = os.path.join(ML_DIR, "train.py")
MODEL_PATH = os.path.join(TRAINED_DIR, "chatbot_model.h5")
WORDS_PATH = os.path.join(TRAINED_DIR, "words.pkl")
CLASSES_PATH = os.path.join(TRAINED_DIR, "classes.pkl")

# Data paths
DATA_DIR = os.path.join(BASE_DIR, "data")
STUDENT_CSV_PATH = os.path.join(DATA_DIR, "student_data.csv")
ADMIN_CSV_PATH = os.path.join(DATA_DIR, "admin_data.csv")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hostel.db")

# JWT
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))
