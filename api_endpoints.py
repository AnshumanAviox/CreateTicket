# api_endpoints.py
from auth import token_manager, get_access_token, clear_token_cache
from fastapi import APIRouter, Depends, HTTPException, Query
import json
import requests
from models import (
    ProcessTemplateResponse,
    CreateProcessRequest,
    ProcessRequest,
    Settings
)
from templates import get_template_content, populate_values_and_update_template_by_name
import pyodbc
from typing import Dict, Any, Optional
from enum import Enum

settings = Settings()
router = APIRouter()

class ProcessAction(Enum):
    SUBMIT = "submit"
    CANCEL = "cancel"
    COMPLETE = "complete"

@router.get("/template/{template_id}", response_model=ProcessTemplateResponse)
async def get_template(
    template_id: str,
    access_token: str = Depends(get_access_token)
):
    """Get template by ID"""
    template = await get_template_content(access_token, template_id)
    return {"template": template}

@router.get("/get-token")
async def get_token():
    """Get access token for testing"""
    try:
        token = await get_access_token()
        token_expiry = (
            token_manager.token_expiry.isoformat() 
            if token_manager.token_expiry 
            else None
        )
        return {
            "access_token": token,
            "cached": bool(token_manager.cached_token),
            "expires_at": token_expiry
        }
    except Exception as e:
        return {"error": str(e)}

@router.post("/refresh-token")
async def refresh_token():
    """Force refresh the access token"""
    clear_token_cache()
    token = await get_access_token()
    token_expiry = (
        token_manager.token_expiry.isoformat() 
        if token_manager.token_expiry 
        else None
    )
    return {
        "message": "Token refreshed",
        "access_token": token,
        "expires_at": token_expiry
    }

@router.post("/process/create")
async def create_process(
    request: CreateProcessRequest,
    access_token: str = Depends(get_access_token)
):
    """Create empty process from template"""
    # First fetch and print the ticket data
    ticket_data = await get_ticket_data(request.ticket_id)
    # print(ticket_data,"==============================")
    # Continue with existing template creation logic
    template_content = await get_template_content(access_token, request.template_id)
    values = populate_values_and_update_template_by_name(template_content, ticket_data)
    # print(values,"00000000000000000000000000000000000")
    
    metadata = {
        "Label": f"Ticket {request.ticket_id}",
        "Priority": 2,
        "TemplateId": request.template_id,
        "TemplateLabel": "Test Process",
        "TemplateVersion": 34,
        "Recipients": [{"Msisdn": request.msisdn}],
        "Timezone": "America/Chicago"
    }
    
    payload = {
        "Template": json.dumps(template_content),
        "Metadata": metadata,
        "Values": json.dumps(values),
        "UseRawValues": True
    }
    
    return await create_process_request(access_token, request.msisdn, payload)

# @router.post("/process/create-with-data")
# async def create_process_with_data(
#     process_data: ProcessRequest,
#     access_token: str = Depends(get_access_token)
# ):
#     """Create process with provided data"""
#     template_content = await get_template_content(
#         access_token, 
#         process_data.template_id
#     )
#     values = populate_values_and_update_template_by_name(
#         template_content,
#         pickup_time=process_data.pickup_time,
#         drop_time=process_data.drop_time,
#         trip_start_time=process_data.trip_start_time,
#         trip_end_time=process_data.trip_end_time,
#         trip_start_address=process_data.trip_start_address,
#         trip_end_address=process_data.trip_end_address,
#         trip_start_latitude=process_data.trip_start_latitude,
#         trip_start_longitude=process_data.trip_start_longitude,
#         trip_end_latitude=process_data.trip_end_latitude,
#         trip_end_longitude=process_data.trip_end_longitude,
#         wait_start_time=process_data.wait_start_time,
#         wait_end_time=process_data.wait_end_time,
#         wait_start_address=process_data.wait_start_address,
#         wait_end_address=process_data.wait_end_address,
#         wait_start_latitude=process_data.wait_start_latitude,
#         wait_start_longitude=process_data.wait_start_longitude,
#         wait_end_latitude=process_data.wait_end_latitude,
#         wait_end_longitude=process_data.wait_end_longitude
#     )
    
#     metadata = {
#         "Label": f"Ticket {process_data.ticket_id}",
#         "Priority": 2,
#         "TemplateId": process_data.template_id,
#         "TemplateLabel": "Test Process",
#         "TemplateVersion": 34,
#         "Recipients": [{"Msisdn": settings.MSISDN}],
#         "Timezone": "America/Chicago"
#     }
    
