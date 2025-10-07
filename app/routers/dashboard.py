import logging
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from ..models import DashboardResponse, OrgDashboardResponse
from .. import storage1 as storage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# @router.get("/dashboard", response_model=DashboardResponse)
# def get_dashboard(
#     org_id:
#     search: Optional[str] = Query(None, description="Search term for filtering"),
#     status: Optional[str] = Query(None, description="Filter by status"),
#     document: Optional[str] = Query(None, description="Filter by document"),
#     page: int = Query(1, description="Page number"),
#     pageSize: int = Query(20, description="Number of records per page")
# ):
#     orgs = storage.list_orgs()
#     total_docs = sum(len(storage.list_documents(o["id"])) for o in orgs)
#     all_validations = storage.list_validations()

#     # Filter validations based on query parameters
#     if status:
#         all_validations = [v for v in all_validations if v.get("status") == status]
#     if document:
#         all_validations = [v for v in all_validations if document in v.get("complianceDocuments", [])]

#     # Pagination logic
#     start = (page - 1) * pageSize
#     end = start + pageSize
#     paginated_validations = all_validations[start:end]

#     response = {
#         "totalAssets": total_docs,
#         "compliant": sum(1 for v in all_validations if v.get("status") == "Compliant"),
#         "violations": sum(1 for v in all_validations if v.get("status") == "Violations"),
#         "pending": sum(1 for v in all_validations if v.get("status") == "Pending"),
#         "page": page,
#         "pageSize": pageSize,
#         "totalRecords": len(all_validations),
#         "validationHistory": paginated_validations
#     }

#     # Log the response
#     logger.info("Dashboard response: %s", response)

#     return response
@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(
    orgId: str = Query(..., description="Organization ID"),
    search: Optional[str] = Query(None, description="Search term for filtering"),
    status: Optional[str] = Query(None, description="Filter by status"),
    document: Optional[str] = Query(None, description="Filter by document"),
    page: int = Query(1, description="Page number"),
    pageSize: int = Query(20, description="Number of records per page")
):
    org = storage.get_org(orgId)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    docs = storage.list_documents(orgId)
    total_docs = len(docs)
    all_validations = storage.list_validations(orgId)

    # Filter validations based on query parameters
    if status:
        all_validations = [v for v in all_validations if v.get("status") == status]
    if document:
        all_validations = [v for v in all_validations if document in v.get("complianceDocuments", [])]
    if search:
        all_validations = [
            v for v in all_validations
            if search.lower() in str(v).lower()
        ]

    # Pagination logic
    start = (page - 1) * pageSize
    end = start + pageSize
    paginated_validations = all_validations[start:end]

    response = {
        "totalAssets": total_docs,
        "compliant": sum(1 for v in all_validations if v.get("status") == "Compliant"),
        "violations": sum(1 for v in all_validations if v.get("status") == "Violations"),
        "pending": sum(1 for v in all_validations if v.get("status") == "Pending"),
        "page": page,
        "pageSize": pageSize,
        "totalRecords": len(all_validations),
        "validationHistory": paginated_validations
    }

    logger.info("Dashboard response: %s", response)
    return response

@router.get("/organizations/{orgId}/dashboard", response_model=OrgDashboardResponse)
def get_org_dashboard(orgId: str):
    org = storage.get_org(orgId)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    docs = storage.list_documents(orgId)
    vals = []
    # Fetch all validations for this org from MongoDB
    all_validations = storage.list_validations(orgId)
    doc_ids = {d.get("id") for d in docs}
    for v in all_validations:
        # v["complianceDocuments"] could be a list of document IDs or objects
        compliance_docs = v.get("complianceDocuments", [])
        # If compliance_docs is a list of dicts, extract their IDs
        if compliance_docs and isinstance(compliance_docs[0], dict):
            compliance_doc_ids = {doc.get("id") for doc in compliance_docs}
        else:
            compliance_doc_ids = set(compliance_docs)
        if doc_ids & compliance_doc_ids:
            vals.append(v)
    return OrgDashboardResponse(organizationId=orgId, documents=docs, validations=vals)
# @router.get("/organizations/{orgId}/dashboard", response_model=OrgDashboardResponse)
# def get_org_dashboard(orgId: str):
#     org = storage.get_org(orgId)
#     if not org:
#         raise HTTPException(status_code=404, detail="Organization not found")
#     docs = storage.list_documents(orgId)
#     vals = []
#     for project, recs in storage.VALIDATIONS.items():
#         for r in recs:
#             if r.get("complianceDocuments"):
#                 for d in docs:
#                     if d.get("id") in r.get("complianceDocuments", []):
#                         vals.append(r)
#                         break
#     return OrgDashboardResponse(organizationId=orgId, documents=docs, validations=vals)
