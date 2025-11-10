"""Gateway configuration."""

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Gateway settings."""
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")
    
    # Environment
    ENV: str = Field(default="development")
    PORT: int = Field(default=8081)
    DEBUG: bool = Field(default=False)
    
    # Redis
    REDIS_URL: str = Field(...)
    
    # Database (for usage logging)
    USAGE_DB_URL: str = Field(...)
    
    # AI Providers
    OPENAI_API_KEY: str = Field(...)
    ANTHROPIC_API_KEY: str = Field(...)
    GOOGLE_API_KEY: str = Field(...)
    REPLICATE_API_TOKEN: str = Field(...)
    NANO_BANANA_API_KEY: str = Field(default="")
    NANO_BANANA_BASE_URL: str = Field(default="https://api.nanobanana.ai/v1")
    VEO3_API_KEY: str = Field(default="")
    VEO3_BASE_URL: str = Field(default="https://api.veo3.ai/v1")
    
    # Provider Settings
    PROVIDER_DEFAULT: str = Field(default="openai")
    TOKEN_LIMIT_WARN_PCT: float = Field(default=0.8)
    
    # Rate Limiting
    RATE_LIMIT_WINDOW_SECONDS: int = Field(default=60)
    RATE_LIMIT_MAX_REQUESTS: int = Field(default=60)
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(default="json")


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()
