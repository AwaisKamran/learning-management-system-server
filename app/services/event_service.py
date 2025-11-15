from typing import List, Optional
import httpx
from app.models.event import EventCreate, EventUpdate, EventResponse
from app.services.storage_service import StorageService
from app.config import settings
from fastapi import HTTPException, status
from datetime import datetime


class EventService:
    def __init__(self):
        self.supabase_url = settings.supabase_url
        self.supabase_key = settings.supabase_key
        self.service_role_key = settings.supabase_service_role_key
        self.storage_service = StorageService()

    async def create_event(self, event_data: EventCreate) -> EventResponse:
        """Create a new event."""
        if not self.supabase_url or not self.supabase_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Supabase configuration is missing"
            )

        async with httpx.AsyncClient() as client:
            try:
                # Prepare data for Supabase
                event_payload = {
                    "name": event_data.name,
                    "description": event_data.description,
                    "date": event_data.date.isoformat(),
                    "photo_url": event_data.photo_url,
                    "meeting_link": event_data.meeting_link,
                }

                response = await client.post(
                    f"{self.supabase_url}/rest/v1/events",
                    headers={
                        "apikey": self.supabase_key,
                        "Authorization": f"Bearer {self.supabase_key}",
                        "Content-Type": "application/json",
                        "Prefer": "return=representation",  # Return the created record
                    },
                    json=event_payload,
                )

                if response.status_code not in [200, 201]:
                    error_data = response.json() if response.content else {}
                    error_msg = error_data.get("message", "Failed to create event")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Error creating event: {error_msg}"
                    )

                data = response.json()
                # PostgREST returns an array, get first item
                event = data[0] if isinstance(data, list) else data
                return EventResponse(**event)

            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Error creating event: {str(e)}"
                )

    async def get_event(self, event_id: int) -> EventResponse:
        """Get an event by ID."""
        if not self.supabase_url or not self.supabase_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Supabase configuration is missing"
            )

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.supabase_url}/rest/v1/events",
                    headers={
                        "apikey": self.supabase_key,
                        "Authorization": f"Bearer {self.supabase_key}",
                    },
                    params={
                        "id": f"eq.{event_id}",
                        "select": "*",
                    },
                )

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail="Failed to fetch event"
                    )

                data = response.json()
                if not data or len(data) == 0:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Event not found"
                    )

                return EventResponse(**data[0])

            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Event not found"
                )

    async def get_all_events(
        self,
        skip: int = 0,
        limit: int = 100,
        upcoming_only: bool = False
    ) -> List[EventResponse]:
        """Get all events with optional filtering."""
        if not self.supabase_url or not self.supabase_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Supabase configuration is missing"
            )

        async with httpx.AsyncClient() as client:
            try:
                params = {
                    "select": "*",
                    "order": "date.asc",
                    "limit": limit,
                    "offset": skip,
                }

                # Filter for upcoming events only
                if upcoming_only:
                    now = datetime.now().isoformat()
                    params["date"] = f"gte.{now}"

                response = await client.get(
                    f"{self.supabase_url}/rest/v1/events",
                    headers={
                        "apikey": self.supabase_key,
                        "Authorization": f"Bearer {self.supabase_key}",
                    },
                    params=params,
                )

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail="Failed to fetch events"
                    )

                data = response.json()
                return [EventResponse(**event) for event in data]

            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Error fetching events: {str(e)}"
                )

    async def update_event(
        self,
        event_id: int,
        event_data: EventUpdate
    ) -> EventResponse:
        """Update an event."""
        if not self.supabase_url or not self.supabase_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Supabase configuration is missing"
            )

        async with httpx.AsyncClient() as client:
            try:
                # Check if event exists first
                check_response = await client.get(
                    f"{self.supabase_url}/rest/v1/events",
                    headers={
                        "apikey": self.supabase_key,
                        "Authorization": f"Bearer {self.supabase_key}",
                    },
                    params={
                        "id": f"eq.{event_id}",
                        "select": "id",
                    },
                )

                if check_response.status_code != 200 or not check_response.json():
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Event not found"
                    )

                # Prepare update payload (only include provided fields)
                update_payload = {}
                if event_data.name is not None:
                    update_payload["name"] = event_data.name
                if event_data.description is not None:
                    update_payload["description"] = event_data.description
                if event_data.date is not None:
                    update_payload["date"] = event_data.date.isoformat()
                if event_data.photo_url is not None:
                    update_payload["photo_url"] = event_data.photo_url
                if event_data.meeting_link is not None:
                    update_payload["meeting_link"] = event_data.meeting_link

                if not update_payload:
                    # No fields to update, return existing event
                    return await self.get_event(event_id)

                # Update event
                response = await client.patch(
                    f"{self.supabase_url}/rest/v1/events",
                    headers={
                        "apikey": self.supabase_key,
                        "Authorization": f"Bearer {self.supabase_key}",
                        "Content-Type": "application/json",
                        "Prefer": "return=representation",
                    },
                    params={
                        "id": f"eq.{event_id}",
                    },
                    json=update_payload,
                )

                if response.status_code != 200:
                    error_data = response.json() if response.content else {}
                    error_msg = error_data.get("message", "Failed to update event")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Error updating event: {error_msg}"
                    )

                data = response.json()
                event = data[0] if isinstance(data, list) else data
                return EventResponse(**event)

            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Error updating event: {str(e)}"
                )

    async def delete_event(self, event_id: int) -> dict:
        """Delete an event."""
        if not self.supabase_url or not self.supabase_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Supabase configuration is missing"
            )

        async with httpx.AsyncClient() as client:
            try:
                # Get event first to check if it exists and get photo_url
                get_response = await client.get(
                    f"{self.supabase_url}/rest/v1/events",
                    headers={
                        "apikey": self.supabase_key,
                        "Authorization": f"Bearer {self.supabase_key}",
                    },
                    params={
                        "id": f"eq.{event_id}",
                        "select": "photo_url",
                    },
                )

                if get_response.status_code != 200 or not get_response.json():
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Event not found"
                    )

                event_data = get_response.json()[0]
                photo_url = event_data.get("photo_url")

                # Delete photo from storage if it exists
                if photo_url:
                    await self.storage_service.delete_file(photo_url)

                # Delete event
                response = await client.delete(
                    f"{self.supabase_url}/rest/v1/events",
                    headers={
                        "apikey": self.supabase_key,
                        "Authorization": f"Bearer {self.supabase_key}",
                    },
                    params={
                        "id": f"eq.{event_id}",
                    },
                )

                if response.status_code not in [200, 204]:
                    error_data = response.json() if response.content else {}
                    error_msg = error_data.get("message", "Failed to delete event")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Error deleting event: {error_msg}"
                    )

                return {"message": "Event deleted successfully", "event_id": event_id}

            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Error deleting event: {str(e)}"
                )
