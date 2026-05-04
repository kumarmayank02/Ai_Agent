import psycopg2
from datetime import datetime

print("PostgreSQL connected")

conn = psycopg2.connect(
    host="localhost",
    database="career_copilot",
    user="postgres",
    password="root"   # apna actual password
)

def init_db():
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_profile(
        id SERIAL PRIMARY KEY,
        skills TEXT,
        resume_text TEXT,
        created_at TIMESTAMP
    )
    """)
    conn.commit()

def save_profile(skills, resume_text):
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO user_profile(skills,resume_text,created_at)
    VALUES(%s,%s,%s)
    """,(",".join(skills), resume_text, datetime.now()))
    conn.commit()

def load_latest_profile():
    cur = conn.cursor()
    cur.execute("SELECT skills,resume_text FROM user_profile ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()

    if row:
        return {
            "skills": row[0].split(","),
            "resume_text": row[1]
        }
    return None
