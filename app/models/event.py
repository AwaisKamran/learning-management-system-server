from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# Pydantic Models (no SQLAlchemy dependency)
class EventCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Event name")
    description: Optional[str] = Field(None, description="Event description")
    date: datetime = Field(..., description="Event date and time")
    photo_url: Optional[str] = Field(None, max_length=500, description="URL to event photo")
    meeting_link: Optional[str] = Field(None, max_length=500, description="Meeting link (Zoom, Google Meet, etc.)")


class EventUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    date: Optional[datetime] = None
    photo_url: Optional[str] = Field(None, max_length=500)
    meeting_link: Optional[str] = Field(None, max_length=500)


class EventResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    date: datetime
    photo_url: Optional[str] = None
    meeting_link: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
