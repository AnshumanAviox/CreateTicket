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
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import InvoiceTable

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

async def get_ticket_data(ticket_id: str, db: Session):
    """Get ticket data from database"""
    try:
        ticket = db.query(InvoiceTable).filter(InvoiceTable.Ticket_ID == ticket_id).first()
        if ticket:
            # Format contact information
            from_contact_info = f"{ticket.From_Contact} - {ticket.From_Phone}" if ticket.From_Contact and ticket.From_Phone else (ticket.From_Contact or ticket.From_Phone or "")
            to_contact_info = f"{ticket.To_Contact} - {ticket.To_Phone}" if ticket.To_Contact and ticket.To_Phone else (ticket.To_Contact or ticket.To_Phone or "")
            
            # Format addresses
            from_address = " ".join(filter(None, [ticket.From_Address_1, ticket.From_Address_2]))
            to_address = " ".join(filter(None, [ticket.To_Address_1, ticket.To_Address_2]))
            
            # Format ticket details
            ticket_details = "\n".join(filter(None, [
                f"Vehicle Type: {ticket.Vehicle_Type}" if ticket.Vehicle_Type else None,
                f"PO: {ticket.PO}" if ticket.PO else None,
                f"Pieces: {ticket.Pieces}" if ticket.Pieces else None,
                f"Skids: {ticket.Skids}" if ticket.Skids else None,
                f"Weight: {ticket.Weight}" if ticket.Weight else None,
                f"COD: ${ticket.COD}" if ticket.COD else None,
                f"\nNotes: {ticket.Notes}" if ticket.Notes else None
            ]))
            
            # Add formatted fields to ticket object
            ticket.formatted_from_contact = from_contact_info
            ticket.formatted_to_contact = to_contact_info
            ticket.formatted_from_address = from_address
            ticket.formatted_to_address = to_address
            ticket.formatted_ticket_details = ticket_details
            
        return ticket
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )

@router.post("/process/create")
async def create_process(
    request: CreateProcessRequest,
    db: Session = Depends(get_db),
    access_token: str = Depends(get_access_token)
):
    """Create process from template, populated with ticket data if available"""
    # Get ticket data if it exists
    ticket_data = await get_ticket_data(request.ticket_id, db)
    template_content = await get_template_content(access_token, request.template_id)
    
    if ticket_data:
        # Populate template with existing ticket data
        values = populate_values_and_update_template_by_name(
            template_content,
            customer=ticket_data.From_Company,
            contact_info=ticket_data.formatted_from_contact,
            pickup_time=ticket_data.Pickup_Date,
            pickup_address=ticket_data.formatted_from_address,
            pickup_city=ticket_data.From_City,
            pickup_state=ticket_data.From_State,
            pickup_zip=ticket_data.From_Zip,
            drop_company=ticket_data.To_Company,
            drop_contact=ticket_data.formatted_to_contact,
            drop_address=ticket_data.formatted_to_address,
            drop_city=ticket_data.To_City,
            drop_state=ticket_data.To_State,
            drop_zip=ticket_data.To_Zip,
            ticket_details=ticket_data.formatted_ticket_details
        )
    else:
        # Create empty template if no ticket data exists
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