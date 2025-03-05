from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic_settings import BaseSettings


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

    # Redis Configuration
    REDIS_HOST: str = "redis"
    REDIS_PORT: str = "6379"
    REDIS_DB: str = "0"

    class Config:
        env_file = ".env"

    @property
    def DATABASE_URL(self) -> str:
        return f"mssql+pyodbc://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_SERVER}:{self.DB_PORT}/{self.DB_NAME}?driver=ODBC+Driver+17+for+SQL+Server"

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


class TokenRequest(BaseModel):
    token_type: str
    scope: str


class TokenResponse(BaseModel):
    access_token: str


class ProcessTemplateResponse(BaseModel):
    template: Dict[str, Any]


class CreateProcessRequest(BaseModel):
    msisdn: str
    template_id: str
    ticket_id: str


class ProcessRequest(BaseModel):
    template_id: str
    ticket_id: str
    pickup_time: Optional[datetime] = None
    drop_time: Optional[datetime] = None
    trip_start_time: Optional[datetime] = None
    trip_end_time: Optional[datetime] = None
    trip_start_address: Optional[str] = None
    trip_end_address: Optional[str] = None
    trip_start_latitude: Optional[float] = None
    trip_start_longitude: Optional[float] = None
    trip_end_latitude: Optional[float] = None
    trip_end_longitude: Optional[float] = None
    wait_start_time: Optional[datetime] = None
    wait_end_time: Optional[datetime] = None
    wait_start_address: Optional[str] = None
    wait_end_address: Optional[str] = None
    wait_start_latitude: Optional[float] = None
    wait_start_longitude: Optional[float] = None
    wait_end_latitude: Optional[float] = None
    wait_end_longitude: Optional[float] = None