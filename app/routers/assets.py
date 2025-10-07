from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
from .. import storage1 as storage
from ..models import ValidationRecord, ComplianceDocumentUpload
from uuid import uuid4
from datetime import date
import json

router = APIRouter()



@router.post("/{projectName}", status_code=201)
async def create_project_and_upload(
    projectName: str,
    orgId: str = Form(..., description="Organization ID"),
    files: List[UploadFile] = File(...),
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

    for f in files:
        rec = ValidationRecord(
            orgId=orgId,
            assetName=f.filename,
            type="file",
            status="Pending",
            lastChecked=None,
            nextCheck=None,
            complianceDocuments=[],
            validationMode=validationMode,
            monitoringEnabled=monitoringEnabled,
            links=links,
            guardrails=guardrails_models
        )
        storage.create_validation(projectName, rec.dict())

    return {
        "message": "Uploaded",
        "project": projectName,
        "fileCount": len(files)
    }

