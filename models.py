from pydantic import BaseModel
from pydantic_settings import BaseSettings
from typing import Dict, Any, Optional
from datetime import datetime


class Settings(BaseSettings):
    API_BASE_URL: str = "https://swapi.teamontherun.com"
    TOKEN_TYPE: str = "sw_organization_all_data"
    CLIENT_ID: str = "31343_43lzb3vngtmokww8wcws48w4oss044s044o4gkcocks4s0k44c"
    CLIENT_SECRET: str = "64po82nnwssosgo80wo88osok4so8kc4s8cgowkcsgc80wcoss"
    USERNAME: str = "bradleycooper888@gmail.com"
    PASSWORD: str = "Not4afish1234!"
    SCOPE: str = "processes provisioning"
    MSISDN: str = "13142014658"
    DATABASE_URL: str = "mssql+pyodbc://chiliadmin:h77pc0l0@172.31.6.34:1433/CHILI_PROD?driver=ODBC+Driver+17+for+SQL+Server"

    class Config:
        env_file = ".env"


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