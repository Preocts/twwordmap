"""
Use sqlite3 to store/access tweet searches
"""
import sqlite3
from contextlib import contextmanager
from typing import Generator
from typing import List
from typing import Optional

from twitterapiv2.model.recent.data import Data


class DataStore:
    def __init__(self, filename: str = ":memory:") -> None:
        """Without a filename uses memory only. Connect using `.connection()` context"""
        self.filename = filename
        self.db: Optional[sqlite3.Connection] = None

    def build_table(self) -> None:
        """Builds table if it doesn't exist"""
        if self.db is None:
            raise Exception("No database connection exists.")
        cursor = self.db.cursor()
        sql = (
            "CREATE TABLE IF NOT EXISTS data "
            "(id TEXT PRIMARY KEY, created_at TEXT, content TEXT)"
        )
        try:
            cursor.execute(sql)
            self.db.commit()
        finally:
            cursor.close()

    def insert_rows(self, tweets: List[Data]) -> None:
        """Insert tweets contained in Data"""
        if self.db is None:
            raise Exception("No database connection exists.")
        cursor = self.db.cursor()
        sql = "INSERT OR REPLACE INTO data (id, created_at, content) VALUES (?, ?, ?)"
        try:
            for tweet in tweets:
                cursor.execute(sql, (tweet.id, tweet.created_at, tweet.text))
            self.db.commit()
        finally:
            cursor.close()

    def get_text(self) -> List[List[str]]:
        if self.db is None:
            raise Exception("No database connection exists.")
        cursor = self.db.cursor()
        sql = "SELECT content FROM data"
        try:
            cursor.execute(sql)
            return cursor.fetchall()
        finally:
            cursor.close()

    @contextmanager
    def connection(self) -> Generator["DataStore", None, None]:
        """Open/Create database and ensure proper close on exit"""
        if self.db is not None:
            raise Exception("Unexpected connection call while already connected.")
        self.db = sqlite3.connect(self.filename)
        try:
            self.build_table()
            yield self
        finally:
            self.db.close()
            self.db = None
