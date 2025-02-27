from celery import Celery
from datetime import datetime
import requests
import json
import pyodbc
import urllib3
from celery.utils.log import get_task_logger

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Initialize Celery
celery_app = Celery('gps_tasks')
celery_app.config_from_object('celeryconfig')

# Setup logger
logger = get_task_logger(__name__)

# API Configuration
API_BASE_URL = "https://swapi.teamontherun.com"
CLIENT_ID = "31343_43lzb3vngtmokww8wcws48w4oss044s044o4gkcocks4s0k44c"
CLIENT_SECRET = "64po82nnwssosgo80wo88osok4so8kc4s8cgowkcsgc80wcoss"
USERNAME = "bradleycooper888@gmail.com"
PASSWORD = "Not4afish1234!"
TOKEN_TYPE = "sw_organization_all_data"
SCOPE = "processes provisioning"
GROUP_ID = "14926"

# Database Configuration
DB_SERVER = "172.31.6.34"
DB_NAME = "CHILI_PROD"
DB_USER = "chiliadmin"
DB_PASSWORD = "h77pc0l0"
DB_PORT = "1433"


def get_access_token():
    """Get access token from the Team on the Run API."""
    try:
        url = f"{API_BASE_URL}/request/token"
        logger.info("Getting Access Token")
        
        payload = {
            "grant_type": "authorization_credentials",
            "token_type": TOKEN_TYPE,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "username": USERNAME,
            "password": PASSWORD,
            "scope": SCOPE
        }
        
        response = requests.post(url, json=payload, verify=False)
        
        if response.status_code == 200:
            token = response.json().get('access_token')
            logger.info("Access token obtained successfully")
            return token
        else:
            logger.error(f"Failed to get token. Response: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Exception during token retrieval: {str(e)}")
        return None


def get_geo_locations(access_token):
    """Fetch geo location data for a specific group."""
    try:
        url = f"{API_BASE_URL}/api/v1/organization/group/{GROUP_ID}/lastgeolocationdata?Offset=0&Records=500"
        logger.info("Getting Geolocation Data")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            logger.info("Successfully retrieved geolocation data")
            return data
        else:
            logger.error(f"Failed to fetch geolocation data: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Exception during geo location data retrieval: {str(e)}")
        return None


def insert_location_data(location_data):
    """Insert geolocation data into the drivers_gps table."""
    try:
        conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_SERVER},{DB_PORT};DATABASE={DB_NAME};UID={DB_USER};PWD={DB_PASSWORD}"
        
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        subscriber_data = location_data.get('SubscriberData', {})
        
        # Convert string dates to datetime objects
        try:
            subscriber_date = datetime.strptime(location_data['SubscriberDataDate'], '%Y%m%dT%H:%M:%S')
        except (KeyError, ValueError) as e:
            logger.warning(f"Error parsing SubscriberDataDate: {e}")
            subscriber_date = None
            
        try:
            battery_date = datetime.strptime(subscriber_data.get('BatteryDate', ''), '%Y%m%dT%H:%M:%S') if subscriber_data.get('BatteryDate') else None
        except ValueError as e:
            logger.warning(f"Error parsing BatteryDate: {e}")
            battery_date = None
            
        try:
            network_date = datetime.strptime(subscriber_data.get('NetworkDate', ''), '%Y%m%dT%H:%M:%S') if subscriber_data.get('NetworkDate') else None
        except ValueError as e:
            logger.warning(f"Error parsing NetworkDate: {e}")
            network_date = None
            
        try:
            home_network_date = datetime.strptime(subscriber_data.get('HomeNetworkIdentityDate', ''), '%Y%m%dT%H:%M:%S') if subscriber_data.get('HomeNetworkIdentityDate') else None
        except ValueError as e:
            logger.warning(f"Error parsing HomeNetworkIdentityDate: {e}")
            home_network_date = None
        
        sql = """
        INSERT INTO [dbo].[drivers_gps] (
            [Msisdn], [SubscriberDataStatus], [GeolocationActivated], [GeolocationDeviceStatus],
            [SubscriberDataDate], [GeolocationLatitude], [GeolocationLongitude], [GeolocationAccuracy],
            [GeolocationAddress], [GeolocationSpeed], [BatteryLevel], [BatteryDate],
            [SignalStrength], [NetworkType], [NetworkDate], [MobileCountryCode],
            [MobileNetworkCode], [HomeNetworkIdentityDate], [DeviceType]
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
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
        
        cursor.execute(sql, params)
        conn.commit()
        logger.info("Successfully inserted data into drivers_gps table")
        
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()


@celery_app.task(name='tasks.collect_gps_data')
def collect_gps_data():
    """Celery task to collect and store GPS data."""
    logger.info("Starting GPS Location Data Collection")
    
    # Get access token
    access_token = get_access_token()
    if not access_token:
        logger.error("Failed to obtain access token")
        return
    
    # Get geo location data
    location_data = get_geo_locations(access_token)
    if not location_data:
        logger.error("Failed to retrieve geo location data")
        return
    
    try:
        # Extract the results array from the response
        records = location_data.get('results', [])
        if records:
            for record in records:
                insert_location_data(record)
            logger.info(f"Successfully processed {len(records)} records")
        else:
            logger.info("No records found to insert")
    except Exception as e:
        logger.error(f"Failed to insert some records: {str(e)}") 