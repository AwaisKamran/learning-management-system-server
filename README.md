# Learning Management System Server

This repository contains a FastAPI-based server for a Learning Management System. The server uses Supabase REST API (PostgREST) for database operations and Supabase Auth API for user authentication.

## Features

- **User Management**: Complete CRUD operations for users
- **Authentication**: User registration and login with JWT tokens via Supabase Auth
- **Supabase REST API**: All database operations via HTTP requests (PostgREST)
- **Supabase Auth API**: Direct HTTP integration with Supabase authentication
- **Event Management**: Create, update, delete, and manage weekly events with photos
- **File Storage**: Image upload service using Supabase Storage

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── models/              # Pydantic models
│   │   ├── __init__.py
│   │   ├── user.py          # User models
│   │   └── event.py         # Event models
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── user_service.py  # User service
│   │   ├── event_service.py  # Event service
│   │   └── storage_service.py  # Storage service
│   └── routers/             # API routes
│       ├── __init__.py
│       ├── users.py         # User endpoints
│       ├── events.py        # Event endpoints
│       └── storage.py       # Storage endpoints
├── migrations/              # Database migration scripts
│   └── create_events_table.sql
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

4. **Set up the database**:
   
   Run the migration script to create the events table:
   ```bash
   # Using psql (replace with your connection string)
   psql "your_connection_string" -f migrations/create_events_table.sql
   
   # Or using Supabase SQL Editor:
   # Copy the contents of migrations/create_events_table.sql and run it in Supabase Dashboard > SQL Editor
   ```

5. **Set up Supabase Storage** (for event photos):
   
   - Go to Supabase Dashboard > Storage
   - Create a new bucket named `events` (or use a different name)
   - Set the bucket to **Public** if you want public access to photos
   - Or configure RLS (Row Level Security) policies as needed

6. **Set up environment variables**:
   
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

### Event Management

#### Create an event
```http
POST /api/events
Content-Type: application/json

{
  "name": "Weekly Coding Event",
  "description": "Learn Python basics",
  "date": "2024-01-15T10:00:00",
  "photo_url": "https://xxx.supabase.co/storage/v1/object/public/events/photo.jpg",
  "meeting_link": "https://zoom.us/j/123456789"
}
```

#### Get all events
```http
GET /api/events?skip=0&limit=100&upcoming_only=false
```

Query parameters:
- `skip`: Number of events to skip (default: 0)
- `limit`: Maximum number of events to return (default: 100, max: 1000)
- `upcoming_only`: Filter to show only upcoming events (default: false)

#### Get event by ID
```http
GET /api/events/{event_id}
```

#### Update an event
```http
PUT /api/events/{event_id}
Content-Type: application/json

{
  "name": "Updated Event Name",
  "description": "Updated description",
  "date": "2024-01-20T14:00:00",
  "meeting_link": "https://meet.google.com/abc-defg-hij"
}
```

#### Delete an event
```http
DELETE /api/events/{event_id}
```

#### Upload event photo
```http
POST /api/events/upload-photo
Content-Type: multipart/form-data

file: [image file]
bucket_name: events (optional, default: "events")
```

Returns:
```json
{
  "photo_url": "https://xxx.supabase.co/storage/v1/object/public/events/uuid.jpg"
}
```

## Development

### Code Structure

- **Models** (`app/models/`): Pydantic models for request/response validation
- **Services** (`app/services/`): Business logic using Supabase REST API and Auth API
- **Routers** (`app/routers/`): API endpoint definitions
- **Config** (`app/config.py`): Environment-based configuration with connection string parsing

### Adding New Features

1. Create models in `app/models/`
2. Implement business logic in `app/services/`
3. Define routes in `app/routers/`
4. Include router in `app/main.py`

## Notes

- The server uses **Supabase REST API (PostgREST)** for all database operations via HTTP requests
- **Supabase Auth API** is used for authentication via HTTP requests
- **Supabase Storage** is used for file uploads (images, documents, etc.)
- All operations use **httpx** for consistent HTTP-based architecture
- Admin operations (get, update, delete users) require the Supabase service role key
- User passwords are securely handled by Supabase Auth
- The connection string URL is automatically extracted for Supabase Auth API calls
- Event photos are uploaded to Supabase Storage and public URLs are stored in the database
- CORS is currently configured to allow all origins (update for production)

## License

See LICENSE file for details.
