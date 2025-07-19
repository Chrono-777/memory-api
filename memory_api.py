from fastapi import FastAPI, HTTPException
import sqlite3
from datetime import datetime
from pydantic import BaseModel
import traceback

DB_PATH = "/tmp/memory.db"

app = FastAPI()

class MemoryRecord(BaseModel):
    user_id: str
    message: str

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY, user_id TEXT, timestamp TEXT, message TEXT)"
    )
    conn.close()

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI on Vercel!"}

@app.post("/store_memory")
async def store_memory(record: MemoryRecord):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT INTO memories (user_id, timestamp, message) VALUES (?, ?, ?)",
            (record.user_id, datetime.utcnow().isoformat(), record.message),
        )
        conn.commit()
        conn.close()
        return {"status": "success"}
    except Exception as e:
        error = traceback.format_exc()
        raise HTTPException(status_code=500, detail=error)

@app.get("/get_memory")
async def get_memory(user_id: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.execute(
            "SELECT timestamp, m
