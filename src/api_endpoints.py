from src.auth import token_manager, get_access_token, clear_token_cache
from fastapi import APIRouter, Depends, HTTPException, Query
import json
import requests
from src.models import (
    ProcessTemplateResponse,
    CreateProcessRequest,
    ProcessRequest,
    Settings
)
from src.templates import get_template_content, populate_values_and_update_template_by_name
# ... rest of the file remains the same 