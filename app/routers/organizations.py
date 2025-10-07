from fastapi import APIRouter, HTTPException
from typing import List
from ..models import Organization, OrganizationCreate, OrganizationUpdate
from .. import storage1 as storage

router = APIRouter()

@router.get("", response_model=List[Organization])
def list_organizations():
    return storage.list_orgs()

@router.post("", response_model=Organization, status_code=201)
def create_organization(org: OrganizationCreate):
    return storage.create_org(org.dict())

@router.get("/{orgId}", response_model=Organization)
def get_organization(orgId: str):
    org = storage.get_org(orgId)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org

@router.put("/{orgId}", response_model=Organization)
def update_organization(orgId: str, org: OrganizationUpdate):
    updated = storage.update_org(orgId, org.dict())
    if not updated:
        raise HTTPException(status_code=404, detail="Organization not found")
    return updated

@router.delete("/{orgId}", status_code=204)
def delete_organization(orgId: str):
    deleted = storage.delete_org(orgId)
    if not deleted:
        raise HTTPException(status_code=404, detail="Organization not found")
    return {}