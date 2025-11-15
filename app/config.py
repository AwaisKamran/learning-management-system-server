from pydantic_settings import BaseSettings
from typing import Optional
import re
from urllib.parse import urlparse


class Settings(BaseSettings):
    # Database connection string
    database_url: str
    
    # Supabase Auth API credentials (for authentication)
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    supabase_service_role_key: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Extract Supabase URL from connection string if not provided
        if not self.supabase_url and self.database_url:
            self.supabase_url = self._extract_supabase_url_from_connection_string(
                self.database_url
            )
    
    @staticmethod
    def _extract_supabase_url_from_connection_string(connection_string: str) -> str:
        """Extract Supabase project URL from PostgreSQL connection string."""
        try:
            parsed = urlparse(connection_string)
            host = parsed.hostname
            
            if not host:
                raise ValueError("Could not extract host from connection string")
            
            # Handle different Supabase connection string formats
            if 'supabase.co' in host or 'supabase.com' in host:
                # Format 1: db.xxxxx.supabase.co
                match = re.search(r'db\.([^.]+)\.supabase\.co', host)
                if match:
                    return f"https://{match.group(1)}.supabase.co"
                
                # Format 2: postgres.xxxxx.pooler.supabase.com
                match = re.search(r'postgres\.([^.]+)\.pooler\.supabase\.com', host)
                if match:
                    return f"https://{match.group(1)}.supabase.co"
                
                # Format 3: xxxxx.pooler.supabase.com
                match = re.search(r'([^.]+)\.pooler\.supabase\.com', host)
                if match:
                    return f"https://{match.group(1)}.supabase.co"
                
                # Format 4: Try to extract any subdomain before supabase.co/com
                match = re.search(r'([^.]+)\.supabase\.(co|com)', host)
                if match:
                    project_ref = match.group(1)
                    if project_ref not in ['db', 'postgres', 'pooler']:
                        return f"https://{project_ref}.supabase.co"
            
            raise ValueError(
                f"Could not extract Supabase URL from connection string. "
                f"Please provide SUPABASE_URL in .env file."
            )
        except Exception as e:
            raise ValueError(f"Error parsing connection string: {str(e)}")


settings = Settings()

