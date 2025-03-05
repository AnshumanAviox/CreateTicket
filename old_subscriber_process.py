import requests
import json
from typing import Dict, Any

class SubscriberProcessAPI:
    def __init__(self):
        # API Configuration
        self.base_url = "https://swapi.teamontherun.com"
        self.access_token = "NjdiNmE2MmY0MTU2ZjI3NTM0Zjk1ZDljZWZjNWFmMTMyYzg2ZmY2NzM3NDE5YTZkNzg4NDhlY2FiM2ZhYjIzZg"

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Generic method to make HTTP requests with the provided token
        """
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        kwargs['headers'] = headers

        print(f"\nMaking request to: {url}")
        response = requests.request(method, url, **kwargs)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code in (200, 201):
            return response.json()
            
        raise Exception(f"API request failed: {response.text}")

    def get_process_current_values(self, process_id: str, raw_values: bool = True, version: str = 'v1') -> Dict[str, Any]:
        """
        Get current values for a process
        """
        endpoint = f"/api/{version}/subscriber/process/{process_id}/currentvalues"
        params = {
            'RawValues': str(raw_values).lower()
        }
        response = self._make_request('get', endpoint, params=params)
        
        if response.get('status') == 'success' and 'results' in response:
            try:
                json_content = json.loads(response['results']['JsonContent'])
                
                # Create a new dictionary with field names instead of UUIDs
                readable_content = {
                    "Customer": json_content.get("6009e7d3-d270-432f-8984-260c22bb5282", ""),
                    "Contact_Info": json_content.get("ab3ee622-9f28-485e-b22a-1e69d66f22e4", ""),
                    "Pickup_Time": json_content.get("7b0f7485-81a7-4dbc-bbe3-31d09e3d6c6b", ""),
                    "Pickup_Address": json_content.get("4c1386a6-8704-417d-9ad8-e16ee164485b", {}),
                    "Drop_Company": json_content.get("9947d65b-cd83-4a4f-a192-b2040596736d", ""),
                    "Drop_Contact": json_content.get("f0f1c241-c66f-4147-8c29-a81106ebb52d", ""),
                    "Drop_Address": json_content.get("6381d343-b490-4166-b4a9-e7c82d3d9bb8", {}),
                    "Drop_Time": json_content.get("f95fe16c-7bdf-4054-8115-d9988cb27c7f", ""),
                    "Ticket_Details": json_content.get("517867f6-77a2-4200-97c4-6259de701c97", ""),
                    "Trip_Time": json_content.get("72b7b063-811b-4b51-ace3-efb28ab8a696", {}),
                    "Wait_Time": json_content.get("ea0f7c3e-5d1f-468c-bfb0-bb94b568fc75", {}),
                    "Notes": json_content.get("6fb51a25-78b3-409b-a3ef-bfeefd2cc9eb", ""),
                    "Pickup_Photo": json_content.get("7bd2829c-b07e-45e2-9a33-143627c1e434", []),  # Get Pickup Photo from json_content
                    "Drop_Photo": json_content.get("7de849cb-c5e5-4f59-a6cc-432bf717db9f", []),    # Get Drop Photo from json_content
                    "Signature": json_content.get("3e94b725-58cb-4e8e-bf82-cd3572e82cfa", "")      # Get Signature from json_content
                }
                
                # Update the JsonContent in the response with readable field names
                response['results']['JsonContent'] = json.dumps(readable_content)
                
            except json.JSONDecodeError:
                print("Warning: Could not parse JsonContent")
        
        return response

def main():
    try:
        api = SubscriberProcessAPI()
        process_id = "d66a7d75-c356-4484-bd32-f02545e88205"

        print("\nGetting Process Current Values:")
        try:
            current_values = api.get_process_current_values(process_id)
            print(json.dumps(current_values, indent=2))
        except Exception as e:
            print(f"Error getting current values: {str(e)}")

    except Exception as e:
        print(f"Fatal error: {str(e)}")

if __name__ == "__main__":
    main() 