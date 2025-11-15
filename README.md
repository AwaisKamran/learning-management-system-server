# Learning Management System Server

This repository contains a FastAPI-based server for a Learning Management System. The server uses SQLAlchemy for database operations and Supabase Auth API for user authentication.

## Features

- **User Management**: Complete CRUD operations for users
- **Authentication**: User registration and login with JWT tokens via Supabase Auth
- **SQLAlchemy Integration**: Async database operations using SQLAlchemy
- **Supabase Auth API**: Direct HTTP integration with Supabase authentication

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── database.py          # SQLAlchemy database setup
│   ├── models/              # Pydantic models
│   │   ├── __init__.py
│   │   └── user.py          # User models
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   └── user_service.py  # User service
│   └── routers/             # API routes
│       ├── __init__.py
│       └── users.py         # User endpoints
├── requirements.txt         # Python dependencies
└── README.md
```

## Setup

### Prerequisites

- Python 3.8 or higher
- A Supabase account and project

### Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd learning-management-system-server
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   
   Create a `.env` file in the root directory:
   ```env
   # Database connection string (required)
   DATABASE_URL=postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres
   
   # Supabase Auth API credentials (required)
   SUPABASE_KEY=your_supabase_anon_key
   SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
   
   # Optional: If connection string doesn't contain Supabase URL, provide it explicitly
   # SUPABASE_URL=https://[project-ref].supabase.co
   ```
   
   **Finding your credentials:**
   - **Connection String**: Go to Supabase Dashboard > Settings > Database > Connection string
   - **API Keys**: Go to Supabase Dashboard > Settings > API
     - Copy the "anon/public" key for `SUPABASE_KEY`
     - Copy the "service_role" key for `SUPABASE_SERVICE_ROLE_KEY`
   - **Project URL**: Will be automatically extracted from the connection string, or provide it explicitly

### Running the Server

Start the development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

- API Documentation (Swagger UI): `http://localhost:8000/docs`
- Alternative API Documentation (ReDoc): `http://localhost:8000/redoc`

## API Endpoints

### User Management

#### Register a new user
```http
POST /api/users/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe",
  "phone": "+1234567890"
}
```

#### Login
```http
POST /api/users/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

Returns:
```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer",
  "user": {
    "id": "user_id",
    "email": "user@example.com",
    "full_name": "John Doe",
    "phone": "+1234567890",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": null
  }
}
```

#### Get user by ID
```http
GET /api/users/{user_id}
```

#### Update user
```http
PUT /api/users/{user_id}
Content-Type: application/json

{
  "email": "newemail@example.com",
  "full_name": "Jane Doe",
  "phone": "+0987654321",
  "password": "newpassword123"
}
```

#### Delete user
```http
DELETE /api/users/{user_id}
```

## Development

### Code Structure

- **Models** (`app/models/`): Pydantic models for request/response validation
- **Services** (`app/services/`): Business logic and Supabase Auth API interactions
- **Routers** (`app/routers/`): API endpoint definitions
- **Database** (`app/database.py`): SQLAlchemy async engine and session management
- **Config** (`app/config.py`): Environment-based configuration with connection string parsing

### Adding New Features

1. Create models in `app/models/`
2. Implement business logic in `app/services/`
3. Define routes in `app/routers/`
4. Include router in `app/main.py`

## Notes

- The server uses **SQLAlchemy** for database operations with async support
- **Supabase Auth API** is used for authentication via HTTP requests
- Admin operations (get, update, delete users) require the Supabase service role key
- User passwords are securely handled by Supabase Auth
- The connection string URL is automatically extracted for Supabase Auth API calls
- CORS is currently configured to allow all origins (update for production)

## License

See LICENSE file for details.
