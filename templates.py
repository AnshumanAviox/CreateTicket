# templates.py
from fastapi import HTTPException
import requests
import json
import base64
import os
from datetime import datetime
from models import Settings
from typing import Optional, List, Dict, Any

settings = Settings()

def encode_signature_to_base64(signature_image_path: str) -> Optional[str]:
    """Encode signature image to base64"""
    try:
        with open(signature_image_path, "rb") as signature_file:
            signature_data = signature_file.read()
            return base64.b64encode(signature_data).decode("utf-8")
    except Exception as e:
        print(f"Error encoding signature: {e}")
        return None

def encode_image_to_base64(image_path: str) -> Optional[str]:
    """Encode image to base64"""
    try:
        if os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                encoded_string = base64.b64encode(img_file.read()).decode('utf-8')
                return encoded_string
        print(f"Path does not exist: {image_path}")
        return None
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None

async def get_template_content(access_token: str, template_id: str):
    """Fetch template content by template_id"""
    url = f"{settings.API_BASE_URL}/api/v1/processtemplate/{template_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            template = extract_json_content(response.json())
            return template
        raise HTTPException(
            status_code=404,
            detail=f"Template not found: {response.text}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching template: {str(e)}"
        )

def extract_json_content(api_response: Dict) -> Dict:
    """Extract JsonContent from API response"""
    try:
        if api_response.get("status") == "success" and "JsonContent" in api_response.get("results", {}):
            json_content = api_response["results"]["JsonContent"]
            return json.loads(json_content)
        raise ValueError("Invalid API response format or missing 'JsonContent'")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error extracting JsonContent: {str(e)}"
        )

