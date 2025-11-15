from fastapi import APIRouter, Depends
from app.services.user_service import UserService
from app.models.user import UserCreate, UserUpdate, UserResponse, UserLogin, TokenResponse
from fastapi import status

router = APIRouter(prefix="/api/users", tags=["users"])


def get_user_service() -> UserService:
    """Dependency to get user service instance."""
    return UserService()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    """Register a new user."""
    return await user_service.create_user(user_data)


@router.post("/login", response_model=TokenResponse)
async def login_user(
    login_data: UserLogin,
    user_service: UserService = Depends(get_user_service)
):
    """Authenticate user and return access token."""
    result = await user_service.authenticate_user(login_data)
    return TokenResponse(**result)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    """Get user by ID (admin operation)."""
    return await user_service.get_user(user_id)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    user_service: UserService = Depends(get_user_service)
):
    """Update user information (admin operation)."""
    return await user_service.update_user(user_id, user_data)


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    """Delete a user (admin operation)."""
    return await user_service.delete_user(user_id)

