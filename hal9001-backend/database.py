import os
import asyncio
import aiosqlite
from dotenv import load_dotenv
import psycopg
from psycopg_pool import AsyncConnectionPool
from contextlib import asynccontextmanager
from typing import Optional

# Load environment variables from .env file
load_dotenv()

# --- DATABASE CONNECTION SETUP ---
DATABASE_URL = os.getenv("DATABASE_URL")
USE_SQLITE = not DATABASE_URL or DATABASE_URL.startswith("sqlite")
pool: Optional[AsyncConnectionPool] = None

if USE_SQLITE:
    # SQLite fallback for local testing
    SQLITE_DB_PATH = "hal9001_local.db"
    print(f"Using SQLite database: {SQLITE_DB_PATH}")
else:
    # PostgreSQL async connection pool
    if DATABASE_URL:
        try:
            pool = AsyncConnectionPool(conninfo=DATABASE_URL, min_size=2, max_size=10)
            print(f"Using PostgreSQL database: {DATABASE_URL}")
        except Exception as e:
            print(f"Failed to create PostgreSQL pool: {e}")
            USE_SQLITE = True
            SQLITE_DB_PATH = "hal9001_local.db"
            print(f"Falling back to SQLite: {SQLITE_DB_PATH}")
            pool = None
    else:
        USE_SQLITE = True
        SQLITE_DB_PATH = "hal9001_local.db"
        print(f"No DATABASE_URL found, using SQLite: {SQLITE_DB_PATH}")

@asynccontextmanager
async def get_db_connection():
    """
    A context manager to get a database connection.
    Uses SQLite for local testing or PostgreSQL for production.
    """
    if USE_SQLITE:
        conn = await aiosqlite.connect(SQLITE_DB_PATH)
        conn.row_factory = aiosqlite.Row
        try:
            yield conn
        finally:
            await conn.close()
    else:
        if pool is None:
            raise RuntimeError("PostgreSQL pool not initialized")
        async with pool.connection() as conn:
            yield conn