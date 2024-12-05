from typing import Dict, Any, Optional
from pydantic import BaseModel
import sqlite3
import os
import uuid
import json

class AdminSettings(BaseModel):
    user_id: str
    personal_info: Dict[str, Any] = {}
    business_details: Dict[str, Any] = {}
    target_countries: list = []
    competitors: list = []
    main_urls: list = []

class AdminStorage:
    def __init__(self, db_file: str = "tmp/admin.db"):
        """Initialize admin storage with SQLite backend."""
        os.makedirs(os.path.dirname(db_file), exist_ok=True)
        self.db_file = db_file
        self._init_db()

    def _init_db(self):
        """Initialize the database with required tables."""
        with sqlite3.connect(self.db_file) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS admin_settings (
                    user_id TEXT PRIMARY KEY,
                    settings TEXT NOT NULL
                )
            """)

    async def get_settings(self, user_id: str) -> AdminSettings:
        """Get settings for a specific user."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.execute(
                "SELECT settings FROM admin_settings WHERE user_id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            if not row:
                return AdminSettings(user_id=user_id)
            return AdminSettings(**json.loads(row[0]))

    async def save_settings(self, settings: AdminSettings) -> None:
        """Save settings for a specific user."""
        with sqlite3.connect(self.db_file) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO admin_settings (user_id, settings)
                VALUES (?, ?)
                """,
                (settings.user_id, json.dumps(settings.dict()))
            )

    async def delete_settings(self, user_id: str) -> None:
        """Delete settings for a specific user."""
        with sqlite3.connect(self.db_file) as conn:
            conn.execute(
                "DELETE FROM admin_settings WHERE user_id = ?",
                (user_id,)
            )

    @staticmethod
    def generate_user_id() -> str:
        """Generate a unique user ID."""
        return str(uuid.uuid4())
