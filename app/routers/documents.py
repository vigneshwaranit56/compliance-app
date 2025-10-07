from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Optional
from ..models import ComplianceDocument, ComplianceDocumentUpload
from .. import storage1 as storage
from uuid import uuid4
from datetime import datetime


router = APIRouter()

@router.get("", response_model=List[ComplianceDocument])
def list_documents(orgId: str):
    return storage.list_documents(orgId)


@router.post("", response_model=ComplianceDocument, status_code=201)
async def upload_document(
    orgId: str,
    name: str = Form(...),
    description: Optional[str] = Form(None),
    version: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    file: Optional[UploadFile] = File(None)
):
    # if storage.get_org(orgId) is None:
    #     raise HTTPException(status_code=404, detail="Organization not found")


    doc_id = str(uuid4())
    d = ComplianceDocument(
        id=doc_id,
        orgId=orgId,
        name=name,
        description=description,
        date=datetime.today(),
        version=version,
        status="Uploaded"
    )
    storage.add_document(orgId, d.dict())
    return d
