from datetime import datetime
from typing import List
import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

DB_PATH = "/tmp/memory.db"

class MemoryRecord(BaseModel):
    user_id: str
    message: str

def init_db(db_path: str = DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                message TEXT NOT NULL
            )
        """)
    conn.close()

def add_memory(user_id: str, message: str, db_path: str = DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    with conn:
        conn.execute(
            "INSERT INTO memories (user_id, timestamp, message) VALUES (?, ?, ?)",
            (user_id_
