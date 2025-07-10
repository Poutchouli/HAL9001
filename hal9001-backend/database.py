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

# PostgreSQL async connection pool
try:
    pool = AsyncConnectionPool(conninfo=DATABASE_URL, min_size=2, max_size=10)
    print(f"Using PostgreSQL database: {DATABASE_URL}")
except Exception as e:
    raise RuntimeError(f"Failed to create PostgreSQL pool: {e}")

@asynccontextmanager
async def get_db_connection():
    """
    A context manager to get a PostgreSQL database connection.
    """
    async with pool.connection() as conn:
        yield conn