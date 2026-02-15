import os
from cs50 import SQL

MIGRATIONS = [
    """
    CREATE TABLE IF NOT EXISTS question_bank (
      id SERIAL PRIMARY KEY,
      course_code TEXT NOT NULL,
      question_text TEXT NOT NULL,
      option_a TEXT,
      option_b TEXT,
      option_c TEXT,
      option_d TEXT,
      correct_answer TEXT,
      marks NUMERIC,
      minus NUMERIC,
      created_by INTEGER,
      created_at TIMESTAMP DEFAULT NOW()
    )
    """,
    """
    ALTER TABLE quizzes
      ADD COLUMN IF NOT EXISTS source_type VARCHAR(20) DEFAULT 'upload',
      ADD COLUMN IF NOT EXISTS bank_count INTEGER,
      ADD COLUMN IF NOT EXISTS bank_course_code TEXT
    """,
    """
    UPDATE quizzes
    SET source_type = 'upload'
    WHERE source_type IS NULL
    """,
    """
    ALTER TABLE quiz_attempts
      ADD COLUMN IF NOT EXISTS questions TEXT
    """,
]


def run():
    database_url = os.environ.get("DATABASE_URL", "postgresql://postgres:5253@localhost:5432/lms_db")
    db = SQL(database_url)
    for stmt in MIGRATIONS:
        db.execute(stmt)
    print("Migrations complete.")


if __name__ == "__main__":
    run()
