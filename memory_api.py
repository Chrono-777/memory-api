"""
memory_api.py
================

This module implements a simple REST API using FastAPI to provide
persistent storage and retrieval of conversation snippets for a
custom GPT. The API exposes two endpoints:

* POST ``/store_memory``: Accepts a JSON payload with a ``user_id``
  and a ``message``. It appends the message to a log associated
  with the given user. If the user does not yet have a log, one
  will be created on the fly.

* GET ``/get_memory``: Returns the full conversation log for a
  ``user_id``. If no memory exists for the given user, it returns an
  empty list.

The underlying storage mechanism is a lightweight SQLite database.
Each entry in the ``memories`` table records a ``user_id``, the
timestamp when the memory was stored, and the message content. This
approach ensures persistence across API restarts without requiring
external dependencies.

This example API can be deployed to any environment that supports
Python 3.9+ and FastAPI (e.g., Replit, Vercel, or a simple
server). Once deployed, you can register actions in the Custom GPT
Builder to call ``store_memory`` and ``get_memory``. See
``memory_client.py`` for a reference implementation of how to call
this API from Python.

Usage
-----

Run the API locally for development:

    uvicorn memory_api:app --reload --port 8000

After starting the server, you can test it with curl:

    curl -X POST "http://localhost:8000/store_memory" \
         -H "Content-Type: application/json" \
         -d '{"user_id": "alice", "message": "Hello world"}'

    curl "http://localhost:8000/get_memory?user_id=alice"

These commands will add a message for ``alice`` and then retrieve
the conversation history. In production you should configure
authentication and TLS according to your needs.
"""

from datetime import datetime
from typing import List

import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class MemoryRecord(BaseModel):
    """Schema for storing a single message for a user.

    Attributes
    ----------
    user_id: str
        Identifier for the user or session. In a Custom GPT
        environment, this might correspond to a conversation ID or
        other unique token.
    message: str
        The text you want to persist in memory.
    """

    user_id: str
    message: str


def init_db(db_path: str = "memory.db") -> None:
    """Initialize the SQLite database and create the table if it
    doesn't exist.

    Parameters
    ----------
    db_path: str
        Location of the SQLite database file. Defaults to
        ``memory.db`` in the current working directory.
    """
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


def add_memory(user_id: str, message: str, db_path: str = "memory.db") -> None:
    """Store a memory in the database.

    Parameters
    ----------
    user_id: str
        Identifier for the user or session.
    message: str
        The text to store.
    db_path: str
        Location of the SQLite database file. Defaults to ``memory.db``.
    """
    conn = sqlite3.connect(db_path)
    with conn:
        conn.execute(
            "INSERT INTO memories (user_id, timestamp, message) VALUES (?, ?, ?)",
            (user_id, datetime.utcnow().isoformat(), message),
        )
    conn.close()


def get_memories(user_id: str, db_path: str = "memory.db") -> List[dict]:
    """Retrieve all memory entries for a user, ordered by timestamp.

    Parameters
    ----------
    user_id: str
        Identifier for the user or session.
    db_path: str
        Location of the SQLite database file.

    Returns
    -------
    List[dict]
        A list of dictionaries representing stored messages. Each
        dictionary has keys ``timestamp`` and ``message``.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    with conn:
        cursor = conn.execute(
            "SELECT timestamp, message FROM memories WHERE user_id = ? ORDER BY id ASC", (user_id,)
        )
        rows = cursor.fetchall()
    conn.close()
    return [{"timestamp": row["timestamp"], "message": row["message"]} for row in rows]


# Initialize the database on import. In a production setting you
# might want more robust initialization and migration handling.
init_db()


app = FastAPI(title="Custom GPT Memory API", description="An API to store and retrieve conversation memory for a Custom GPT.")


@app.post("/store_memory")
def store_memory(record: MemoryRecord):
    """Endpoint for storing a message in the database.

    Parameters
    ----------
    record: MemoryRecord
        The payload containing ``user_id`` and ``message``.

    Returns
    -------
    dict
        Confirmation message.
    """
    try:
        add_memory(record.user_id, record.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"status": "success", "message": "Memory stored"}


@app.get("/get_memory")
def get_memory(user_id: str):
    """Endpoint for retrieving all messages stored for a user.

    Parameters
    ----------
    user_id: str
        Identifier for the user or session.

    Returns
    -------
    dict
        A dictionary containing the list of messages.
    """
    try:
        memories = get_memories(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"user_id": user_id, "memories": memories}