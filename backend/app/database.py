import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Engine setup for SQLite with FastAPI
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hostel.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# FastAPI dependency
def get_db():
    """
    Yields a database session for a single request.
    Closes the session when the request is done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Database initialization
def init_db():
    """
    Called once at the start of FastAPI.
    Creates all tables if required.
    Loads student data into admin_students table if it is empty.
    """
    from app.models.db_models import AdminStudent

    Base.metadata.create_all(bind=engine)
    print("Database tables created.")

    db = SessionLocal()
    try:
        if db.query(AdminStudent).count() == 0:
            csv_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "data",
                "student_data.csv",
            )
            if os.path.exists(csv_path):
                with open(csv_path, "r") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        admin_student = AdminStudent(
                            registration_number=int(row["registration_number"]),
                            name=row["name"],
                            email=row["email"],
                            department=row["department"],
                        )
                        db.add(admin_student)
                db.commit()
                print("Admin student data loaded from CSV.")
            else:
                print("Warning: data/student_data.csv not found. Admin table is empty.")
    finally:
        db.close()
