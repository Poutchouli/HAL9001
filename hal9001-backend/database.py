import os
from dotenv import load_dotenv
from psycopg_pool import ConnectionPool
from contextlib import asynccontextmanager

# Load environment variables from .env file
load_dotenv()

# --- DATABASE CONNECTION SETUP ---
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create a connection pool. This is more efficient than creating new connections
# for every request. The pool will be managed by FastAPI's lifespan events.
pool = ConnectionPool(conninfo=DATABASE_URL)

@asynccontextmanager
async def get_db_connection():
    """
    A context manager to get a connection from the pool.
    It ensures the connection is returned to the pool.
    """
    conn = None
    try:
        conn = pool.getconn()
        yield conn
    finally:
        if conn:
            pool.putconn(conn)