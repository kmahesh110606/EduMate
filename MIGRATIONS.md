# Database migrations

Run these once to add the question bank and quiz metadata.

## Option A: Using pgAdmin or psql

```sql
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
);

ALTER TABLE quizzes
  ADD COLUMN IF NOT EXISTS source_type VARCHAR(20) DEFAULT 'upload',
  ADD COLUMN IF NOT EXISTS bank_count INTEGER,
  ADD COLUMN IF NOT EXISTS bank_course_code TEXT;

UPDATE quizzes
SET source_type = 'upload'
WHERE source_type IS NULL;

ALTER TABLE quiz_attempts
  ADD COLUMN IF NOT EXISTS questions TEXT;
```

## Option B: Using the helper script

1) Set `DATABASE_URL`
2) Run:

```bash
python migrate.py
```
