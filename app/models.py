from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date

class ComplianceDocument(BaseModel):
    id: Optional[str]
    orgId: str
    name: Optional[str]
    description: Optional[str]
    date: Optional[datetime]
    status: Optional[str]
    version: Optional[str]


class ComplianceDocumentUpload(BaseModel):
    id: int
    title: str
    version: str
    status: str

class ValidationRecord(BaseModel):
    orgId: str
    assetName: str
    type: str
    status: str
    lastChecked: Optional[str] = None
    nextCheck: Optional[str] = None
    complianceDocuments: List[ComplianceDocumentUpload]
    validationMode: str
    monitoringEnabled: bool
    links: List[str]
    guardrails: List[ComplianceDocumentUpload]

class OrganizationBase(BaseModel):
    name: str
    address: Optional[str]

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(BaseModel):
    name: Optional[str]
    address: Optional[str]

class Organization(OrganizationBase):
    id: str


class DashboardResponse(BaseModel):
    totalAssets: int
    compliant: int
    violations: int
    pending: int
    page: int
    pageSize: int
    totalRecords: int
    validationHistory: List[ValidationRecord]

class OrgDashboardResponse(BaseModel):
    organizationId: str
    documents: List[ComplianceDocument] = []
    validations: List[ValidationRecord] = []