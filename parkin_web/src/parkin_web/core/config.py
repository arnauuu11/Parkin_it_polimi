# src/parkin_web/core/config.py
import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, HttpUrl, PostgresDsn, validator


class Settings(BaseSettings):
    PROJECT_NAME: str = "Parkin-it"
    PROJECT_DESCRIPTION: str = "A secure parking rental platform connecting drivers with parking space owners"
    PROJECT_VERSION: str = "0.1.0"
    
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "parkin_it"
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None

    # Admin user
    FIRST_SUPERUSER: EmailStr = "admin@parkin-it.com"
    FIRST_SUPERUSER_PASSWORD: str = "admin"
    USERS_OPEN_REGISTRATION: bool = True

    # Security
    SECURITY_CAMERA_API_KEY: Optional[str] = None
    SECURITY_CAMERA_API_URL: Optional[HttpUrl] = None
    
    # Insurance
    INSURANCE_API_KEY: Optional[str] = None
    INSURANCE_API_URL: Optional[HttpUrl] = None
    
    # EV Charging
    EV_CHARGING_API_KEY: Optional[str] = None
    EV_CHARGING_API_URL: Optional[HttpUrl] = None
    
    # Payment
    STRIPE_API_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()