"""
Configuration management for Smart Garden Planner.
Handles environment variables and application settings.
"""

import os
from typing import Optional
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Digital Ocean LLM API Configuration
    digital_ocean_llm_api_key: str
    digital_ocean_llm_endpoint: str
    
    # Digital Ocean Spaces Configuration (Optional)
    do_spaces_key: Optional[str] = None
    do_spaces_secret: Optional[str] = None
    do_spaces_endpoint: str = "https://nyc3.digitaloceanspaces.com"
    do_spaces_region: str = "nyc3"
    do_spaces_bucket: str = "garden-planner-logs"
    
    # Application Configuration
    environment: str = "development"
    debug: bool = True
    
    # Database Configuration
    database_url: str = "sqlite+aiosqlite:///./garden_planner.db"
    
    # Logging Configuration
    log_level: str = "INFO"
    
    class Config:
        # Only use .env file if it exists (for local development)
        # In production, Terraform will provide environment variables directly
        env_file = ".env" if os.path.exists(".env") else None
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings instance."""
    return settings


def is_development() -> bool:
    """Check if running in development environment."""
    return settings.environment.lower() == "development"


def is_production() -> bool:
    """Check if running in production environment."""
    return settings.environment.lower() == "production"


def spaces_configured() -> bool:
    """Check if Digital Ocean Spaces is configured."""
    return bool(settings.do_spaces_key and settings.do_spaces_secret)


def is_terraform_managed() -> bool:
    """Check if running in a Terraform-managed environment (no .env file)."""
    return not os.path.exists(".env") and is_production()


def get_config_source() -> str:
    """Get the source of configuration (for logging/debugging)."""
    if os.path.exists(".env"):
        return "local .env file"
    elif is_production():
        return "terraform/environment variables"
    else:
        return "environment variables"