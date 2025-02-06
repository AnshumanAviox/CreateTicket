# auth.py
from fastapi import HTTPException
import requests
from models import Settings
from datetime import datetime, timedelta

settings = Settings()

class TokenManager:
    def __init__(self):
        self.cached_token = None
        self.token_expiry = None

token_manager = TokenManager()

async def get_access_token():
    """Get access token using OAuth 2.0 with caching"""
    # Check if we have a valid cached token
    if (token_manager.cached_token and token_manager.token_expiry 
        and datetime.now() < token_manager.token_expiry):
        print("Using cached token")
        return token_manager.cached_token
        
    print("Getting new token...")
    url = f"{settings.API_BASE_URL}/request/token"
    payload = {
        "grant_type": "authorization_credentials",
        "token_type": settings.TOKEN_TYPE,
        "client_id": settings.CLIENT_ID,
        "client_secret": settings.CLIENT_SECRET,
        "username": settings.USERNAME,
        "password": settings.PASSWORD,
        "scope": settings.SCOPE
    }
    
    try:
        response = requests.post(url, json=payload, verify=False)
        if response.status_code == 200:
            token_manager.cached_token = response.json()["access_token"]
            # Set token expiry to 1 hour
            token_manager.token_expiry = datetime.now() + timedelta(hours=1)
            print(f"New token generated, expires at: {token_manager.token_expiry}")
            return token_manager.cached_token
            
        raise HTTPException(
            status_code=401,
            detail=f"Failed to get access token: {response.text}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting access token: {str(e)}"
        )

def clear_token_cache():
    """Clear the token cache"""
    token_manager.cached_token = None
    token_manager.token_expiry = None