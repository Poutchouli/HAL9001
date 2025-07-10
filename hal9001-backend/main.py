import uvicorn
import logging
from fastapi import FastAPI, Depends, HTTPException, status
from typing import List
from contextlib import asynccontextmanager
from database import get_db_connection
from psycopg.rows import dict_row

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
    print("Setting up database...")
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
            print("Users table created or exists.")

            # Create the permissions table as defined in the blueprint
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
            print("Permissions table created or exists.")

            # Populate users table (ignore conflicts if already exists)
            for user in MOCK_USERS:
                await cur.execute("""
                    INSERT INTO users (id, name, role, email)
                    VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO NOTHING;
                """, (user['id'], user['name'], user['role'], user['email']))
            print(f"Populated users table with {len(MOCK_USERS)} users.")

            # Populate permissions table
            # Clear existing permissions to ensure a clean slate on restart
            await cur.execute("DELETE FROM user_table_permissions;")
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
            print("Populated permissions table.")
            await conn.commit()
    print("Database setup complete.")


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


# --- API ENDPOINTS ---
@app.get("/api/health", tags=["System"])
async def health_check():
    """Endpoint to verify that the API is running."""
    return {"status": "ok", "message": "HAL9001 API is online."}


@app.get("/api/v1/admin/users", tags=["Admin"], summary="Get All Users")
async def get_all_users(conn=Depends(get_db_connection)):
    """Retrieves a list of all users from the database."""
    async with conn.cursor(row_factory=dict_row) as cur:
        await cur.execute("SELECT id, name, role, email FROM users ORDER BY name;")
        users = await cur.fetchall()
        return users

@app.get("/api/v1/admin/tables", tags=["Admin"], summary="Get All Managed Tables")
async def get_all_tables():
    """Returns a hardcoded list of tables that can be managed."""
    return MOCK_TABLES

@app.get("/api/v1/admin/permissions/{user_id}", tags=["Admin"], summary="Get Permissions for a User")
async def get_user_permissions(user_id: str, conn=Depends(get_db_connection)):
    """
    Retrieves a map of table permissions for a specific user.
    """
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

# ... We will add the POST endpoint next ...


# --- SERVER BOOTSTRAP ---
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)