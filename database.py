# database.py
import sqlite3
from contextlib import contextmanager
import contextlib as ctxlib

DATABASE_URL = "sqlite:///./central_server.db" # Or just "./central_server.db" for relative path

def get_db_connection():
    conn = sqlite3.connect(DATABASE_URL.replace("sqlite:///./", ""), check_same_thread=False)
    conn.row_factory = sqlite3.Row # Allows accessing rows as dictionaries
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lecturers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sch_id TEXT UNIQUE,
            rfid_uid TEXT UNIQUE, -- Fingerprint/Card UID from enrollment
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sch_id TEXT UNIQUE, 
            rfid_uid TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            code TEXT PRIMARY KEY,
            course_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lecture_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_code TEXT NOT NULL,
            lecturer_id INTEGER NOT NULL, -- Lecturer for this specific session
            session_date TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (course_code) REFERENCES courses(code) ON DELETE RESTRICT,
            FOREIGN KEY (lecturer_id) REFERENCES lecturers(id) ON DELETE RESTRICT
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance_records (
            session_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            attendance_time TIMESTAMP NOT NULL,
            attended BOOLEAN NOT NULL DEFAULT 1,
            PRIMARY KEY (session_id, student_id),
            FOREIGN KEY (session_id) REFERENCES lecture_sessions(id) ON DELETE CASCADE,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE RESTRICT
        );
    """)
    conn.commit()
    print("Database initialized successfully.")
    conn.close()

# Context manager for database sessions in FastAPI
@contextmanager
def get_db():
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()



####################################################
########## Used to aquire a database conn ##########
# with ctxlib.closing(get_db_connection()) as db_gen:
#     db = next(db_gen)
#     cursor = db.cursor()
#     # handle database operations here
#     db.commit()