# api_endpoints.py
from auth import token_manager, get_access_token, clear_token_cache
from fastapi import APIRouter, Depends, HTTPException
import json
import requests
from models import (
    ProcessTemplateResponse,
    CreateProcessRequest,
    ProcessRequest,
    Settings
)
from templates import get_template_content, populate_values_and_update_template_by_name

settings = Settings()
router = APIRouter()

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
    template_content = await get_template_content(access_token, request.template_id)
    values = populate_values_and_update_template_by_name(template_content)
    
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

@router.post("/process/create-with-data")
async def create_process_with_data(
    process_data: ProcessRequest,
    access_token: str = Depends(get_access_token)
):
    """Create process with provided data"""
    template_content = await get_template_content(
        access_token, 
        process_data.template_id
    )
    values = populate_values_and_update_template_by_name(
        template_content,
        pickup_time=process_data.pickup_time,
        drop_time=process_data.drop_time,
        trip_start_time=process_data.trip_start_time,
        trip_end_time=process_data.trip_end_time,
        trip_start_address=process_data.trip_start_address,
        trip_end_address=process_data.trip_end_address,
        trip_start_latitude=process_data.trip_start_latitude,
        trip_start_longitude=process_data.trip_start_longitude,
        trip_end_latitude=process_data.trip_end_latitude,
        trip_end_longitude=process_data.trip_end_longitude,
        wait_start_time=process_data.wait_start_time,
        wait_end_time=process_data.wait_end_time,
        wait_start_address=process_data.wait_start_address,
        wait_end_address=process_data.wait_end_address,
        wait_start_latitude=process_data.wait_start_latitude,
        wait_start_longitude=process_data.wait_start_longitude,
        wait_end_latitude=process_data.wait_end_latitude,
        wait_end_longitude=process_data.wait_end_longitude
    )
    
    metadata = {
        "Label": f"Ticket {process_data.ticket_id}",
        "Priority": 2,
        "TemplateId": process_data.template_id,
        "TemplateLabel": "Test Process",
        "TemplateVersion": 34,
        "Recipients": [{"Msisdn": settings.MSISDN}],
        "Timezone": "America/Chicago"
    }
    
    payload = {
        "Template": json.dumps(template_content),
        "Metadata": metadata,
        "Values": json.dumps(values),
        "UseRawValues": True
    }
    
    return await create_process_request(
        access_token, 
        settings.MSISDN, 
        payload
    )

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
            return response.json()
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create process: {response.text}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating process: {str(e)}"
        )