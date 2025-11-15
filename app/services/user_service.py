from typing import Optional
import httpx
import json
from app.models.user import UserCreate, UserUpdate, UserResponse, UserLogin
from app.config import settings
from fastapi import HTTPException, status
from datetime import datetime


class UserService:
    def __init__(self):
        self.supabase_url = settings.supabase_url
        self.supabase_key = settings.supabase_key
        self.service_role_key = settings.supabase_service_role_key

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user in Supabase Auth."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.supabase_url}/auth/v1/signup",
                    headers={
                        "apikey": self.supabase_key,
                        "Content-Type": "application/json",
                    },
                    json={
                        "email": user_data.email,
                        "password": user_data.password,
                        "data": {
                            "full_name": user_data.full_name,
                            "phone": user_data.phone
                        }
                    },
                )

                if response.status_code != 200:
                    error_data = response.json() if response.content else {}
                    error_msg = error_data.get("msg", "Failed to create user")
                    
                    if "already registered" in error_msg.lower() or "already exists" in error_msg.lower():
                        raise HTTPException(
                            status_code=status.HTTP_409_CONFLICT,
                            detail="User with this email already exists"
                        )
                    
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=error_msg
                    )

                data = response.json()
                print(json.dumps(data, indent=4))
                
                if not data:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to create user"
                    )

                user = data.get("user_metadata", {})
                
                return UserResponse(
                    id=user.get("sub"),
                    email=user.get("email"),
                    full_name=user.get("full_name") or data.full_name,
                    phone=user.get("phone") or data.phone,
                    created_at=datetime.fromisoformat(user.get("created_at").replace('Z', '+00:00')) if user.get("created_at") else None
                )
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Error creating user: {str(e)}"
                )

    async def authenticate_user(self, login_data: UserLogin) -> dict:
        """Authenticate user and return access token."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.supabase_url}/auth/v1/token?grant_type=password",
                    headers={
                        "apikey": self.supabase_key,
                        "Content-Type": "application/json",
                    },
                    json={
                        "email": login_data.email,
                        "password": login_data.password
                    },
                )

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid email or password"
                    )

                data = response.json()
                user = data.get("user", {})
                access_token = data.get("access_token")
                
                if not user or not access_token:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid email or password"
                    )

                user_metadata = user.get("user_metadata", {})
                
                return {
                    "access_token": access_token,
                    "token_type": "bearer",
                    "user": UserResponse(
                        id=user.get("id"),
                        email=user.get("email"),
                        full_name=user_metadata.get("full_name"),
                        phone=user_metadata.get("phone"),
                        created_at=datetime.fromisoformat(user.get("created_at").replace('Z', '+00:00')) if user.get("created_at") else None
                    )
                }
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )

    async def get_user(self, user_id: str) -> UserResponse:
        """Get user by ID (admin operation)."""
        if not self.service_role_key:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Service role key is required for this operation"
            )

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.supabase_url}/auth/v1/admin/users/{user_id}",
                    headers={
                        "apikey": self.service_role_key,
                        "Authorization": f"Bearer {self.service_role_key}",
                    },
                )

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User not found"
                    )

                user = response.json()
                user_metadata = user.get("user_metadata", {})
                
                return UserResponse(
                    id=user.get("id"),
                    email=user.get("email"),
                    full_name=user_metadata.get("full_name"),
                    phone=user_metadata.get("phone"),
                    created_at=datetime.fromisoformat(user.get("created_at").replace('Z', '+00:00')) if user.get("created_at") else None
                )
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

    async def update_user(self, user_id: str, user_data: UserUpdate) -> UserResponse:
        """Update user information (admin operation)."""
        if not self.service_role_key:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Service role key is required for this operation"
            )

        async with httpx.AsyncClient() as client:
            try:
                update_payload = {}
                
                if user_data.email:
                    update_payload["email"] = user_data.email
                
                if user_data.password:
                    update_payload["password"] = user_data.password
                
                # Update user metadata
                metadata = {}
                if user_data.full_name is not None:
                    metadata["full_name"] = user_data.full_name
                if user_data.phone is not None:
                    metadata["phone"] = user_data.phone
                
                if metadata:
                    update_payload["user_metadata"] = metadata

                response = await client.put(
                    f"{self.supabase_url}/auth/v1/admin/users/{user_id}",
                    headers={
                        "apikey": self.service_role_key,
                        "Authorization": f"Bearer {self.service_role_key}",
                        "Content-Type": "application/json",
                    },
                    json=update_payload,
                )

                if response.status_code != 200:
                    error_data = response.json() if response.content else {}
                    error_msg = error_data.get("msg", "Failed to update user")
                    
                    if "not found" in error_msg.lower():
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found"
                        )
                    
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=error_msg
                    )

                user = response.json()
                user_metadata = user.get("user_metadata", {})
                
                return UserResponse(
                    id=user.get("id"),
                    email=user.get("email"),
                    full_name=user_metadata.get("full_name"),
                    phone=user_metadata.get("phone"),
                    created_at=datetime.fromisoformat(user.get("created_at").replace('Z', '+00:00')) if user.get("created_at") else None
                )
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Error updating user: {str(e)}"
                )

    async def delete_user(self, user_id: str) -> dict:
        """Delete a user (admin operation)."""
        if not self.service_role_key:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Service role key is required for this operation"
            )

        async with httpx.AsyncClient() as client:
            try:
                response = await client.delete(
                    f"{self.supabase_url}/auth/v1/admin/users/{user_id}",
                    headers={
                        "apikey": self.service_role_key,
                        "Authorization": f"Bearer {self.service_role_key}",
                    },
                )

                if response.status_code not in [200, 204]:
                    error_data = response.json() if response.content else {}
                    error_msg = error_data.get("msg", "Failed to delete user")
                    
                    if "not found" in error_msg.lower():
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found"
                        )
                    
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=error_msg
                    )

                return {"message": "User deleted successfully", "user_id": user_id}
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Error deleting user: {str(e)}"
                )
