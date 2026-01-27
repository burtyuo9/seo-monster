"""
AWS SES API Routes - API для управления рассылками
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional
import os
import shutil

router = APIRouter(prefix="/api/ses", tags=["AWS SES"])

# Import services
from services.aws_ses_service import ses_service
from services.email_content_generator import email_generator
from services.recipient_manager import recipient_manager


class AddKeyRequest(BaseModel):
    access_key_id: str
    secret_access_key: str
    region: str = "us-east-1"
    name: str = ""

class GenerateContentRequest(BaseModel):
    task: str
    format_type: str = "html"
    language: str = "ru"
    tone: str = "professional"

class ManualContentRequest(BaseModel):
    name: str
    subject: str
    html_body: str = ""
    text_body: str = ""
    preheader: str = ""
    format_type: str = "html"

class ManualListRequest(BaseModel):
    name: str
    emails: List[str]
    description: str = ""


# === AWS Keys ===

@router.get("/keys")
async def get_all_keys():
    return {"keys": ses_service.get_all_keys()}

@router.post("/keys")
async def add_key(request: AddKeyRequest):
    result = await ses_service.add_aws_key(
        request.access_key_id, request.secret_access_key,
        request.region, request.name
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@router.get("/keys/{key_id}")
async def get_key_info(key_id: str):
    info = ses_service.get_key_info(key_id)
    if not info:
        raise HTTPException(status_code=404, detail="Key not found")
    return {"key": info}

@router.post("/keys/{key_id}/refresh")
async def refresh_key(key_id: str):
    result = await ses_service.refresh_key_info(key_id)
    return result

@router.delete("/keys/{key_id}")
async def delete_key(key_id: str):
    if ses_service.delete_key(key_id):
        return {"success": True}
    raise HTTPException(status_code=404, detail="Key not found")

@router.get("/regions")
async def get_regions():
    return {"regions": ses_service.get_available_regions()}


# === Email Content ===

@router.get("/content")
async def get_all_content():
    return {"contents": email_generator.get_all_contents()}

@router.post("/content/generate")
async def generate_content(request: GenerateContentRequest):
    result = await email_generator.generate_content_ai(
        request.task, request.format_type,
        request.language, request.tone
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@router.post("/content/manual")
async def create_content_manual(request: ManualContentRequest):
    result = email_generator.create_content_manual(
        request.name, request.subject, request.html_body,
        request.text_body, request.preheader, request.format_type
    )
    return result

@router.post("/content/upload")
async def upload_content(file: UploadFile = File(...), name: str = Form(...)):
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    result = email_generator.upload_html_file(temp_path, name)
    os.remove(temp_path)
    return result

@router.get("/content/{content_id}")
async def get_content(content_id: str):
    content = email_generator.get_content(content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return {"content": content}

@router.delete("/content/{content_id}")
async def delete_content(content_id: str):
    if email_generator.delete_content(content_id):
        return {"success": True}
    raise HTTPException(status_code=404, detail="Content not found")

@router.get("/templates")
async def get_templates():
    return {"templates": email_generator.get_builtin_templates()}


# === Recipient Lists ===

@router.get("/lists")
async def get_all_lists():
    return {"lists": recipient_manager.get_all_lists()}

@router.post("/lists/upload")
async def upload_list(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: str = Form(""),
    email_column: str = Form("email"),
    delimiter: str = Form(",")
):
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    result = recipient_manager.upload_list(temp_path, name, description, email_column, delimiter)
    os.remove(temp_path)
    return result

@router.post("/lists/manual")
async def create_list_manual(request: ManualListRequest):
    result = recipient_manager.create_list_manual(request.name, request.emails, request.description)
    return result

@router.get("/lists/{list_id}")
async def get_list(list_id: str):
    lst = recipient_manager.get_list(list_id)
    if not lst:
        raise HTTPException(status_code=404, detail="List not found")
    return {"list": lst}

@router.get("/lists/{list_id}/recipients")
async def get_recipients(list_id: str, limit: int = 100, offset: int = 0):
    result = recipient_manager.get_recipients(list_id, limit, offset)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@router.delete("/lists/{list_id}")
async def delete_list(list_id: str):
    if recipient_manager.delete_list(list_id):
        return {"success": True}
    raise HTTPException(status_code=404, detail="List not found")

@router.get("/lists/stats")
async def get_lists_stats():
    return {"stats": recipient_manager.get_stats()}


# === Stats ===

@router.get("/stats")
async def get_ses_stats():
    return {
        "keys_count": len(ses_service.get_all_keys()),
        "contents_count": len(email_generator.get_all_contents()),
        "lists_count": len(recipient_manager.get_all_lists()),
        "total_recipients": sum(l.get("valid_count", 0) for l in recipient_manager.get_all_lists())
    }
