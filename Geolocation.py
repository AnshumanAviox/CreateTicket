#!/usr/bin/env python3
"""
Script to fetch GPS location data from Team on the Run API and store in MSSQL database.
To be run as a cron job: TZ=America/Chicago/5 5-17 * 1-5 /path/to/this/script.py
"""
import requests
import pyodbc
import json
import logging
import sys
from datetime import datetime

# Set up logging
logging.basicConfig(
    filename='/var/log/geo_location_data.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('geo_location_script')

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
DB_PORT = "1433"
DB_NAME = "CHILI_PROD"
DB_USERNAME = "chiliadmin"
DB_PASSWORD = "h77pc0l0"
DB_TABLE = "GeoLocationData"

def get_access_token():
    """Get access token from the Team on the Run API."""
    try:
        url = f"{API_BASE_URL}/oauth/token"
        payload = {
            "grant_type": "password",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "username": USERNAME,
            "password": PASSWORD,
            "token_type": TOKEN_TYPE,
            "scope": SCOPE
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        response = requests.post(url, data=payload, headers=headers)
        if response.status_code == 200:
            return response.json().get('access_token')
        else:
            logger.error(f"Failed to get access token: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Exception during token retrieval: {str(e)}")
        return None

def get_geo_locations(access_token, group_id):
    """Fetch geo location data for a specific group."""
    try:
        url = f"{API_BASE_URL}/api/v1/organization/group/{group_id}/lastgeolocationdata?Offset=0&Records=500"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to fetch geo location data: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Exception during geo location data retrieval: {str(e)}")
        return None

def parse_datetime(date_str):
    """Parse datetime string from API format to Python datetime object."""
    if not date_str:
        return None
    try:
        # Format: '20250225T21:54:47'
        return datetime.strptime(date_str, '%Y%m%dT%H:%M:%S')
    except ValueError:
        logger.warning(f"Failed to parse datetime: {date_str}")
        return None

def insert_location_data(location_data):
    """Insert location data into SQL Server database."""
    conn = None
    cursor = None
    try:
        # Connect to the database
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_SERVER},{DB_PORT};DATABASE={DB_NAME};UID={DB_USERNAME};PWD={DB_PASSWORD}'
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        records_updated = 0
        records_inserted = 0
        
        # Process each location record
        for record in location_data:
            # Extract base fields
            msisdn = record.get('Msisdn')
            subscriber_data_status = record.get('SubscriberDataStatus')
            geolocation_activated = 1 if record.get('GeolocationActivated') else 0
            geolocation_device_status = 1 if record.get('GeolocationDeviceStatus') else 0
            subscriber_data_date = parse_datetime(record.get('SubscriberDataDate'))
            
            # Extract nested subscriber data
            subscriber_data = record.get('SubscriberData', {})
            
            # Query to check if record exists
            check_query = f"SELECT Msisdn FROM {DB_TABLE} WHERE Msisdn = ?"
            cursor.execute(check_query, (msisdn,))
            exists = cursor.fetchone()
            
            # Parse dates from subscriber data
            battery_date = parse_datetime(subscriber_data.get('BatteryDate'))
            network_date = parse_datetime(subscriber_data.get('NetworkDate'))
            home_network_identity_date = parse_datetime(subscriber_data.get('HomeNetworkIdentityDate'))
            
            if exists:
                # Update existing record
                update_query = f"""
                UPDATE {DB_TABLE} SET
                    SubscriberDataStatus = ?,
                    GeolocationActivated = ?,
                    GeolocationDeviceStatus = ?,
                    SubscriberDataDate = ?,
                    GeolocationLatitude = ?,
                    GeolocationLongitude = ?,
                    GeolocationAccuracy = ?,
                    GeolocationAddress = ?,
                    GeolocationSpeed = ?,
                    BatteryLevel = ?,
                    BatteryDate = ?,
                    SignalStrength = ?,
                    NetworkType = ?,
                    NetworkDate = ?,
                    MobileCountryCode = ?,
                    MobileNetworkCode = ?,
                    HomeNetworkIdentityDate = ?,
                    DeviceType = ?
                WHERE Msisdn = ?
                """
                cursor.execute(
                    update_query,
                    (
                        subscriber_data_status,
                        geolocation_activated,
                        geolocation_device_status,
                        subscriber_data_date,
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
                        home_network_identity_date,
                        subscriber_data.get('DeviceType'),
                        msisdn
                    )
                )
                records_updated += 1
            else:
                # Insert new record
                insert_query = f"""
                INSERT INTO {DB_TABLE} (
                    Msisdn,
                    SubscriberDataStatus,
                    GeolocationActivated,
                    GeolocationDeviceStatus,
                    SubscriberDataDate,
                    GeolocationLatitude,
                    GeolocationLongitude,
                    GeolocationAccuracy,
                    GeolocationAddress,
                    GeolocationSpeed,
                    BatteryLevel,
                    BatteryDate,
                    SignalStrength,
                    NetworkType,
                    NetworkDate,
                    MobileCountryCode,
                    MobileNetworkCode,
                    HomeNetworkIdentityDate,
                    DeviceType
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                cursor.execute(
                    insert_query,
                    (
                        msisdn,
                        subscriber_data_status,
                        geolocation_activated,
                        geolocation_device_status,
                        subscriber_data_date,
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
                        home_network_identity_date,
                        subscriber_data.get('DeviceType')
                    )
                )
                records_inserted += 1
        
        # Commit the transaction
        conn.commit()
        logger.info(f"Successfully processed {len(location_data)} records: {records_inserted} inserted, {records_updated} updated")
        
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def main():
    """Main execution function."""
    try:
        # Get access token
        logger.info("Starting GPS location data collection")
        access_token = get_access_token()
        if not access_token:
            logger.error("Failed to obtain access token. Exiting.")
            sys.exit(1)
        
        # Get geo location data
        logger.info(f"Getting location data for group ID: {GROUP_ID}")
        location_data = get_geo_locations(access_token, GROUP_ID)
        if not location_data:
            logger.error("Failed to retrieve geo location data. Exiting.")
            sys.exit(1)
        
        logger.info(f"Retrieved {len(location_data)} location records")
        
        # Insert data into database
        insert_location_data(location_data)
        
        logger.info("Script completed successfully")
        
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()