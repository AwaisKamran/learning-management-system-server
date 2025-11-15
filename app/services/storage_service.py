from typing import Optional, List
from fastapi import HTTPException, status, UploadFile
import httpx
from app.config import settings
import uuid
from pathlib import Path
import mimetypes


class StorageService:
    """Service for handling file uploads to Supabase Storage."""
    
    # Allowed image MIME types
    ALLOWED_IMAGE_TYPES = {
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/gif",
        "image/webp",
        "image/svg+xml"
    }
    
    # Maximum file size in bytes (10MB default)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    def __init__(self):
        self.supabase_url = settings.supabase_url
        self.supabase_key = settings.supabase_key
        self.service_role_key = settings.supabase_service_role_key
    
    async def upload_image(
        self,
        file: UploadFile,
        bucket_name: str,
        folder: Optional[str] = None,
        max_size: Optional[int] = None,
        allowed_types: Optional[set] = None
    ) -> str:
        """
        Upload an image file to Supabase Storage.
        
        Args:
            file: The file to upload
            bucket_name: Name of the Supabase Storage bucket
            folder: Optional folder path within the bucket (e.g., "events", "users")
            max_size: Maximum file size in bytes (default: 10MB)
            allowed_types: Set of allowed MIME types (default: common image types)
        
        Returns:
            Public URL of the uploaded file
        
        Raises:
            HTTPException: If upload fails or validation fails
        """
        # Validate configuration - use service role key for uploads to bypass RLS
        if not self.supabase_url or not self.service_role_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Supabase configuration is missing. Service role key is required for file uploads."
            )
        
        # Set defaults
        max_size = max_size or self.MAX_FILE_SIZE
        allowed_types = allowed_types or self.ALLOWED_IMAGE_TYPES
        
        # Validate file type
        if not file.content_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File content type is required"
            )
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type '{file.content_type}' is not allowed. Allowed types: {', '.join(allowed_types)}"
            )
        
        try:
            # Read file content
            file_content = await file.read()
            
            # Validate file size
            file_size = len(file_content)
            if file_size > max_size:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File size ({file_size / 1024 / 1024:.2f}MB) exceeds maximum allowed size ({max_size / 1024 / 1024:.2f}MB)"
                )
            
            # Generate unique filename
            file_extension = self._get_file_extension(file.filename, file.content_type)
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Build file path
            if folder:
                file_path = f"{folder}/{unique_filename}"
            else:
                file_path = unique_filename
            
            # Upload to Supabase Storage using service role key to bypass RLS
            async with httpx.AsyncClient(timeout=30.0) as client:
                upload_response = await client.post(
                    f"{self.supabase_url}/storage/v1/object/{bucket_name}/{file_path}",
                    headers={
                        "apikey": self.service_role_key,
                        "Authorization": f"Bearer {self.service_role_key}",
                        "Content-Type": file.content_type,
                    },
                    content=file_content,
                )
                
                if upload_response.status_code not in [200, 201]:
                    error_data = upload_response.json() if upload_response.content else {}
                    error_msg = error_data.get("message", "Failed to upload file")
                    raise HTTPException(
                        status_code=upload_response.status_code,
                        detail=f"Error uploading file: {error_msg}"
                    )
                
                # Return public URL
                public_url = f"{self.supabase_url}/storage/v1/object/public/{bucket_name}/{file_path}"
                return public_url
                
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error uploading file: {str(e)}"
            )
    
    async def upload_file(
        self,
        file: UploadFile,
        bucket_name: str,
        folder: Optional[str] = None,
        max_size: Optional[int] = None
    ) -> str:
        """
        Upload any file type to Supabase Storage.
        
        Args:
            file: The file to upload
            bucket_name: Name of the Supabase Storage bucket
            folder: Optional folder path within the bucket
            max_size: Maximum file size in bytes (default: 10MB)
        
        Returns:
            Public URL of the uploaded file
        """
        max_size = max_size or self.MAX_FILE_SIZE
        
        if not self.supabase_url or not self.service_role_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Supabase configuration is missing. Service role key is required for file uploads."
            )
        
        try:
            # Read file content
            file_content = await file.read()
            
            # Validate file size
            file_size = len(file_content)
            if file_size > max_size:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File size ({file_size / 1024 / 1024:.2f}MB) exceeds maximum allowed size ({max_size / 1024 / 1024:.2f}MB)"
                )
            
            # Generate unique filename
            file_extension = self._get_file_extension(file.filename, file.content_type)
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Build file path
            if folder:
                file_path = f"{folder}/{unique_filename}"
            else:
                file_path = unique_filename
            
            # Upload to Supabase Storage using service role key to bypass RLS
            async with httpx.AsyncClient(timeout=30.0) as client:
                upload_response = await client.post(
                    f"{self.supabase_url}/storage/v1/object/{bucket_name}/{file_path}",
                    headers={
                        "apikey": self.service_role_key,
                        "Authorization": f"Bearer {self.service_role_key}",
                        "Content-Type": file.content_type or "application/octet-stream",
                    },
                    content=file_content,
                )
                
                if upload_response.status_code not in [200, 201]:
                    error_data = upload_response.json() if upload_response.content else {}
                    error_msg = error_data.get("message", "Failed to upload file")
                    raise HTTPException(
                        status_code=upload_response.status_code,
                        detail=f"Error uploading file: {error_msg}"
                    )
                
                # Return public URL
                public_url = f"{self.supabase_url}/storage/v1/object/public/{bucket_name}/{file_path}"
                return public_url
                
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error uploading file: {str(e)}"
            )
    
    async def delete_file(self, file_url: str) -> bool:
        """
        Delete a file from Supabase Storage.
        
        Args:
            file_url: The public URL of the file to delete
        
        Returns:
            True if deletion was successful, False otherwise
        """
        if not self.supabase_url or not self.service_role_key:
            return False
        
        try:
            # Extract bucket and file path from URL
            # URL format: https://xxx.supabase.co/storage/v1/object/public/bucket/path/to/file
            if "/storage/v1/object/public/" not in file_url:
                return False
            
            path_part = file_url.split("/storage/v1/object/public/")[1]
            parts = path_part.split("/", 1)
            
            if len(parts) != 2:
                return False
            
            bucket_name, file_path = parts
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                delete_response = await client.delete(
                    f"{self.supabase_url}/storage/v1/object/{bucket_name}/{file_path}",
                    headers={
                        "apikey": self.service_role_key,
                        "Authorization": f"Bearer {self.service_role_key}",
                    },
                )
                
                return delete_response.status_code in [200, 204]
                
        except Exception:
            return False
    
    async def delete_files(self, file_urls: List[str]) -> dict:
        """
        Delete multiple files from Supabase Storage.
        
        Args:
            file_urls: List of public URLs of files to delete
        
        Returns:
            Dictionary with success count and failed URLs
        """
        results = {"success": 0, "failed": []}
        
        for url in file_urls:
            success = await self.delete_file(url)
            if success:
                results["success"] += 1
            else:
                results["failed"].append(url)
        
        return results
    
    def _get_file_extension(self, filename: Optional[str], content_type: Optional[str]) -> str:
        """Get file extension from filename or content type."""
        # Try to get extension from filename
        if filename:
            path = Path(filename)
            if path.suffix:
                return path.suffix
        
        # Fall back to content type
        if content_type:
            extension = mimetypes.guess_extension(content_type)
            if extension:
                return extension
        
        # Default to .bin if we can't determine
        return ".bin"
    
    def validate_image_type(self, content_type: Optional[str]) -> bool:
        """Check if content type is an allowed image type."""
        if not content_type:
            return False
        return content_type in self.ALLOWED_IMAGE_TYPES
    
    def validate_file_size(self, file_size: int, max_size: Optional[int] = None) -> bool:
        """Check if file size is within allowed limit."""
        max_size = max_size or self.MAX_FILE_SIZE
        return file_size <= max_size

