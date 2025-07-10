import sqlite3
import aiosqlite
from contextlib import asynccontextmanager

# --- DATABASE CONNECTION SETUP FOR TESTING ---
DATABASE_PATH = "hal9001_test.db"

@asynccontextmanager
async def get_db_connection():
    """
    A context manager to get an SQLite connection for testing.
    """
    conn = None
    try:
        conn = await aiosqlite.connect(DATABASE_PATH)
        conn.row_factory = aiosqlite.Row  # Enable dict-like access to rows
        yield conn
    finally:
        if conn:
            await conn.close()
