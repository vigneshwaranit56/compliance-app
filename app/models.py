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
    file: Optional[bytes]


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
    lastChecked: Optional[datetime]
    nextCheck: Optional[datetime] 
    complianceDocuments: List[ComplianceDocumentUpload]
    validationMode: str
    monitoringEnabled: bool
    links: List[str]
    guardrails: List[ComplianceDocumentUpload]
    file: Optional[bytes]


class OrganizationBase(BaseModel):
    name: Optional[str]
    industry: Optional[str]
    complianceOfficer: Optional[str]
    lastAudit: Optional[datetime]

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(BaseModel):
    name: Optional[str]
    industry: Optional[str]
    complianceOfficer: Optional[str]
    lastAudit: Optional[datetime]

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