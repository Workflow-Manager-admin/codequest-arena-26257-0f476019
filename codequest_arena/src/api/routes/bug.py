"""
FastAPI router for Bug Logging & Peer Review.

Handles:
- Logging a bug during PR review (with category, severity, description)
- Listing bugs for a PR (repo/pr pair)
- Get/update/delete a specific bug
- Instant visibility logic (bugs are instantly visible to PR authors)
"""

from fastapi import APIRouter, HTTPException, status, Body
from typing import List, Dict, Any

from ..services.bug_service import (
    BugDTO,
    BugService,
    BugSeverity,
    BugCategory,
    BugStatus,
)

router = APIRouter()
bug_service = BugService()


# PUBLIC_INTERFACE
@router.post(
    "/repositories/{repo_id}/prs/{pr_id}/bugs",
    response_model=BugDTO,
    status_code=status.HTTP_201_CREATED,
    tags=["Bug Logging & Peer Review"],
)
def log_bug(
    repo_id: str,
    pr_id: str,
    bug: BugDTO,
):
    """
    Log a new bug for a given PR.
    - Instantly visible to PR author
    - Requires title, category, severity, and description
    """
    # Override repo_id, pr_id just in case user tampered
    bug.repo_id = repo_id
    bug.pr_id = pr_id
    result = bug_service.log_bug(bug)
    return result


# PUBLIC_INTERFACE
@router.get(
    "/repositories/{repo_id}/prs/{pr_id}/bugs",
    response_model=List[BugDTO],
    tags=["Bug Logging & Peer Review"],
)
def list_bugs(
    repo_id: str,
    pr_id: str,
):
    """
    List all bugs for a given PR (for authors & reviewers).
    """
    return bug_service.list_bugs(repo_id, pr_id)


# PUBLIC_INTERFACE
@router.get(
    "/bugs/{bug_id}",
    response_model=BugDTO,
    tags=["Bug Logging & Peer Review"],
)
def get_bug(
    bug_id: str,
):
    """
    Get a specific logged bug by ID.
    """
    bug = bug_service.get_bug(bug_id)
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")
    return bug


# PUBLIC_INTERFACE
@router.put(
    "/bugs/{bug_id}",
    response_model=BugDTO,
    tags=["Bug Logging & Peer Review"],
)
def update_bug(
    bug_id: str,
    data: Dict[str, Any] = Body(...),
):
    """
    Update bug fields (status, description, etc).
    Authors/reviewers may use this for triage workflow.
    """
    updated_bug = bug_service.update_bug(bug_id, data)
    if not updated_bug:
        raise HTTPException(status_code=404, detail="Bug not found")
    return updated_bug


# PUBLIC_INTERFACE
@router.delete(
    "/bugs/{bug_id}",
    tags=["Bug Logging & Peer Review"],
)
def delete_bug(
    bug_id: str,
):
    """
    Delete a bug (admin/mod only unless extended with auth).
    """
    ok = bug_service.delete_bug(bug_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Bug not found")
    return {"success": True}


# PUBLIC_INTERFACE
@router.get(
    "/bug-severities",
    response_model=List[str],
    tags=["Bug Logging & Peer Review"]
)
def list_bug_severities():
    """
    List possible bug severities (for UI dropdowns).
    """
    # Use list to avoid returning Enum objects
    return [s.value for s in BugSeverity]


# PUBLIC_INTERFACE
@router.get(
    "/bug-categories",
    response_model=List[str],
    tags=["Bug Logging & Peer Review"]
)
def list_bug_categories():
    """
    List possible bug categories (for UI dropdowns).
    """
    return [c.value for c in BugCategory]


# PUBLIC_INTERFACE
@router.get(
    "/bug-statuses",
    response_model=List[str],
    tags=["Bug Logging & Peer Review"]
)
def list_bug_statuses():
    """
    List possible bug statuses.
    """
    return [s.value for s in BugStatus]
