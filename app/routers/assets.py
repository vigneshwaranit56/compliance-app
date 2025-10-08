
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Optional
from .. import storage1 as storage
from ..smart_compliance import validate_file
from ..models import ValidationRecord, ComplianceDocumentUpload
from uuid import uuid4
from datetime import datetime
import json
import base64
import os

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
    # Retrieve the document by guardrails ID
    document = storage.get_document_by_id(guardrails)
    status= "success"

    # Check if the document exists
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Extract and decode file bytes from the document
    compliance_file_base64 = document.get('file')
    if not compliance_file_base64:
        raise HTTPException(status_code=400, detail="Compliance file data is missing")

    compliance_file_bytes = base64.b64decode(compliance_file_base64)

    lastChecked = datetime.now()
    file_bytes = await file.read() if file else None
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file data is missing")

    encoded_file = base64.b64encode(file_bytes).decode("utf-8")

    try:
        # Define temporary file paths
        compliance_file_path = "/tmp/compliance_file.csv"
        input_file_path = "/tmp/input_file.csv"

        # Write bytes to temporary files
        with open(compliance_file_path, "wb") as f:
            f.write(compliance_file_bytes)
        with open(input_file_path, "wb") as f:
            f.write(file_bytes)

        # Call the validate_file function
        validation_results_json = validate_file(compliance_file_path, input_file_path)
        validation_results_dict = json.loads(validation_results_json)  # Parse JSON string to dict
        # validation_results = list(validation_results_dict.values())  # Convert dict to list

    except Exception as e:
        status="failed"
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

    finally:
        # Clean up temporary files
        if os.path.exists(compliance_file_path):
            os.remove(compliance_file_path)
        if os.path.exists(input_file_path):
            os.remove(input_file_path)


    rec = ValidationRecord(
        orgId=orgId,
        assetName=file.filename,
        type="file",
        status=status,
        lastChecked=lastChecked,
        nextCheck=None,
        complianceDocuments=guardrails,
        validationResults=validation_results_dict,
        validationMode=validationMode,
        monitoringEnabled=monitoringEnabled,
        links=links,
        file=encoded_file
    )
    storage.create_validation(projectName, rec.dict())

    return {
        "message": "Uploaded",
        "project": projectName,
    }
# from fastapi import APIRouter, UploadFile, File, Form, HTTPException
# from typing import List, Optional
# from .. import storage1 as storage
# from ..smart_compliance import validate_file
# from ..models import ValidationRecord
# from uuid import uuid4
# from datetime import datetime
# import json
# import base64
# import os

# router = APIRouter()

# @router.post("/{projectName}", status_code=201)
# async def create_project_and_upload(
#     projectName: str,
#     orgId: str = Form(..., description="Organization ID"),
#     file: Optional[UploadFile] = File(...),
#     validationMode: str = Form(..., description="Validation mode"),
#     monitoringEnabled: bool = Form(False, description="Monitoring enabled"),
#     links: List[str] = Form(["www.google.com"], description="Links associated with the project"),
#     guardrails: str = Form(..., description="Guardrails for validation (JSON string)")
# ):
#    # Retrieve the document by guardrails ID
#     document = storage.get_document_by_id(guardrails)

#     # Check if the document exists
#     if not document:
#         raise HTTPException(status_code=404, detail="Document not found")

#     # Extract and decode file bytes from the document
#     compliance_file_base64 = document.get('file')
#     if not compliance_file_base64:
#         raise HTTPException(status_code=400, detail="Compliance file data is missing")

#     compliance_file_bytes = base64.b64decode(compliance_file_base64)


#     lastChecked = datetime.now()
#     file_bytes = await file.read() if file else None
#     if not file_bytes:
#         raise HTTPException(status_code=400, detail="Uploaded file data is missing")

#     encoded_file = base64.b64encode(file_bytes).decode("utf-8")

