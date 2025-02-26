#!/usr/bin/env python3
"""
Script to fetch GPS location data from Team on the Run API and store in MSSQL database.
To be run as a cron job: TZ=America/Chicago/5 5-17 * 1-5 /path/to/this/script.py
"""
import requests
import pyodbc
import json
# import logging
import sys
from datetime import datetime

# Set up logging
# logging.basicConfig(
#     filename='/var/log/geo_location_data.log',
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger('geo_location_script')

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
        print("\n=== Getting Access Token ===")
        print(f"Making request to: {url}")
        
        # Define payload and headers
        payload = {
            "grant_type": "password",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "username": USERNAME,
            "password": PASSWORD,
            "token_type": TOKEN_TYPE,
            "scope": SCOPE
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        print("Payload:", {
            "grant_type": "password",
            "client_id": CLIENT_ID,
            "client_secret": "***hidden***",
            "username": USERNAME,
            "password": "***hidden***",
            "token_type": TOKEN_TYPE,
            "scope": SCOPE
        })
        
        response = requests.post(url, data=payload, headers=headers)
        print(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            token = response.json().get('access_token')
            print("Access token obtained successfully")
            print(f"Token (first 10 chars): {token[:10]}...")
            return token
        else:
            print(f"Failed to get token. Response: {response.text}")
            return None
    except Exception as e:
        print(f"Exception during token retrieval: {str(e)}")
        return None

def get_geo_locations(access_token, group_id):
    """Fetch geo location data for a specific group."""
    try:
        url = f"{API_BASE_URL}/api/v1/organization/group/{group_id}/lastgeolocationdata?Offset=0&Records=500"
        print("\n=== Getting Geolocation Data ===")
        print(f"Making request to: {url}")
        print(f"Using group_id: {group_id}")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        print("Headers:", {
            "Authorization": f"Bearer {access_token[:10]}...",
            "Content-Type": "application/json"
        })
        
        response = requests.get(url, headers=headers)
        print(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\nGeolocation API Response Summary:")
            print(f"Number of records received: {len(data)}")
            print("\nFirst record details:")
            first_record = data[0] if data else None
            if first_record:
                print(f"MSISDN: {first_record.get('Msisdn')}")
                print(f"Status: {first_record.get('SubscriberDataStatus')}")
                print(f"Geolocation Activated: {first_record.get('GeolocationActivated')}")
                print("\nSubscriber Data Sample:")
                subscriber_data = first_record.get('SubscriberData', {})
                print(f"Latitude: {subscriber_data.get('GeolocationLatitude')}")
                print(f"Longitude: {subscriber_data.get('GeolocationLongitude')}")
                print(f"Address: {subscriber_data.get('GeolocationAddress')}")
            return data
        else:
            print(f"\nError getting geolocation data: {response.status_code}")
            print(f"Response: {response.text}\n")
            return None
    except Exception as e:
        print(f"Exception during geo location data retrieval: {str(e)}")
        return None

def parse_datetime(date_str):
    """Parse datetime string from API format to Python datetime object."""
    if not date_str:
        return None
    try:
        # Format: '20250225T21:54:47'
        return datetime.strptime(date_str, '%Y%m%dT%H:%M:%S')
    except ValueError:
        # logger.warning(f"Failed to parse datetime: {date_str}")
        return None

def insert_location_data(location_data):
    """Insert location data into SQL Server database."""
    conn = None
    cursor = None
    try:
        print("\n=== Database Operations ===")
        print("Attempting database connection...")
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_SERVER},{DB_PORT};DATABASE={DB_NAME};UID={DB_USERNAME};PWD=***hidden***'
        print(f"Connection string (masked): {conn_str.replace(DB_PASSWORD, '***hidden***')}")
        
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        print("Database connection successful")
        
        records_updated = 0
        records_inserted = 0
        records_failed = 0
        
        total_records = len(location_data)
        print(f"\nProcessing {total_records} records...")
        
        for index, record in enumerate(location_data, 1):
            try:
                msisdn = record.get('Msisdn')
                print(f"\nProcessing record {index}/{total_records}")
                print(f"MSISDN: {msisdn}")
                
                # Extract and print key data points
                subscriber_data = record.get('SubscriberData', {})
                print("Key data points:")
                print(f"- Status: {record.get('SubscriberDataStatus')}")
                print(f"- Location: {subscriber_data.get('GeolocationLatitude')}, {subscriber_data.get('GeolocationLongitude')}")
                print(f"- Address: {subscriber_data.get('GeolocationAddress')}")
                
                # Check if record exists
                check_query = f"SELECT Msisdn FROM {DB_TABLE} WHERE Msisdn = ?"
                cursor.execute(check_query, (msisdn,))
                exists = cursor.fetchone()
                
                if exists:
                    print(f"Updating existing record...")
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
                            record.get('SubscriberDataStatus'),
                            record.get('GeolocationActivated'),
                            record.get('GeolocationDeviceStatus'),
                            parse_datetime(record.get('SubscriberDataDate')),
                            subscriber_data.get('GeolocationLatitude'),
                            subscriber_data.get('GeolocationLongitude'),
                            subscriber_data.get('GeolocationAccuracy'),
                            subscriber_data.get('GeolocationAddress'),
                            subscriber_data.get('GeolocationSpeed'),
                            subscriber_data.get('BatteryLevel'),
                            parse_datetime(subscriber_data.get('BatteryDate')),
                            subscriber_data.get('SignalStrength'),
                            subscriber_data.get('NetworkType'),
                            parse_datetime(subscriber_data.get('NetworkDate')),
                            subscriber_data.get('MobileCountryCode'),
                            subscriber_data.get('MobileNetworkCode'),
                            parse_datetime(subscriber_data.get('HomeNetworkIdentityDate')),
                            subscriber_data.get('DeviceType'),
                            msisdn
                        )
                    )
                    records_updated += 1
                    print("Update successful")
                else:
                    print(f"Inserting new record...")
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
                            record.get('SubscriberDataStatus'),
                            record.get('GeolocationActivated'),
                            record.get('GeolocationDeviceStatus'),
                            parse_datetime(record.get('SubscriberDataDate')),
                            subscriber_data.get('GeolocationLatitude'),
                            subscriber_data.get('GeolocationLongitude'),
                            subscriber_data.get('GeolocationAccuracy'),
                            subscriber_data.get('GeolocationAddress'),
                            subscriber_data.get('GeolocationSpeed'),
                            subscriber_data.get('BatteryLevel'),
                            parse_datetime(subscriber_data.get('BatteryDate')),
                            subscriber_data.get('SignalStrength'),
                            subscriber_data.get('NetworkType'),
                            parse_datetime(subscriber_data.get('NetworkDate')),
                            subscriber_data.get('MobileCountryCode'),
                            subscriber_data.get('MobileNetworkCode'),
                            parse_datetime(subscriber_data.get('HomeNetworkIdentityDate')),
                            subscriber_data.get('DeviceType')
                        )
                    )
                    records_inserted += 1
                    print("Insert successful")
                
            except Exception as e:
                records_failed += 1
                print(f"Failed to process record: {str(e)}")
                continue
        
        # Commit the transaction
        conn.commit()
        print("\n=== Database Operation Summary ===")
        print(f"Total records processed: {total_records}")
        print(f"Successfully inserted: {records_inserted}")
        print(f"Successfully updated: {records_updated}")
        print(f"Failed to process: {records_failed}")
        
    except Exception as e:
        print(f"\nDatabase error: {str(e)}")
        if conn:
            conn.rollback()
            print("Transaction rolled back")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("Database connection closed")

def main():
    """Main execution function."""
    print("\n====== Starting GPS Location Data Collection ======")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API URL: {API_BASE_URL}")
    print(f"Group ID: {GROUP_ID}")
    
    # Get access token
    print("\nStep 1: Getting access token...")
    access_token = get_access_token()
    if access_token:
        print("✓ Access token obtained successfully")
    else:
        print("✗ Failed to obtain access token")
        sys.exit(1)
    
    # Get geo location data
    print("\nStep 2: Fetching location data...")
    location_data = get_geo_locations(access_token, GROUP_ID)
    if not location_data:
        print("✗ Failed to retrieve geo location data")
        sys.exit(1)
    print(f"✓ Successfully retrieved {len(location_data)} location records")
    
    # Insert data into database
    print("\nStep 3: Processing database operations...")
    insert_location_data(location_data)
    
    print("\n====== Script Execution Completed ======")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()