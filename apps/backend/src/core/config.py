"""
Application configuration using Pydantic Settings.
Supports AWS Secrets Manager references (aws:secretsmanager:KEY_NAME).
"""

import boto3
import json
from functools import lru_cache
from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")
    
    # Environment
    ENV: str = Field(default="development")
    PORT: int = Field(default=8080)
    DEBUG: bool = Field(default=False)
    
    # Database
    DATABASE_URL: str = Field(...)
    DB_POOL_SIZE: int = Field(default=10)
    DB_MAX_OVERFLOW: int = Field(default=20)
    
    # Redis
    REDIS_URL: str = Field(...)
    REDIS_MAX_CONNECTIONS: int = Field(default=50)
    
    # JWT
    JWT_SECRET: str = Field(...)
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_EXPIRE_MINUTES: int = Field(default=43200)  # 30 days
    
    # AWS
    AWS_REGION: str = Field(default="eu-central-1")
    S3_ASSETS_BUCKET: str = Field(...)
    S3_QUAR_BUCKET: str = Field(...)
    
    # Email (SES)
    SES_REGION: str = Field(default="eu-central-1")
    EMAIL_FROM: str = Field(...)
    
    # Payments
    PAYMENTS_PROVIDER: str = Field(default="hyperpay")
    HYPERPAY_API_KEY: str = Field(...)
    HYPERPAY_ENTITY_ID: str = Field(...)
    HYPERPAY_TEST_MODE: bool = Field(default=True)
    HYPERPAY_BASE_URL: str = Field(default="https://test.oppwa.com")
    
    # Application URLs
    BASE_URL: str = Field(default="http://localhost:3000")
    API_BASE_URL: str = Field(default="http://localhost:8080")
    FRONTEND_URL: str = Field(default="http://localhost:3000")
    
    # CORS
    CORS_ORIGINS: str = Field(default="http://localhost:3000")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(default="json")
    
    def get_cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    def resolve_secret(self, value: str) -> str:
        """
        Resolve AWS Secrets Manager references.
        If value starts with 'aws:secretsmanager:', fetch from Secrets Manager.
        """
        if not value.startswith("aws:secretsmanager:"):
            return value
        
        secret_name = value.replace("aws:secretsmanager:", "")
        
        try:
            client = boto3.client("secretsmanager", region_name=self.AWS_REGION)
            response = client.get_secret_value(SecretId=secret_name)
            
            if "SecretString" in response:
                return response["SecretString"]
            else:
                # Binary secret (unlikely for config)
                return response["SecretBinary"].decode("utf-8")
        except Exception as e:
            raise ValueError(f"Failed to resolve secret {secret_name}: {str(e)}")
    
    def model_post_init(self, __context):
        """Post-init hook to resolve Secrets Manager references."""
        # Resolve secrets for sensitive fields
        sensitive_fields = [
            "DATABASE_URL",
            "REDIS_URL",
            "JWT_SECRET",
            "EMAIL_FROM",
            "HYPERPAY_API_KEY",
            "HYPERPAY_ENTITY_ID",
        ]
        
        for field in sensitive_fields:
            value = getattr(self, field, None)
            if value and isinstance(value, str) and value.startswith("aws:secretsmanager:"):
                setattr(self, field, self.resolve_secret(value))


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings instance.
    Use this function to get settings throughout the app.
    """
    return Settings()
