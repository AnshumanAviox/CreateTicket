# file_handlers.py
import base64
from fastapi import HTTPException
import os

async def encode_signature_to_base64(signature_image_path: str):
    """Encode signature image to base64"""
    try:
        with open(signature_image_path, "rb") as signature_file:
            signature_data = signature_file.read()
            return base64.b64encode(signature_data).decode("utf-8")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error encoding signature: {str(e)}"
        )

async def encode_image_to_base64(image_path: str):
    """Encode image to base64"""
    try:
        if os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                encoded_string = base64.b64encode(img_file.read()).decode('utf-8')
                return encoded_string
        raise HTTPException(
            status_code=404,
            detail=f"Image path does not exist: {image_path}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error encoding image: {str(e)}"
        )