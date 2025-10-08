from typing import Dict, List
from uuid import uuid4
from .models import Organization, ComplianceDocument, ValidationRecord

ORGS = {}
DOCUMENTS = {}  # orgId -> list of documents
VALIDATIONS = {}  # projectName -> list of ValidationRecord

def create_org(data: dict):
    org_id = str(uuid4())
    org = Organization(id=org_id, **data)
    ORGS[org_id] = org.dict()
    DOCUMENTS[org_id] = []
    return ORGS[org_id]

def list_orgs():
    return list(ORGS.values())

def get_org(org_id):
    return ORGS.get(org_id)

def update_org(org_id, data: dict):
    if org_id in ORGS:
        ORGS[org_id].update({k:v for k,v in data.items() if v is not None})
        return ORGS[org_id]
    return None

def delete_org(org_id):
    return ORGS.pop(org_id, None)

def add_document(org_id, doc: dict):
    DOCUMENTS.setdefault(org_id, []).append(doc)
    return doc

def list_documents(org_id):
    return DOCUMENTS.get(org_id, [])

def create_validation(project_name, record: dict):
    VALIDATIONS.setdefault(project_name, []).append(record)
    return record

def list_validations(org_id=None):
    # Filter validations by orgId
    filtered_validations = []
    for project_name, records in VALIDATIONS.items():
        for record in records:
            if record.get('orgId') == org_id:
                filtered_validations.append(record)
    
    return filtered_validations
