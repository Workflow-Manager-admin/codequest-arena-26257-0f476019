"""
FastAPI router for Rule Engine.

Handles:
- CRUD endpoints for managing rules and policies
- Admin-configurable API for code quality/static analysis/process policy rules

Extend to connect with persistent backend in production.
"""
from fastapi import APIRouter, HTTPException, status
from typing import List

from ..services.rule_engine_service import (
    RuleDTO,
    RuleEngineService,
)


router = APIRouter()
rule_service = RuleEngineService()


# PUBLIC_INTERFACE
@router.get("/rules", response_model=List[RuleDTO], tags=["Rule Engine"])
def list_rules():
    """
    List all code quality/static analysis/process policy rules.
    """
    return rule_service.list_rules()


# PUBLIC_INTERFACE
@router.get("/rules/{rule_id}", response_model=RuleDTO, tags=["Rule Engine"])
def get_rule(rule_id: str):
    """
    Retrieve a rule by id.
    """
    rule = rule_service.get_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


# PUBLIC_INTERFACE
@router.post(
    "/rules",
    response_model=RuleDTO,
    status_code=status.HTTP_201_CREATED,
    tags=["Rule Engine"],
)
def create_rule(rule: RuleDTO):
    """
    Create a new rule.
    """
    created = rule_service.create_rule(rule)
    return created


# PUBLIC_INTERFACE
@router.put("/rules/{rule_id}", response_model=RuleDTO, tags=["Rule Engine"])
def update_rule(rule_id: str, rule_data: dict):
    """
    Update a rule by id.
    """
    updated = rule_service.update_rule(rule_id, rule_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Rule not found")
    return updated


# PUBLIC_INTERFACE
@router.delete("/rules/{rule_id}", tags=["Rule Engine"])
def delete_rule(rule_id: str):
    """
    Delete a rule by id.
    """
    deleted = rule_service.delete_rule(rule_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"success": True}
