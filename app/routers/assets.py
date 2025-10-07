from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Optional
from .. import storage1 as storage
from ..models import ValidationRecord, ComplianceDocumentUpload
from uuid import uuid4
from datetime import datetime
import json
import base64

router = APIRouter()



@router.post("/{projectName}", status_code=201)
async def create_project_and_upload(
    projectName: str,
    orgId: str = Form(..., description="Organization ID"),
    file: Optional[UploadFile] = File(...),
    validationMode: str = Form(..., description="Validation mode"),
    monitoringEnabled: bool = Form(False, description="Monitoring enabled"),
    links: List[str] = Form(["www.google.com"], description="Links associated with the project"),
    guardrails: str = Form(..., description="Guardrails for validation (JSON string)")
):
    try:
        if not guardrails.strip():
            raise ValueError("Guardrails input is empty")

        print("Raw guardrails input:", guardrails)  # Optional: for debugging

        guardrails_data = json.loads(guardrails)

        if not isinstance(guardrails_data, list):
            raise ValueError("Guardrails should be a JSON array")

        guardrails_models = [ComplianceDocumentUpload(**doc) for doc in guardrails_data]

    except Exception as e:
        return {
            "error": "Invalid guardrails format",
            "details": str(e)
        }
    lastChecked = datetime.now()
    file_bytes = await file.read() if file else None
    encoded_file = base64.b64encode(file_bytes).decode("utf-8") if file_bytes else None


    
    rec = ValidationRecord(
        orgId=orgId,
        assetName=file.filename,
        type="file",
        status="Pending",
        lastChecked=lastChecked,
        nextCheck=None,
        complianceDocuments=[],
        validationMode=validationMode,
        monitoringEnabled=monitoringEnabled,
        links=links,
        guardrails=guardrails_models,
        file=encoded_file
    )
    storage.create_validation(projectName, rec.dict())

    return {
        "message": "Uploaded",
        "project": projectName,
    }

