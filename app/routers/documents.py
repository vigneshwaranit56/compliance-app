from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Optional
from ..models import ComplianceDocument, ComplianceDocumentUpload
from .. import storage1 as storage
from uuid import uuid4
from datetime import datetime
import base64


router = APIRouter()

@router.get("", response_model=List[ComplianceDocument])
def list_documents(orgId: str):
    documents = storage.list_documents_skip_file(orgId)
    for doc in documents:
        doc['file'] = None  # Set 'file' to None if it is not included in the response
    return documents


@router.post("", response_model=ComplianceDocument, status_code=201)
async def upload_document(
    orgId: str,
    name: str = Form(...),
    description: Optional[str] = Form(None),
    version: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    file: Optional[UploadFile] = File(None)
):
    if storage.get_org(orgId) is None:
        raise HTTPException(status_code=404, detail="Organization not found")

    file_bytes = await file.read() if file else None
    encoded_file = base64.b64encode(file_bytes).decode("utf-8") if file_bytes else None

    doc_id = str(uuid4())
    d = ComplianceDocument(
        id=doc_id,
        orgId=orgId,
        name=name,
        description=description,
        date=datetime.today(),
        version=version,
        status="Uploaded",
        file= encoded_file
    )

    storage.add_document(orgId, d.dict())
    return d
