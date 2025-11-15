from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users

app = FastAPI(
    title="Learning Management System API",
    description="API server for Learning Management System",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Learning Management System API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

