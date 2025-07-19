from datetime import datetime
from typing import List
import os
import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Vercel上で書き込み可能な一時フォルダを利用
DB_PATH = "/tmp/memory.db"

class MemoryRecord(BaseModel):
    user_id: str
    message: str

def init_db(db_path: str = DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                message TEXT NOT NULL
            )
            """
        )
    conn.close()

def add_memory(user_id: str, message: str, db_path: str = DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    with conn:
        conn.execute(
            "INSERT INTO memories (user_id, timestamp, message) VALUES (?, ?, ?)",
            (user_id, datetime.utcnow().isoformat(), message),
        )
    conn.close()

def get_memories(user_id: str, db_path: str = DB_PATH) -> List[dict]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    with conn:
        cursor = conn.execute(
            "SELECT timestamp, message FROM memories WHERE user_id = ? ORDER BY id ASC",
            (user_id,),
        )
        rows = cursor.fetchall()
    conn.close()
    return [{"timestamp": row["timestamp"], "message": row["message"]} for row in rows]

# DBの初期化を行う
init_db()

app = FastAPI(
    title="Custom GPT Memory API",
    description="An API to store and retrieve conversation memory for a Custom GPT.",
)

@app.post("/store_memory")
def store_memory(record: MemoryRecord):
    try:
        add_memory(record.user_id, record.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"status": "success", "message": "Memory stored"}

@app.get("/get_memory")
def get_memory(user_id: str):
    try:
        memories = get_memories(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"user_id": user_id, "memories": memories}
