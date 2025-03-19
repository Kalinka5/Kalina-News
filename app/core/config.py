import os
import json
from typing import Any, List, Optional, Union
from pydantic import AnyHttpUrl, validator, field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Kalina News"
    
    # Security configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-for-development-only")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week
    
    # CORS configuration
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            # Try to parse as JSON
            try:
                if v.startswith("[") and v.endswith("]"):
                    return json.loads(v)
            except json.JSONDecodeError:
                pass
                
            # Try to parse as comma-separated
            if "," in v:
                return [i.strip() for i in v.split(",") if i.strip()]
            
            # If it's a single URL
            if v.strip():
                return [v.strip()]
                
        # If it's already a list or empty
        if isinstance(v, list):
            return v
            
        # Default fallback
        return ["http://localhost:3000", "http://localhost:5173"]
    
    # Database configuration
    # SQLite configuration (replacing PostgreSQL)
    SQLITE_PATH: str = os.getenv("SQLITE_PATH", "kalina_news.db")
    SQLALCHEMY_DATABASE_URI: Optional[str] = os.getenv("SQLALCHEMY_DATABASE_URI")
    
    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> Any:
        if isinstance(v, str) and v:
            return v
        # Use SQLite instead of PostgreSQL
        sqlite_path = values.get("SQLITE_PATH", "kalina_news.db")
        return f"sqlite:///{sqlite_path}"
    
    # Redis configuration (for caching)
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields

settings = Settings() 