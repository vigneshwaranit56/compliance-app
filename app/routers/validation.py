from fastapi import APIRouter, Query
from typing import List, Optional
from ..models import ValidationRecord
from .. import storage1 as storage

router = APIRouter()

@router.get("/history", response_model=List[ValidationRecord])
def validation_history(project: Optional[str] = Query(None, description="Project name to filter")):
    return storage.list_validations(project)