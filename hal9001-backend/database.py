import os
from dotenv import load_dotenv
import psycopg
from psycopg_pool import AsyncConnectionPool
from contextlib import asynccontextmanager
from typing import Optional

# Load environment variables from .env file
load_dotenv()

# --- DATABASE CONNECTION SETUP ---
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is required")

# Global pool variable
pool = None

async def get_pool():
    """Get or create the connection pool"""
    global pool
    if pool is None:
        try:
            pool = AsyncConnectionPool(conninfo=DATABASE_URL, min_size=2, max_size=10)
            print(f"Created PostgreSQL pool: {DATABASE_URL}")
        except Exception as e:
            raise RuntimeError(f"Failed to create PostgreSQL pool: {e}")
    return pool

@asynccontextmanager
async def get_db_connection():
    """
    A context manager to get a PostgreSQL database connection.
    """
    connection_pool = await get_pool()
    async with connection_pool.connection() as conn:
        yield conn