#     try:
#         # Define temporary file paths
#         compliance_file_path = "/tmp/compliance_file.csv"
#         input_file_path = "/tmp/input_file.csv"

#         # Write bytes to temporary files
#         with open(compliance_file_path, "wb") as f:
#             f.write(compliance_file_bytes)
#         with open(input_file_path, "wb") as f:
#             f.write(file_bytes)

#               # Call the validate_file function
#         validation_results_json = validate_file(compliance_file_path, input_file_path)
#         validation_results = json.loads(validation_results_json)  # Parse JSON string to dict
#         # validation_results = list(validation_results_dict.values())  # Convert dict to list

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

#     finally:
#         # Clean up temporary files
#         if os.path.exists(compliance_file_path):
#             os.remove(compliance_file_path)
#         if os.path.exists(input_file_path):
#             os.remove(input_file_path)

#     rec = ValidationRecord(
#         orgId=orgId,
#         assetName=file.filename,
#         type="file",
#         status="Pending",
#         lastChecked=lastChecked,
#         nextCheck=None,
#         complianceDocuments=document,
#         validationResults=validation_results,
#         validationMode=validationMode,
#         monitoringEnabled=monitoringEnabled,
#         links=links,
#         guardrails=guardrails,
#         file=encoded_file
#     )
#     storage.create_validation(projectName, rec.dict())

#     return {
#         "message": "Uploaded",
#         "project": projectName,
#     }


# version 1


# from fastapi import APIRouter, UploadFile, File, Form, HTTPException
# from typing import List, Optional
# from .. import storage1 as storage
# from ..smart_compliance import validate_file
# from ..models import ValidationRecord, ComplianceDocumentUpload
# from uuid import uuid4
# from datetime import datetime
# import json
# import base64

# router = APIRouter()



# @router.post("/{projectName}", status_code=201)
# async def create_project_and_upload(
#     projectName: str,
#     orgId: str = Form(..., description="Organization ID"),
#     file: Optional[UploadFile] = File(...),
#     validationMode: str = Form(..., description="Validation mode"),
#     monitoringEnabled: bool = Form(False, description="Monitoring enabled"),
#     links: List[str] = Form(["www.google.com"], description="Links associated with the project"),
#     guardrails: str = Form(..., description="Guardrails for validation (JSON string)")
# ):
#     document = get_document_by_id(guardrails)

#     # Check if the document exists
#     if not document:
#         raise HTTPException(status_code=404, detail="Document not found")

#     # Extract file bytes from the document
#     compliance_file_bytes = document.get('file')

#     lastChecked = datetime.now()
#     file_bytes = await file.read() if file else None
#     encoded_file = base64.b64encode(file_bytes).decode("utf-8") if file_bytes else None

#     # compliance_analysis_json = validate_file(compliance_file_path="", input_file_path="")

#     try:
        

#         # Define temporary file paths
#         compliance_file_path = "/tmp/compliance_file.csv"
#         input_file_path = "/tmp/input_file.csv"

#         # Write bytes to temporary files
#         with open(compliance_file_path, "wb") as f:
#             f.write(compliance_file_bytes)
#         with open(input_file_path, "wb") as f:
#             f.write(file_bytes)

#         # Call the validate_file function
#         validation_results = validate_file(compliance_file_path, input_file_path)

#         # Clean up temporary files
#         os.remove(compliance_file_path)
#         os.remove(input_file_path)

#         # return {"validation_results": validation_results}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
#     rec = ValidationRecord(
#         orgId=orgId,
#         assetName=file.filename,
#         type="file",
#         status="Pending",
#         lastChecked=lastChecked,
#         nextCheck=None,
#         complianceDocuments=validation_results,
#         validationMode=validationMode,
#         monitoringEnabled=monitoringEnabled,
#         links=links,
#         guardrails=guardrails_models,
#         file=encoded_file
#     )
#     storage.create_validation(projectName, rec.dict())

#     return {
#         "message": "Uploaded",
#         "project": projectName,
#     }