def populate_values_and_update_template_by_name(
    template: Dict,
    ticket_data:Dict,
    customer_name: Optional[str] = None,
    pickup_time: Optional[datetime] = None,
    drop_time: Optional[datetime] = None,
    trip_start_time: Optional[datetime] = None,
    trip_end_time: Optional[datetime] = None,
    trip_start_address: Optional[str] = None,
    trip_end_address: Optional[str] = None,
    trip_start_latitude: Optional[float] = None,
    trip_start_longitude: Optional[float] = None,
    trip_end_latitude: Optional[float] = None,
    trip_end_longitude: Optional[float] = None,
    wait_start_time: Optional[datetime] = None,
    wait_end_time: Optional[datetime] = None,
    wait_start_address: Optional[str] = None,
    wait_end_address: Optional[str] = None,
    wait_start_latitude: Optional[float] = None,
    wait_start_longitude: Optional[float] = None,
    wait_end_latitude: Optional[float] = None,
    wait_end_longitude: Optional[float] = None,
    signature_image_path: Optional[str] = None,
    drop_photo: Optional[List[str]] = None,
    pickup_photo: Optional[List[str]] = None
) -> Dict:
    """
    Populate values for the fields in the template based on their name
    and update the default values in the template.
    """
    values = {}
    print(ticket_data,"32222222222222222222222222222")

    if "label" in template:
        template["label"] = "Ticket 1234"

    for block in template.get("blocks", []):
        for field in block.get("fields", []):
            field_name = field.get("friendlyName")
            field_type = field.get("type")

            # Handle Customer and Contact Info fields
            if field_name in ["Customer"] and field_type == "text":
                field_uuid = field["uuid"]
                field_value = ticket_data.get('From_Company', '')
                values[field_uuid] = field_value
                field["defaultValue"] = field_value
                field["unsupportedTypeValue"] = field_value

            elif field_name in ["Contact Info"] and field_type == "text":
                field_uuid = field["uuid"]
                contact = ticket_data.get('From_Contact', '')
                phone = ticket_data.get('From_Phone', '')
                field_value = f"{contact}{phone}" if contact and phone else contact or phone
                values[field_uuid] = field_value
                field["defaultValue"] = field_value
                field["unsupportedTypeValue"] = field_value
                # values[field_uuid] = ""
                # field["defaultValue"] = "New John"
                # field["unsupportedTypeValue"] = "New John"

            # Handle Pickup Time field
            elif field_name in ["Pickup Time"] and field_type == "date":
                field_uuid = field.get("uuid")
                print("2024-09-07T11:16:35","-0-------------------")
                if pickup_time:
                    formatted_time = {
                        "date": "02/04/2025",
                        "time": "10:45 AM",
                        "tzd": "UTC"
                    }
                    # values[field_uuid] = formatted_time
                    field_value = ticket_data.get('Pickup_Date', '')
                    field["value"] = "2024-09-07T11:16:35"
                    field["defaultValue"] = "2024-09-07T11:16:35"
                    field["unsupportedTypeValue"] = "2024-09-07T11:16:35"
                    field["hasValue"] = True
                else:
                    empty_time = {"date": "", "time": "", "tzd": ""}
                    field["value"] = empty_time
                    field["defaultValue"] = empty_time
                    field["unsupportedTypeValue"] = empty_time
                    field["hasValue"] = False

            # Handle Address fields
            elif field_name in ["Pickup Address"] and field_type == "address":
                address_uuid = field["uuid"]
                address_options = field.get("options", {})
                location_uuid = address_options.get("address", {}).get("uuid", "")
                
                # Format complete address from components
                if field_name == "Pickup Address":
                    address_line1 = ticket_data.get('From_Address_1', '')
                    address_line2 = ticket_data.get('From_Address_2', '')
                    city = ticket_data.get('From_City', '')
                    state = ticket_data.get('From_State', '')
                    zip_code = str(ticket_data.get('From_Zip', ''))
                else:  # Drop Address
                    address_line1 = ticket_data.get('To_Address_1', '')
                    address_line2 = ticket_data.get('To_Address_2', '')
                    city = ticket_data.get('To_City', '')
                    state = ticket_data.get('To_State', '')
                    zip_code = str(ticket_data.get('To_Zip', ''))

                # Combine address components
                full_address = address_line1
                if address_line2:
                    full_address += f" {address_line2}"
                if city and state:
                    full_address += f", {city}, {state}"
                if zip_code:
                    full_address += f" {zip_code}"
                
                address_value = {
                    location_uuid: {
                        address_options["address"]["options"]["location"]["uuid"]: full_address,
                        address_options["address"]["options"]["latitude"]["uuid"]: "",
                        address_options["address"]["options"]["longitude"]["uuid"]: "",
                        address_options["address"]["options"]["image"]["uuid"]: [],
                        address_options["address"]["options"]["accuracy"]["uuid"]: ""
                    },
                    address_options["zipCode"]["uuid"]: zip_code
                }
                values[address_uuid] = address_value
                field["defaultValue"] = address_value
                field["unsupportedTypeValue"] = address_value

            elif field_name in ["Drop Address"] and field_type == "address":
                address_uuid = field["uuid"]
                address_options = field.get("options", {})
                location_uuid = address_options.get("address", {}).get("uuid", "")
                
                # Format complete address from components
                if field_name == "Drop Address":
                    address_line1 = ticket_data.get('From_Address_1', '')
                    address_line2 = ticket_data.get('From_Address_2', '')
                    city = ticket_data.get('From_City', '')
                    state = ticket_data.get('From_State', '')
                    zip_code = str(ticket_data.get('From_Zip', ''))
                else:  # Drop Address
                    address_line1 = ticket_data.get('To_Address_1', '')
                    address_line2 = ticket_data.get('To_Address_2', '')
                    city = ticket_data.get('To_City', '')
                    state = ticket_data.get('To_State', '')
                    zip_code = str(ticket_data.get('To_Zip', ''))

                # Combine address components
                full_address = address_line1
                if address_line2:
                    full_address += f" {address_line2}"
                if city and state:
                    full_address += f", {city}, {state}"
                if zip_code:
                    full_address += f" {zip_code}"
                
                address_value = {
                    location_uuid: {
                        address_options["address"]["options"]["location"]["uuid"]: full_address,
                        address_options["address"]["options"]["latitude"]["uuid"]: "",
                        address_options["address"]["options"]["longitude"]["uuid"]: "",
                        address_options["address"]["options"]["image"]["uuid"]: [],
                        address_options["address"]["options"]["accuracy"]["uuid"]: ""
                    },
                    address_options["zipCode"]["uuid"]: zip_code
                }
                values[address_uuid] = address_value
                field["defaultValue"] = address_value
                field["unsupportedTypeValue"] = address_value

            # Handle Separator
            elif field_name == "Separator" and field_type == "separator":
                field_uuid = field["uuid"]

            # Handle Drop Company and Contact
            elif field_name in ["Drop Company"] and field_type == "text":
                field_uuid = field["uuid"]
                field_value = ticket_data.get('To_Company', '')
                values[field_uuid] = field_value
                field["defaultValue"] = field_value
                field["unsupportedTypeValue"] = field_value

            elif field_name in ["Drop Contact"] and field_type == "text":
                field_uuid = field["uuid"]
                to_contact = ticket_data.get('To_Contact', '')
                to_phone = ticket_data.get('To_Phone', '')
                field_value = f"{to_contact} - {to_phone}" if to_contact and to_phone else to_contact or to_phone
                values[field_uuid] = field_value
                field["defaultValue"] = field_value
                field["unsupportedTypeValue"] = field_value

            # Handle Drop Time
            elif field_name.strip().lower() == "drop time" and field_type.strip().lower() == "date":
                field_uuid = field.get("uuid")
                if drop_time:
                    formatted_time = {
                        "date": "02/04/2025",
                        "time": "10:45 AM",
                        "tzd": "UTC"
                    }
                    values[field_uuid] = formatted_time
                    field["value"] = formatted_time
                    field["defaultValue"] = formatted_time
                    field["unsupportedTypeValue"] = formatted_time
                    field["hasValue"] = True
                else:
                    empty_time = {"date": "", "time": "", "tzd": ""}
                    field["value"] = empty_time
                    field["defaultValue"] = empty_time
                    field["unsupportedTypeValue"] = empty_time
                    field["hasValue"] = False

            # Handle Notes and Ticket Details
            elif field_name in ["Notes"] and field_type == "textarea":
                field_uuid = field["uuid"]
                values[field_uuid] = ""
                field["defaultValue"] = ""
                field["unsupportedTypeValue"] = ""

            elif field_name in ["Ticket Details"] and field_type == "textarea":
                field_uuid = field["uuid"]
                vehicle_type = ticket_data.get('Vehicle_Type', '')
                po = ticket_data.get('PO', '')
                pieces = ticket_data.get('Pieces', '')
                skids = ticket_data.get('Skids', '')
                weight = ticket_data.get('Weight', '')
                cod = ticket_data.get('COD', '')
                notes = ticket_data.get('Notes', '')
                field_value = f"{vehicle_type}, {po}, {pieces}, {skids}, {weight}, {cod}, {notes}" if vehicle_type and po and pieces and skids and weight and cod and notes else vehicle_type or po or pieces or skids or weight or cod or notes
                values[field_uuid] = field_value
                field["defaultValue"] = field_value
                field["unsupportedTypeValue"] = field_value

            # Handle Signature
            elif field_name == "Signature" and field_type == "signature":
                if signature_image_path:
                    encoded_signature = encode_signature_to_base64(signature_image_path)
                    if encoded_signature:
                        field_uuid = field["uuid"]
                        values[field_uuid] = encoded_signature
                        field["unsupportedTypeValue"] = encoded_signature
                        field["hasValue"] = True
                    else:
                        field["unsupportedTypeValue"] = None
                        field["hasValue"] = False
                else:
                    field["unsupportedTypeValue"] = None
                    field["hasValue"] = False

            # Handle Photos
            elif field_name in ["Drop Photo", "Pickup Photo"] and field_type == "file":
                photo_list = drop_photo if field_name == "Drop Photo" else pickup_photo
                if photo_list:
                    uploaded_files = []
                    for file_path in photo_list:
                        encoded_image = encode_image_to_base64(file_path)
                        if encoded_image:
                            uploaded_files.append(encoded_image)
                    if uploaded_files:
                        field_uuid = field["uuid"]
                        values[field_uuid] = uploaded_files
                        field["unsupportedTypeValue"] = uploaded_files
                        field["hasValue"] = True
                    else:
                        field["unsupportedTypeValue"] = []
                        field["hasValue"] = False
                else:
                    field["unsupportedTypeValue"] = []
                    field["hasValue"] = False

            # Handle Trip Time
            elif field_name == "Trip Time" and field_type == "startstop":
                field_uuid = field["uuid"]
                start_options = field.get("options", {}).get("start", {})
                stop_options = field.get("options", {}).get("stop", {})
                
                start_stop_values = {
                    start_options["uuid"]: {
                        start_options["options"]["date"]["uuid"]: {
                            "date": trip_start_time.strftime("%m/%d/%Y") if trip_start_time else "",
                            "time": trip_start_time.strftime("%I:%M %p") if trip_start_time else "",
                            "tzd": ""
                        },
                        start_options["options"]["location"]["uuid"]: {
                            start_options["options"]["location"]["options"]["location"]["uuid"]: trip_start_address if trip_start_address else "",
                            start_options["options"]["location"]["options"]["latitude"]["uuid"]: trip_start_latitude if trip_start_latitude else "",
                            start_options["options"]["location"]["options"]["longitude"]["uuid"]: trip_start_longitude if trip_start_longitude else "",
                            start_options["options"]["location"]["options"]["image"]["uuid"]: [],
                            start_options["options"]["location"]["options"]["accuracy"]["uuid"]: ""
                        }
                    },
                    stop_options["uuid"]: {
                        stop_options["options"]["date"]["uuid"]: {
                            "date": trip_end_time.strftime("%m/%d/%Y") if trip_end_time else "",
                            "time": trip_end_time.strftime("%I:%M %p") if trip_end_time else "",
                            "tzd": ""
                        },
                        stop_options["options"]["location"]["uuid"]: {
                            stop_options["options"]["location"]["options"]["location"]["uuid"]: trip_end_address if trip_end_address else "",
                            stop_options["options"]["location"]["options"]["latitude"]["uuid"]: trip_end_latitude if trip_end_latitude else "",
                            stop_options["options"]["location"]["options"]["longitude"]["uuid"]: trip_end_longitude if trip_end_longitude else "",
                            stop_options["options"]["location"]["options"]["image"]["uuid"]: [],
                            stop_options["options"]["location"]["options"]["accuracy"]["uuid"]: ""
                        }
                    }
                }
                
                values[field_uuid] = start_stop_values
                field["unsupportedTypeValue"] = start_stop_values
                field["hasValue"] = True

            # Handle Wait Time
            elif field_name == "Wait Time" and field_type == "startstop":
                field_uuid = field["uuid"]
                start_options = field.get("options", {}).get("start", {})
                stop_options = field.get("options", {}).get("stop", {})
                
                start_stop_values = {
                    start_options["uuid"]: {
                        start_options["options"]["date"]["uuid"]: {
                            "date": wait_start_time.strftime("%m/%d/%Y") if wait_start_time else "",
                            "time": wait_start_time.strftime("%I:%M %p") if wait_start_time else "",
                            "tzd": ""
                        },
                        start_options["options"]["location"]["uuid"]: {
                            start_options["options"]["location"]["options"]["location"]["uuid"]: wait_start_address if wait_start_address else "",
                            start_options["options"]["location"]["options"]["latitude"]["uuid"]: wait_start_latitude if wait_start_latitude else "",
                            start_options["options"]["location"]["options"]["longitude"]["uuid"]: wait_start_longitude if wait_start_longitude else "",
                            start_options["options"]["location"]["options"]["image"]["uuid"]: [],
                            start_options["options"]["location"]["options"]["accuracy"]["uuid"]: ""
                        }
                    },
                    stop_options["uuid"]: {
                        stop_options["options"]["date"]["uuid"]: {
                            "date": wait_end_time.strftime("%m/%d/%Y") if wait_end_time else "",
                            "time": wait_end_time.strftime("%I:%M %p") if wait_end_time else "",
                            "tzd": ""
                        },
                        stop_options["options"]["location"]["uuid"]: {
                            stop_options["options"]["location"]["options"]["location"]["uuid"]: wait_end_address if wait_end_address else "",
                            stop_options["options"]["location"]["options"]["latitude"]["uuid"]: wait_end_latitude if wait_end_latitude else "",
                            stop_options["options"]["location"]["options"]["longitude"]["uuid"]: wait_end_longitude if wait_end_longitude else "",
                            stop_options["options"]["location"]["options"]["image"]["uuid"]: [],
                            stop_options["options"]["location"]["options"]["accuracy"]["uuid"]: ""
                        }
                    }
                }
                
                values[field_uuid] = start_stop_values
                field["unsupportedTypeValue"] = start_stop_values
                field["hasValue"] = True

            # Handle any other fields
            else:
                values[field["uuid"]] = ""

    return values