import json
import requests
import pyodbc
from datetime import datetime
from .config import settings

class GeolocationService:
    @staticmethod
    def get_access_token():
        """Get access token from the Team on the Run API."""
        try:
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
            
            response = requests.post(url, json=payload, verify=False)
            
            if response.status_code == 200:
                return response.json().get('access_token')
            return None
        except Exception as e:
            print(f"Token retrieval error: {str(e)}")
            return None

    @staticmethod
    def get_geo_locations(access_token, group_id):
        """Fetch geo location data for a specific group."""
        try:
            url = (f"{settings.API_BASE_URL}/api/v1/organization/group/"
                  f"{group_id}/lastgeolocationdata?Offset=0&Records=500")
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Geo location retrieval error: {str(e)}")
            return None

    @staticmethod
    def insert_location_data(location_data):
        """Insert geolocation data into the drivers_gps table."""
        try:
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={settings.DB_SERVER},{settings.DB_PORT};"
                f"DATABASE={settings.DB_NAME};"
                f"UID={settings.DB_USER};PWD={settings.DB_PASSWORD}"
            )
            
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()

            # Rest of your insert_location_data logic...
            # (keeping the same logic as in your original code)
            
            cursor.execute(sql, params)
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Database error: {str(e)}")
            raise
        finally:
            cursor.close()
            conn.close() 