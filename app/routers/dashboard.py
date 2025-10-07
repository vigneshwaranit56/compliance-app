import logging
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from ..models import DashboardResponse, OrgDashboardResponse
from .. import storage1 as storage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


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

@router.get("/organizations/{orgId}/dashboard")
def get_dashboard_data(orgId):
    # Fetch documents for the organization
    docs = storage.list_documents(orgId)
    total_documents = len(docs)

    # Fetch all validations for this organization
    all_validations = storage.list_validations(orgId)
    total_validations = len(all_validations)

    # Fetch organization details
    organization_details = storage.get_org(orgId)  # Assuming this method exists

    # Extract compliance information from documents
    compliance_info = docs

    # Calculate active users (assuming a method exists to fetch this data)
    active_users = 4  # Placeholder for actual logic to fetch active users

        # Extract last checked date from validations
    valid_dates = [v.get("lastChecked") for v in all_validations if v.get("lastChecked")]
    last_updated = max(valid_dates) if valid_dates else None

    return {
        "utilizationMetrics": {
            "totalDocuments": total_documents,
            "activeUsers": active_users,
            "totalValidations": total_validations,
            "lastUpdated": last_updated
        },
        "organizationDetails": {
            "orgName": organization_details.get("name", "N/A"),  # CHANGE: Use .get() to safely access dictionary keys
            "industry": organization_details.get("industry", "N/A"),  # CHANGE: Provide default value
            "complianceOfficer": organization_details.get("complianceOfficer", "N/A"),  # CHANGE: Provide default value
            "lastAudit": organization_details.get("lastAudit", "N/A"),  # CHANGE: Provide default value
            "complianceFrameworks": compliance_info if compliance_info else []  # CHANGE: Ensure compliance_info is a list
        }
    }

