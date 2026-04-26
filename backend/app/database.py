import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import ADMIN_CSV_PATH, DATABASE_URL, STUDENT_CSV_PATH

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
    Called once at FastAPI startup via the on_startup event in main.py.
    Creates all database tables if they do not already exist.
    Loads student_data.csv into the admin_students table on first run.
    Loads admin_data.csv into the admin_data table on first run.
    Both CSV loads are skipped if the respective table already has rows,
    preventing duplicate inserts on subsequent server restarts.
    """
    from app.models.db_models import AdminData, AdminStudent

    Base.metadata.create_all(bind=engine)
    print("Database tables created.")

    db = SessionLocal()
    try:
        # Student CSV loading
        if db.query(AdminStudent).count() == 0:
            if os.path.exists(STUDENT_CSV_PATH):
                with open(STUDENT_CSV_PATH, "r") as f:
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

        # Admin CSV loading
        if db.query(AdminData).count() == 0:
            if os.path.exists(ADMIN_CSV_PATH):
                with open(ADMIN_CSV_PATH, "r") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        admin_data = AdminData(
                            email=row["email"],
                            admin_team=row["admin_team"],
                        )
                        db.add(admin_data)
                db.commit()
                print("Admin data loaded from CSV.")
            else:
                print("Warning: data/admin_data.csv not found. Admin table is empty.")
    finally:
        db.close()
