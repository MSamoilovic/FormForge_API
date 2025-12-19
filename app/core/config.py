import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field

class Settings(BaseSettings):
    # Database Configuration (individual components for security)
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "db"
    DB_PORT: int = 5432
    DB_NAME: str = "formforge_db"
    
    # API Keys
    GEMINI_API_KEY: str
    
    # Optional: Seed configuration
    RUN_SEED: bool = False
    CLEAR_DATA: bool = False
    
    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        """
        Konstruiše DATABASE_URL iz komponenti.
        Password ostaje sakriven u .env fajlu.
        """
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"  # Ignoriši dodatna polja iz .env
    )

settings = Settings()
