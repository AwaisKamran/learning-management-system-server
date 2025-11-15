from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from app.services.storage_service import StorageService
from typing import Optional

router = APIRouter(prefix="/api/storage", tags=["storage"])


def get_storage_service() -> StorageService:
    """Dependency to get storage service instance."""
    return StorageService()


@router.post("/upload-image", status_code=status.HTTP_200_OK)
async def upload_image(
    file: UploadFile = File(..., description="Image file to upload"),
    bucket_name: str = Query(..., description="Supabase storage bucket name"),
    folder: Optional[str] = Query(None, description="Optional folder path within the bucket"),
    max_size: Optional[int] = Query(None, description="Maximum file size in bytes (default: 10MB)"),
    storage_service: StorageService = Depends(get_storage_service)
):
    """
    Upload an image file to Supabase Storage.
    
    - **file**: Image file (JPEG, PNG, GIF, WebP, SVG)
    - **bucket_name**: Name of the Supabase Storage bucket
    - **folder**: Optional folder path (e.g., "events", "users")
    - **max_size**: Maximum file size in bytes (default: 10MB)
    
    Returns the public URL of the uploaded image.
    """
    try:
        image_url = await storage_service.upload_image(
            file=file,
            bucket_name=bucket_name,
            folder=folder,
            max_size=max_size
        )
        return {
            "success": True,
            "url": image_url,
            "filename": file.filename,
            "content_type": file.content_type,
            "size": file.size if hasattr(file, 'size') else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {str(e)}"
        )


@router.post("/upload-file", status_code=status.HTTP_200_OK)
async def upload_file(
    file: UploadFile = File(..., description="File to upload"),
    bucket_name: str = Query(..., description="Supabase storage bucket name"),
    folder: Optional[str] = Query(None, description="Optional folder path within the bucket"),
    max_size: Optional[int] = Query(None, description="Maximum file size in bytes (default: 10MB)"),
    storage_service: StorageService = Depends(get_storage_service)
):
    """
    Upload any file type to Supabase Storage.
    
    - **file**: File to upload (any type)
    - **bucket_name**: Name of the Supabase Storage bucket
    - **folder**: Optional folder path (e.g., "documents", "videos")
    - **max_size**: Maximum file size in bytes (default: 10MB)
    
    Returns the public URL of the uploaded file.
    """
    try:
        file_url = await storage_service.upload_file(
            file=file,
            bucket_name=bucket_name,
            folder=folder,
            max_size=max_size
        )
        return {
            "success": True,
            "url": file_url,
            "filename": file.filename,
            "content_type": file.content_type,
            "size": file.size if hasattr(file, 'size') else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )


@router.delete("/delete", status_code=status.HTTP_200_OK)
async def delete_file(
    file_url: str = Query(..., description="Public URL of the file to delete"),
    storage_service: StorageService = Depends(get_storage_service)
):
    """
    Delete a file from Supabase Storage.
    
    - **file_url**: Public URL of the file to delete
    
    Returns success status.
    """
    success = await storage_service.delete_file(file_url)
    
    if success:
        return {
            "success": True,
            "message": "File deleted successfully"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete file. File may not exist or URL is invalid."
        )

