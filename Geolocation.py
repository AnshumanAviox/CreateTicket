#!/usr/bin/env python3
"""
Script to fetch GPS location data from Team on the Run API.
"""
import requests
import json
import pyodbc
from datetime import datetime

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
        print("\n=== Getting Access Token ===")
        print(f"Making request to: {url}")
        
        payload = {
            "grant_type": "authorization_credentials",
            "token_type": TOKEN_TYPE,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "username": USERNAME,
            "password": PASSWORD,
            "scope": SCOPE
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        print("Attempting to get access token...")
        response = requests.post(url, json=payload, verify=False)
        print(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            token = response.json().get('access_token')
            print("✓ Access token obtained successfully")
            return token
        else:
            print(f"✗ Failed to get token. Response: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Exception during token retrieval: {str(e)}")
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
        
        response = requests.get(url, headers=headers)
        print(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Successfully retrieved geolocation data")
            return data
        else:
            print(f"✗ Failed to fetch geolocation data: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Exception during geo location data retrieval: {str(e)}")
        return None

def insert_location_data(location_data):
    """Insert geolocation data into the database."""
    try:
        # Create connection string
        conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_SERVER},{DB_PORT};DATABASE={DB_NAME};UID={DB_USER};PWD={DB_PASSWORD}"
        
        # Establish connection
        print("\n=== Inserting Data into Database ===")
        print("Connecting to database...")
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Parse the subscriber data
        subscriber_data = location_data.get('SubscriberData', {})
        
        # Convert string dates to datetime objects
        subscriber_date = datetime.strptime(location_data['SubscriberDataDate'], '%Y%m%dT%H:%M:%S')
        battery_date = datetime.strptime(subscriber_data.get('BatteryDate', ''), '%Y%m%dT%H:%M:%S') if subscriber_data.get('BatteryDate') else None
        network_date = datetime.strptime(subscriber_data.get('NetworkDate', ''), '%Y%m%dT%H:%M:%S') if subscriber_data.get('NetworkDate') else None
        home_network_date = datetime.strptime(subscriber_data.get('HomeNetworkIdentityDate', ''), '%Y%m%dT%H:%M:%S') if subscriber_data.get('HomeNetworkIdentityDate') else None
        
        # Prepare SQL query
        sql = """
        INSERT INTO [dbo].[GEOLOCATION_DATA] (
            [Msisdn], [SubscriberDataStatus], [GeolocationActivated], [GeolocationDeviceStatus],
            [SubscriberDataDate], [GeolocationLatitude], [GeolocationLongitude], [GeolocationAccuracy],
            [GeolocationAddress], [GeolocationSpeed], [BatteryLevel], [BatteryDate],
            [SignalStrength], [NetworkType], [NetworkDate], [MobileCountryCode],
            [MobileNetworkCode], [HomeNetworkIdentityDate], [DeviceType]
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        # Prepare parameters
        params = [
            location_data['Msisdn'],
            location_data['SubscriberDataStatus'],
            1 if location_data['GeolocationActivated'] else 0,
            1 if location_data['GeolocationDeviceStatus'] else 0,
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
        print("✓ Successfully inserted data into database")
        
    except Exception as e:
        print(f"✗ Database error: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()

def main():
    """Main execution function."""
    print("\n====== Starting GPS Location Data Collection ======")
    
    # Get access token
    access_token = get_access_token()
    if not access_token:
        print("✗ Failed to obtain access token. Exiting.")
        return
    
    # Get geo location data
    location_data = get_geo_locations(access_token, GROUP_ID)
    if not location_data:
        print("✗ Failed to retrieve geo location data. Exiting.")
        return
    
    # Print the data in formatted JSON
    print("\n=== Retrieved Data ===")
    print(f"Number of records: {len(location_data)}")
    print("\nData in JSON format:")
    print(json.dumps(location_data, indent=2))
    
    # Insert data into database
    try:
        for record in location_data:
            insert_location_data(record)
        print("✓ All records successfully inserted into database")
    except Exception as e:
        print(f"✗ Failed to insert some records: {str(e)}")

if __name__ == "__main__":
    main()