import os
import uvicorn
import logging
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
from contextlib import asynccontextmanager
from database import get_db_connection
from psycopg.rows import dict_row
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration from environment
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Configure logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL))
logger = logging.getLogger(__name__)

# --- MOCK DATA FOR INITIAL SETUP (from UI.html) ---
MOCK_USERS = [
  {'id': 'usr_001', 'name': 'Dave Bowman', 'role': 'Data Editor', 'email': 'd.bowman@discovery.co'},
  {'id': 'usr_002', 'name': 'Frank Poole', 'role': 'Data Viewer', 'email': 'f.poole@discovery.co'},
  {'id': 'usr_003', 'name': 'Admin User', 'role': 'Tenant Admin', 'email': 'admin@discovery.co'},
  {'id': 'usr_004', 'name': 'System Architect', 'role': 'System Admin', 'email': 'sysarch@system.co'},
]

MOCK_TABLES = [
  'crew_vitals_log', 'pod_bay_doors_status', 'discovery_one_systems',
  'monolith_observations_secure', 'mission_critical_data'
]

MOCK_INITIAL_PERMISSIONS = {
  'usr_001': {
    'crew_vitals_log': {'can_select': True, 'can_insert': True, 'can_update': True, 'can_delete': False},
    'pod_bay_doors_status': {'can_select': True, 'can_insert': True, 'can_update': True, 'can_delete': False},
    'discovery_one_systems': {'can_select': True, 'can_insert': False, 'can_update': False, 'can_delete': False},
  },
  'usr_002': {
    'crew_vitals_log': {'can_select': True, 'can_insert': False, 'can_update': False, 'can_delete': False},
    'discovery_one_systems': {'can_select': True, 'can_insert': False, 'can_update': False, 'can_delete': False},
  },
  'usr_003': {
    'crew_vitals_log': {'can_select': True, 'can_insert': True, 'can_update': True, 'can_delete': True},
    'pod_bay_doors_status': {'can_select': True, 'can_insert': True, 'can_update': True, 'can_delete': True},
    'discovery_one_systems': {'can_select': True, 'can_insert': True, 'can_update': True, 'can_delete': True},
  },
}


async def setup_database():
    """
    Function to create tables and populate them with initial mock data.
    This function is called once when the application starts.
    """
    logger.info("Setting up database...")
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            # Create users table
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL
                );
            """)
            logger.info("Users table created or exists.")

            # Create the permissions table
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS user_table_permissions (
                    user_id TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    can_select BOOLEAN DEFAULT FALSE,
                    can_insert BOOLEAN DEFAULT FALSE,
                    can_update BOOLEAN DEFAULT FALSE,
                    can_delete BOOLEAN DEFAULT FALSE,
                    PRIMARY KEY(user_id, table_name)
                );
            """)
            logger.info("Permissions table created or exists.")

            # Check if tables are empty
            await cur.execute("SELECT COUNT(*) FROM users")
            result = await cur.fetchone()
            is_empty = result[0] == 0 if result else True

            if is_empty:
                logger.info("Database is empty. Populating with initial mock data...")
                # Populate users table
                for user in MOCK_USERS:
                    await cur.execute("""
                        INSERT INTO users (id, name, role, email)
                        VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO NOTHING;
                    """, (user['id'], user['name'], user['role'], user['email']))
                logger.info(f"Populated users table with {len(MOCK_USERS)} users.")

                # Populate permissions table
                for user_id, perms in MOCK_INITIAL_PERMISSIONS.items():
                    for table_name, actions in perms.items():
                        await cur.execute("""
                            INSERT INTO user_table_permissions
                            (user_id, table_name, can_select, can_insert, can_update, can_delete)
                            VALUES (%s, %s, %s, %s, %s, %s);
                        """, (
                            user_id, table_name,
                            actions.get('can_select', False),
                            actions.get('can_insert', False),
                            actions.get('can_update', False),
                            actions.get('can_delete', False)
                        ))
                logger.info("Populated permissions table.")
            else:
                logger.info("Database already contains data. Skipping initial population.")

            await conn.commit()
    logger.info("Database setup complete.")


# --- LIFESPAN MANAGEMENT ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup
    await setup_database()
    yield
    # On shutdown (optional cleanup)
    print("API shutting down.")


# --- APPLICATION SETUP ---
app = FastAPI(
    title="HAL9001 API",
    version="1.0",
    description="Secure API Gateway for offline-first data synchronization.",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,  # Configured via environment variable
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Pydantic models for request validation ---
class PermissionUpdate(BaseModel):
    user_id: str
    permissions: Dict[str, Dict[str, bool]]


# --- API ENDPOINTS ---
@app.get("/api/health", tags=["System"])
async def health_check():
    """Endpoint to verify that the API is running."""
    return {"status": "ok", "message": "HAL9001 API is online."}


@app.get("/api/v1/admin/users", tags=["Admin"], summary="Get All Users")
async def get_all_users():
    """Retrieves a list of all users from the database."""
    async with get_db_connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute("SELECT id, name, role, email FROM users ORDER BY name;")
            users = await cur.fetchall()
            return users

@app.get("/api/v1/admin/tables", tags=["Admin"], summary="Get All Managed Tables")
async def get_all_tables():
    """Returns a hardcoded list of tables that can be managed."""
    return MOCK_TABLES

@app.get("/api/v1/admin/permissions/{user_id}", tags=["Admin"], summary="Get Permissions for a User")
async def get_user_permissions(user_id: str):
    """
    Retrieves a map of table permissions for a specific user.
    """
    async with get_db_connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "SELECT table_name, can_select, can_insert, can_update, can_delete FROM user_table_permissions WHERE user_id = %s;",
                (user_id,)
            )
            permissions = {}
            records = await cur.fetchall()
            for record in records:
                permissions[record['table_name']] = {
                    "can_select": record['can_select'],
                    "can_insert": record['can_insert'],
                    "can_update": record['can_update'],
                    "can_delete": record['can_delete'],
                }
            return permissions

@app.post("/api/v1/admin/permissions", tags=["Admin"], summary="Update User Permissions")
async def update_user_permissions(update: PermissionUpdate):
    """
    Updates permissions for a specific user.
    """
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            # First, delete existing permissions for this user
            await cur.execute(
                "DELETE FROM user_table_permissions WHERE user_id = %s;",
                (update.user_id,)
            )
            
            # Insert new permissions
            for table_name, perms in update.permissions.items():
                await cur.execute("""
                    INSERT INTO user_table_permissions
                    (user_id, table_name, can_select, can_insert, can_update, can_delete)
                    VALUES (%s, %s, %s, %s, %s, %s);
                """, (
                    update.user_id, 
                    table_name,
                    perms.get('can_select', False),
                    perms.get('can_insert', False),
                    perms.get('can_update', False),
                    perms.get('can_delete', False)
                ))
            
            await conn.commit()
            
            return {
                "status": "success", 
                "message": f"Permissions updated for user {update.user_id}",
                "user_id": update.user_id,
                "updated_tables": list(update.permissions.keys())
            }


# --- SERVER BOOTSTRAP ---
if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host=API_HOST, 
        port=API_PORT, 
        reload=DEBUG,
        log_level=LOG_LEVEL.lower()
    )
