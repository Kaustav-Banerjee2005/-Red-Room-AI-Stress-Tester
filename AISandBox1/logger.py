import sqlite3
from datetime import datetime

DB_NAME = "logs.db"


def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        model_name TEXT,
        user_input TEXT,
        llm_output TEXT,
        flagged INTEGER,
        categories TEXT,
        severity TEXT,
        confidence REAL,
        action TEXT
    )
    """)

    conn.commit()
    conn.close()


def log_event(model_name, user_input, llm_output, risk, action):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO logs(
        timestamp,
        model_name,
        user_input,
        llm_output,
        flagged,
        categories,
        severity,
        confidence,
        action
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        model_name,
        user_input,
        llm_output,
        int(risk.get("flagged", False)),
        ",".join(risk.get("categories", [])),
        risk.get("severity"),
        risk.get("confidence"),
        action
    ))

    conn.commit()
    conn.close()