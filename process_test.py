#!/usr/bin/env python3
"""
Test script for Team on the Run Process API operations.
"""
import requests
import json
from datetime import datetime
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# API Configuration
API_BASE_URL = "https://swapi.teamontherun.com"
CLIENT_ID = "31343_43lzb3vngtmokww8wcws48w4oss044s044o4gkcocks4s0k44c"
CLIENT_SECRET = "64po82nnwssosgo80wo88osok4so8kc4s8cgowkcsgc80wcoss"
USERNAME = "bradleycooper888@gmail.com"
PASSWORD = "Not4afish1234!"
TOKEN_TYPE = "sw_organization_all_data"
SCOPE = "processes provisioning"

# Test Configuration
MSISDN = "13142014658"  # The recipient's phone number
PROCESS_ID = "128951a4-a5ea-48a4-86a5-22c375461b3f"  # Replace with actual process ID
TEMPLATE_ID = "b55c87eb-6fc2-4830-8f6f-1c5aaeeb7a2c"  # From testing.py

def get_access_token():
    """Get access token from the Team on the Run API."""
    try:
        url = f"{API_BASE_URL}/request/token"
        print("\n=== Getting Access Token ===")
        
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
        
        response = requests.post(url, json=payload, verify=False)
        
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

def process_action(access_token, msisdn, process_id, action, comment=None):
    """
    Perform an action (submit/cancel/complete) on a process.
    
    Args:
        access_token (str): The OAuth access token
        msisdn (str): The recipient's phone number
        process_id (str): The ID of the process to act upon
        action (str): The action to perform ('submit', 'cancel', or 'complete')
        comment (str, optional): Optional comment for the action
    """
    try:
        url = f"{API_BASE_URL}/api/v1/subscriber/{msisdn}/process/{process_id}"
        url += "?filter=processOwnerRequestAndSubmit"
        print(f"\n=== Performing Process {action.title()} ===")
        print(f"URL: {url}")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Simplified payload matching documentation example
        payload = {
            "Action": action,
            "Metadata": {
                "Label": "process",
                "Recipients": [
                    {"Msisdn": msisdn}
                ],
                "TemplateId": TEMPLATE_ID
            },
            "UseRawValues": True,
            "Values": "{\"67b00a8a-a8a8-4b6d-b471-d3f7f8a0467a\":\"" + msisdn + "\"}"
        }
        
        if comment:
            payload["Comment"] = comment
            
        print("\nRequest Payload:")
        print(json.dumps(payload, indent=2))
        
        # Make the request
        response = requests.put(url, json=payload, headers=headers)
        print(f"\nResponse Status Code: {response.status_code}")
        
        if response.status_code in [200, 201, 202]:
            print(f"✓ Successfully performed {action} action on process")
            print("\nResponse Data:")
            print(json.dumps(response.json(), indent=2))
            return response.json()
        else:
            print(f"✗ Failed to {action} process. Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"✗ Exception during process {action}: {str(e)}")
        return None

def main():
    """Main execution function."""
    print("\n====== Team on the Run Process API Test ======")
    
    # Get access token
    access_token = get_access_token()
    if not access_token:
        print("✗ Failed to obtain access token. Exiting.")
        return
        
    # Test process actions
    actions = ['submit', 'cancel', 'complete']
    for action in actions:
        print(f"\nTesting {action.upper()} action...")
        result = process_action(
            access_token=access_token,
            msisdn=MSISDN,
            process_id=PROCESS_ID,
            action=action,
            comment=f"Test {action} action from API"
        )
        
        if result:
            print(f"✓ {action.title()} action test completed successfully")
        else:
            print(f"✗ {action.title()} action test failed")
        
        # Add a separator between tests
        print("\n" + "="*50)

if __name__ == "__main__":
    main() 