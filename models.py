from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class Settings:
    API_BASE_URL = "https://swapi.teamontherun.com"
    CLIENT_ID = "31343_43lzb3vngtmokww8wcws48w4oss044s044o4gkcocks4s0k44c"
    CLIENT_SECRET = "64po82nnwssosgo80wo88osok4so8kc4s8cgowkcsgc80wcoss"
    USERNAME = "bradleycooper888@gmail.com"
    PASSWORD = "Not4afish1234!"
    TOKEN_TYPE = "sw_organization_all_data"
    SCOPE = "processes provisioning"
    MSISDN = "13142014658"

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

class ProcessRequest(BaseModel):
    template_id: str
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