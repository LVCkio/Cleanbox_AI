"""
CleanInbox AI — Settings (Pydantic BaseSettings)
Đọc config từ .env file, validate kiểu dữ liệu tự động.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./cleaninbox_dev.db"

    # Security
    SECRET_KEY: str = "change-this-to-random-secret-key-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Third-party APIs
    MAILCHIMP_API_KEY: str = ""
    MAILCHIMP_SERVER_PREFIX: str = "us21"
    HUBSPOT_ACCESS_TOKEN: str = ""
    SENDGRID_API_KEY: str = ""

    # ESG Constants
    CO2_PER_EMAIL_GRAMS: float = 0.3
    COST_PER_EMAIL_USD: float = 0.02
    CO2_TARGET_KG: float = 1500.0

    # App
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: str = "http://localhost:3999,http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

settings = Settings()
