#!/usr/bin/env python3
"""
Script to fetch GPS location data from Team on the Run API.
"""
import requests
import json

# API Configuration
API_BASE_URL = "https://swapi.teamontherun.com"
CLIENT_ID = "31343_43lzb3vngtmokww8wcws48w4oss044s044o4gkcocks4s0k44c"
CLIENT_SECRET = "64po82nnwssosgo80wo88osok4so8kc4s8cgowkcsgc80wcoss"
USERNAME = "bradleycooper888@gmail.com"
PASSWORD = "Not4afish1234!"
TOKEN_TYPE = "sw_organization_all_data"
SCOPE = "processes provisioning"
GROUP_ID = "14926"

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

if __name__ == "__main__":
    main()