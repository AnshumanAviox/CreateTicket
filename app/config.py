from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API Configuration
    API_BASE_URL: str
    CLIENT_ID: str
    CLIENT_SECRET: str
    USERNAME: str
    PASSWORD: str
    TOKEN_TYPE: str
    SCOPE: str
    GROUP_ID: str

    # Database Configuration
    DB_SERVER: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_PORT: str

    # Optional fields
    msisdn: str | None = None
    database_url: str | None = None

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def api_token_url(self) -> str:
        """Get the complete token URL"""
        return f"{self.API_BASE_URL}/request/token"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings() 