#     payload = {
#         "Template": json.dumps(template_content),
#         "Metadata": metadata,
#         "Values": json.dumps(values),
#         "UseRawValues": True
#     }
    
#     return await create_process_request(
#         access_token, 
#         settings.MSISDN, 
#         payload
#     )

async def create_process_request(access_token: str, msisdn: str, payload: dict):
    """Send process creation request"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    process_url = f"{settings.API_BASE_URL}/api/v1/subscriber/{msisdn}/process"
    
    try:
        response = requests.post(process_url, json=payload, headers=headers)
        if response.status_code == 201:
            # Extract the process ID from the response
            process_id = response.json()["results"]["ProcessId"]
            
            # Create enhanced response with all the requested information
            enhanced_response = {
                "status": "success",
                "process": {
                    "process_id": process_id,
                    "msisdn": msisdn,
                    "template_id": payload["Metadata"]["TemplateId"],
                    "ticket_id": payload["Metadata"]["Label"].split(" ")[1],  # Extract ticket_id from Label
                },
                "template": json.loads(payload["Template"]),  # Include the template
                # "values": json.loads(payload["Values"]),      # Include the values
                "metadata": payload["Metadata"],              # Include the metadata
                "api_response": response.json()               # Include original API response
            }
            
            return enhanced_response
            
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create process: {response.text}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating process: {str(e)}"
        )

async def get_ticket_data(ticket_id: str) -> Dict[str, Any]:
    """Fetch ticket data from database"""
    # Database connection details
    server = "172.31.6.34"
    database = "CHILI_PROD"
    username = "chiliadmin"
    password = "h77pc0l0"
    port = "1433"

    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server},{port};DATABASE={database};UID={username};PWD={password}"

    try:
        # Establish connection
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # SQL Query
        query = """
        SELECT 
            [Billing_ID], [Ticket_ID], [Customer_ID], [Called], [Pickup_Date], [Vehicle_Type],
            [Rate_Type], [Notes], [PO], [Pieces], [Skids], [Weight], [COD], 
            [From_Company], [From_Contact], [From_Address_1], [From_Address_2], 
            [From_City], [From_State], [From_Zip], [From_Phone], [From_Alt_Phone], 
            [To_Company], [To_Contact], [To_Address_1], [To_Address_2], 
            [To_City], [To_State], [To_Zip], [To_Phone], [To_Alt_Phone]
        FROM [dbo].[INVOICE_TABLE]
        WHERE Ticket_ID = ?;
        """

        # Execute query
        cursor.execute(query, (ticket_id,))
        
        # Get column names and results
        columns = [column[0] for column in cursor.description]
        row = cursor.fetchone()
        
        if row:
            # Convert row to dictionary
            ticket_data = dict(zip(columns, row))
            print("Ticket Data Found:")
            print(ticket_data)  # Print the data to terminal
            return ticket_data
        else:
            print(f"No data found for ticket ID: {ticket_id}")
            return {}

    except Exception as e:
        print(f"Database Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
    finally:
        cursor.close()
        conn.close()

async def process_owner_request_submit(
    access_token: str, 
    msisdn: str, 
    process_id: str, 
    action: str, 
    comment: Optional[str] = None
):
    """Send process owner request and submit"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    process_url = (
        f"{settings.API_BASE_URL}/api/v1/subscriber/{msisdn}/process/{process_id}"
        "?filter=processOwnerRequestAndSubmit"
    )
    
    payload = {
        "Action": action
    }
    if comment:
        payload["Comment"] = comment
    
    try:
        response = requests.put(process_url, json=payload, headers=headers)
        if response.status_code in [200, 201, 202]:
            return {
                "status": "success",
                "process": {
                    "process_id": process_id,
                    "msisdn": msisdn,
                    "action": action
                },
                "api_response": response.json()
            }
            
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Failed to {action} process: {response.text}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during process {action}: {str(e)}"
        )

@router.put("/api/v1/subscriber/{msisdn}/process/{process_id}")
async def process_owner_request_and_submit(
    msisdn: str,
    process_id: str,
    action: ProcessAction = Query(..., description="Action to perform (submit/cancel/complete)"),
    access_token: str = Depends(get_access_token),
    comment: Optional[str] = Query(None, description="Optional comment for the action")
):
    """
    Submit/cancel/complete a process without explicitly requesting ownership.
    Uses the processOwnerRequestAndSubmit filter.
    """
    return await process_owner_request_submit(
        access_token=access_token,
        msisdn=msisdn,
        process_id=process_id,
        action=action.value,
        comment=comment
    )