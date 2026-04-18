import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / os.getenv("SESSION_DB", "sessions.db")


def _get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            user_id TEXT PRIMARY KEY,
            description TEXT,
            symptoms TEXT,
            impact TEXT,
            ci TEXT,
            incident_id TEXT,
            state TEXT
        )
        """
    )
    return conn


CONN = _get_conn()


@dataclass
class Session:
    user_id: str
    description: str | None = None
    symptoms: str | None = None
    impact: str | None = None
    ci: str | None = None
    incident_id: str | None = None
    state: str = "init"

    def save(self):
        CONN.execute(
            """
            INSERT INTO sessions (user_id, description, symptoms, impact, ci, incident_id, state)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                description=excluded.description,
                symptoms=excluded.symptoms,
                impact=excluded.impact,
                ci=excluded.ci,
                incident_id=excluded.incident_id,
                state=excluded.state
            """,
            (
                self.user_id,
                self.description,
                self.symptoms,
                self.impact,
                self.ci,
                self.incident_id,
                self.state,
            ),
        )
        CONN.commit()

    def reset(self):
        self.description = None
        self.symptoms = None
        self.impact = None
        self.ci = None
        self.incident_id = None
        self.state = "init"
        self.save()


def get_session(user_id):
    row = CONN.execute(
        "SELECT description, symptoms, impact, ci, incident_id, state FROM sessions WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    if row:
        session = Session(
            user_id=user_id,
            description=row[0],
            symptoms=row[1],
            impact=row[2],
            ci=row[3],
            incident_id=row[4],
            state=row[5] or "init",
        )
    else:
        session = Session(user_id=user_id)
        session.save()
    return session
