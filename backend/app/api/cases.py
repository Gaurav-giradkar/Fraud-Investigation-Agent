from typing import List
from fastapi import APIRouter, HTTPException, status
from app.models.case import CasePackItem
from app.services.case_service import case_service

router = APIRouter(prefix="/cases", tags=["cases"])

@router.get("", response_model=List[CasePackItem])
async def get_all_cases():
    """Retrieve all 20 benchmark cases from case_pack.csv."""
    return case_service.get_all_cases()

@router.get("/{case_id}", response_model=CasePackItem)
async def get_case_by_id(case_id: str):
    """Retrieve a specific benchmark case by case_id (e.g. HHG-001)."""
    case_item = case_service.get_case_by_id(case_id)
    if not case_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case with ID '{case_id}' not found."
        )
    return case_item
