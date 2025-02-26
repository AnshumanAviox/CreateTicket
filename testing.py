import requests
import json

# Define constants
API_BASE_URL = "https://swapi.teamontherun.com"
CLIENT_ID = "31343_43lzb3vngtmokww8wcws48w4oss044s044o4gkcocks4s0k44c"
CLIENT_SECRET = "64po82nnwssosgo80wo88osok4so8kc4s8cgowkcsgc80wcoss"
USERNAME = "bradleycooper888@gmail.com"
PASSWORD = "Not4afish1234!"
TOKEN_TYPE = "sw_organization_all_data"
SCOPE = "processes provisioning"
MSISDN = "13142014658"
PROCESS_ID = "82167099-4f5c-45f5-9d3f-169cd20e93c1"
TEMPLATE_ID = "b55c87eb-6fc2-4830-8f6f-1c5aaeeb7a2c"


def get_access_token():
    """Get an access token using the OAuth 2.0 protocol."""
    url = f"{API_BASE_URL}/request/token"
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
        return response.json()["access_token"]
    else:
        print("Failed to get access token:", response.text)
        return None


def tag_process(access_token):
    """Tag the process before submitting."""
    url = f"{API_BASE_URL}/api/v1/process/{PROCESS_ID}"  # Changed endpoint
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # More complete payload for process update
    payload = {
        "processId": PROCESS_ID,
        "templateId": TEMPLATE_ID,
        "label": "process",
        "tags": ["process"],
        "status": "draft",
        "metadata": {
            "Label": "process",
            "TemplateId": TEMPLATE_ID,
            "Recipients": [
                {"Msisdn": MSISDN}
            ]
        }
    }

    print("\nTagging process...")
    print("URL:", url)
    print("Payload:", json.dumps(payload, indent=2))

    try:
        # Try PUT first
        response = requests.put(
            url,
            json=payload, 
            headers=headers, 
            verify=False
        )
        
        if response.status_code == 404:
            # If PUT fails, try PATCH
            response = requests.patch(
                url,
                json={"tags": ["process"]},
                headers=headers,
                verify=False
            )

        print("Tag Response Status:", response.status_code)
        print("Tag Response Body:", response.text)
        return response.status_code in [200, 201, 202]

    except Exception as e:
        print("Error tagging process:", str(e))
        return False


def submit_process(access_token):
    """Submit the process using PUT method as per documentation."""
    base = f"{API_BASE_URL}/api/v1/subscriber/{MSISDN}/process/{PROCESS_ID}"
    url = f"{base}?filter=processOwnerRequestAndSubmit"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Updated payload with process tags
    payload = {
        "Action": "submit",
        "Metadata": {
            "Label": "process",
            "Recipients": [
                {"Msisdn": MSISDN}
            ],
            "TemplateId": TEMPLATE_ID,
            "TemplateLabel": "process",
            "TemplateVersion": 82,
            "ProcessTags": ["process"]  # Try adding process tags here
        },
        "UseRawValues": True,
        "Values": "{\"67b00a8a-a8a8-4b6d-b471-d3f7f8a0467a\":\"13142014658\"}",
        "ProcessTags": ["process"]  # And at root level
    }

    print("\nSubmitting process...")
    print("URL:", url)
    print("Payload:", json.dumps(payload, indent=2))

    try:
        response = requests.put(
            url,
            json=payload, 
            headers=headers, 
            verify=False
        )

        print("\nResponse Status Code:", response.status_code)
        print("Response Body:", response.text)
        return response.status_code in [200, 201, 202]

    except Exception as e:
        print("Error occurred:", str(e))
        return False


def main():
    """Main execution flow."""
    access_token = get_access_token()
    if not access_token:
        return

    # Try submission directly with process tags
    if not submit_process(access_token):
        print("Failed to submit process")
        return

    print("Process submission completed")


if __name__ == "__main__":
    main()