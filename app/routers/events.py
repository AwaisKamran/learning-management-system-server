from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from app.services.event_service import EventService
from app.models.event import EventCreate, EventUpdate, EventResponse
from typing import List

router = APIRouter(prefix="/api/events", tags=["events"])


def get_event_service() -> EventService:
    """Dependency to get event service instance."""
    return EventService()


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    event_service: EventService = Depends(get_event_service)
):
    """Create a new event."""
    return await event_service.create_event(event_data)


@router.get("", response_model=List[EventResponse])
async def get_all_events(
    skip: int = Query(0, ge=0, description="Number of events to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of events to return"),
    upcoming_only: bool = Query(False, description="Filter to show only upcoming events"),
    event_service: EventService = Depends(get_event_service)
):
    """Get all events with optional filtering."""
    return await event_service.get_all_events(
        skip=skip,
        limit=limit,
        upcoming_only=upcoming_only
    )


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    event_service: EventService = Depends(get_event_service)
):
    """Get an event by ID."""
    return await event_service.get_event(event_id)


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    event_data: EventUpdate,
    event_service: EventService = Depends(get_event_service)
):
    """Update an event."""
    return await event_service.update_event(event_id, event_data)


@router.delete("/{event_id}", status_code=status.HTTP_200_OK)
async def delete_event(
    event_id: int,
    event_service: EventService = Depends(get_event_service)
):
    """Delete an event."""
    return await event_service.delete_event(event_id)


@router.post("/upload-photo", status_code=status.HTTP_200_OK)
async def upload_event_photo(
    file: UploadFile = File(..., description="Photo file to upload"),
    bucket_name: str = Query("events", description="Supabase storage bucket name"),
    event_service: EventService = Depends(get_event_service)
):
    """Upload a photo to Supabase Storage and get the public URL."""
    # Use the storage service from event service
    photo_url = await event_service.storage_service.upload_image(
        file=file,
        bucket_name=bucket_name,
        folder="events"
    )
    return {"photo_url": photo_url}

