import json
import requests
import pyodbc
from datetime import datetime
from urllib3.exceptions import InsecureRequestWarning
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from .config import settings

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class GeolocationService:
    @staticmethod
    def get_access_token():
        """Get access token from the Team on the Run API."""
        try:
            url = settings.api_token_url
            print(f"Requesting token from: {url}")  # Debug log
            
            payload = {
                "grant_type": "authorization_credentials",
                "token_type": settings.TOKEN_TYPE,
                "client_id": settings.CLIENT_ID,
                "client_secret": settings.CLIENT_SECRET,
                "username": settings.USERNAME,
                "password": settings.PASSWORD,
                "scope": settings.SCOPE
            }
            
            print("Payload:", {k: v for k, v in payload.items() if k != 'password'})  # Debug log
            
            # Add SSL verification options and timeout
            response = requests.post(
                url, 
                json=payload, 
                verify=False,
                timeout=30,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )
            print(f"Response status: {response.status_code}")  # Debug log
            
            if response.status_code == 200:
                token = response.json().get('access_token')
                print("Token obtained successfully")  # Debug log
                return token
            print(f"Failed to get token. Response: {response.text}")  # Debug log
            return None
        except requests.exceptions.SSLError as e:
            print(f"SSL Error during token retrieval: {str(e)}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Request Error during token retrieval: {str(e)}")
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
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # Add SSL verification options and timeout
            response = requests.get(
                url, 
                headers=headers, 
                verify=False,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            print(f"Failed to get locations. Status: {response.status_code}, Response: {response.text}")
            return None
        except requests.exceptions.SSLError as e:
            print(f"SSL Error during geo location retrieval: {str(e)}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Request Error during geo location retrieval: {str(e)}")
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

            # Parse the subscriber data
            subscriber_data = location_data.get('SubscriberData', {})
            if isinstance(subscriber_data, str):
                subscriber_data = json.loads(subscriber_data)

            # Convert string dates to datetime objects
            try:
                subscriber_date = datetime.strptime(location_data['SubscriberDataDate'], '%Y%m%dT%H:%M:%S')
            except (KeyError, ValueError) as e:
                print(f"Warning: Error parsing SubscriberDataDate: {e}")
                subscriber_date = None

            try:
                battery_date = datetime.strptime(subscriber_data.get('BatteryDate', ''), '%Y%m%dT%H:%M:%S') if subscriber_data.get('BatteryDate') else None
            except ValueError as e:
                print(f"Warning: Error parsing BatteryDate: {e}")
                battery_date = None

            try:
                network_date = datetime.strptime(subscriber_data.get('NetworkDate', ''), '%Y%m%dT%H:%M:%S') if subscriber_data.get('NetworkDate') else None
            except ValueError as e:
                print(f"Warning: Error parsing NetworkDate: {e}")
                network_date = None

            try:
                home_network_date = datetime.strptime(subscriber_data.get('HomeNetworkIdentityDate', ''), '%Y%m%dT%H:%M:%S') if subscriber_data.get('HomeNetworkIdentityDate') else None
            except ValueError as e:
                print(f"Warning: Error parsing HomeNetworkIdentityDate: {e}")
                home_network_date = None

            # Define SQL query
            sql = """
            INSERT INTO [dbo].[drivers_gps] (
                [Msisdn], [SubscriberDataStatus], [GeolocationActivated], [GeolocationDeviceStatus],
                [SubscriberDataDate], [GeolocationLatitude], [GeolocationLongitude], [GeolocationAccuracy],
                [GeolocationAddress], [GeolocationSpeed], [BatteryLevel], [BatteryDate],
                [SignalStrength], [NetworkType], [NetworkDate], [MobileCountryCode],
                [MobileNetworkCode], [HomeNetworkIdentityDate], [DeviceType]
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            # Prepare parameters
            params = [
                location_data.get('Msisdn'),
                location_data.get('SubscriberDataStatus'),
                1 if location_data.get('GeolocationActivated') else 0,
                1 if location_data.get('GeolocationDeviceStatus') else 0,
                subscriber_date,
                subscriber_data.get('GeolocationLatitude'),
                subscriber_data.get('GeolocationLongitude'),
                subscriber_data.get('GeolocationAccuracy'),
                subscriber_data.get('GeolocationAddress'),
                subscriber_data.get('GeolocationSpeed'),
                subscriber_data.get('BatteryLevel'),
                battery_date,
                subscriber_data.get('SignalStrength'),
                subscriber_data.get('NetworkType'),
                network_date,
                subscriber_data.get('MobileCountryCode'),
                subscriber_data.get('MobileNetworkCode'),
                home_network_date,
                subscriber_data.get('DeviceType')
            ]

            # Execute query
            cursor.execute(sql, params)
            conn.commit()
            print("✓ Successfully inserted data into drivers_gps table")
            return True
            
        except Exception as e:
            print(f"Database error: {str(e)}")
            raise
        finally:
            cursor.close()
            conn.close() 