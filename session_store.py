import sqlite3
import json
import os
from typing import Optional, Dict, Any
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "sessions.db")

class StateEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "dict"):
            return obj.dict()
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            candidate_id TEXT NOT NULL,
            state_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def create_session(session_id: str, candidate_id: str, initial_state: Dict[str, Any]):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    c.execute('''
        INSERT INTO sessions (session_id, candidate_id, state_json, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (session_id, candidate_id, json.dumps(initial_state, cls=StateEncoder), now, now))
    conn.commit()
    conn.close()

def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT state_json FROM sessions WHERE session_id = ?', (session_id,))
    row = c.fetchone()
    conn.close()
    
    if row:
        return json.loads(row[0])
    return None

def save_session(session_id: str, state: Dict[str, Any]):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    c.execute('''
        UPDATE sessions
        SET state_json = ?, updated_at = ?
        WHERE session_id = ?
    ''', (json.dumps(state, cls=StateEncoder), now, session_id))
    conn.commit()
    conn.close()

def delete_session(session_id: str):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM sessions WHERE session_id = ?', (session_id,))
    conn.commit()
    conn.close()
