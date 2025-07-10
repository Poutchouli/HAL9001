# HAL9001 Permissions API

A secure API Gateway for offline-first data synchronization with user permissions management.

## Overview

HAL9001 is a FastAPI-based application that provides user and table permissions management with a clean web interface. It features:

- User management with role-based access
- Table-level permissions (SELECT, INSERT, UPDATE, DELETE)
- PostgreSQL database backend
- Modern web UI for administration
- RESTful API endpoints

## Features

- **User Management**: Manage users with different roles (Data Editor, Data Viewer, Tenant Admin, System Admin)
- **Permission Control**: Granular table-level permissions for each user
- **Database Integration**: PostgreSQL with async connection handling
- **Web Interface**: Clean, modern UI for managing users and permissions
- **API Documentation**: Auto-generated Swagger/OpenAPI documentation

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL database
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/HAL9001.git
cd HAL9001
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

3. Install dependencies:
```bash
cd hal9001-backend
pip install -r requirements.txt
```

4. Set up your database connection in `hal9001-backend/.env`:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/hal9001
```

5. Run the application:
```bash
python main.py
```

The API will be available at `http://localhost:8000` and the web interface can be accessed by opening `UI.html` in your browser.

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/v1/admin/users` - Get all users
- `GET /api/v1/admin/tables` - Get all managed tables
- `GET /api/v1/admin/permissions/{user_id}` - Get permissions for a user
- More endpoints coming soon...

## Project Structure

```
HAL9001/
├── hal9001-backend/          # Backend API
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database connection
│   ├── requirements.txt     # Python dependencies
│   └── .env                # Environment variables
├── UI.html                  # Frontend interface
├── README.md               # This file
└── .venv/                  # Virtual environment
```

## Development

The application uses:
- **FastAPI** for the REST API
- **PostgreSQL** with **psycopg** for database operations
- **Uvicorn** as the ASGI server
- **Async/await** for database operations

## License

This project is licensed under the MIT License.
