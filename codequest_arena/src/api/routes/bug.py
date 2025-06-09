"""
FastAPI router for Bug Logging & Peer Review.

Handles:
- Logging a bug during PR review (with category, severity, description)
- Listing bugs for a PR (repo/pr pair)
- Get/update/delete a specific bug
- Instant visibility logic (bugs are instantly visible to PR authors)
"""

from fastapi import APIRouter, HTTPException, status, Body
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from ..services.bug_service import (
    BugDTO,
    BugService,
    BugSeverity,
    BugCategory,
    BugStatus,
    DisputeDTO,
    VoteDTO,
    VoteChoice,
)

router = APIRouter()
bug_service = BugService()


# Pydantic Request Models for Dispute API

class DisputeOpenRequest(BaseModel):
    opened_by: str = Field(..., description="User initiating the dispute (usually PR author)")
    reason: Optional[str] = Field(
        None, description="Why is this bug being disputed?"
    )


class VoteRequest(BaseModel):
    voter: str = Field(..., description="Voter username or ID")
    choice: VoteChoice = Field(
        ...,
        description=(
            "'ACCEPT' (vote upholds bug), "
            "'REJECT' (vote agrees with dispute and bug should be dismissed)"
        ),
    )


class DisputeResolveRequest(BaseModel):
    resolved_by: str = Field(..., description="User closing the dispute (peer or admin)")
    as_admin: Optional[bool] = Field(
        False, description="If true, do admin override"
    )
    accept: Optional[bool] = Field(
        None, description="If admin override: True to accept/keep bug, False to reject bug"
    )
    notes: Optional[str] = Field(
        None, description="Optional resolution notes or justification"
    )


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


# ----- DISPUTE RESOLUTION WORKFLOW ENDPOINTS -----

# PUBLIC_INTERFACE
@router.post(
    "/bugs/{bug_id}/dispute",
    response_model=DisputeDTO,
    tags=["Dispute Resolution Workflow"],
    status_code=status.HTTP_201_CREATED
)
def open_dispute(bug_id: str, req: DisputeOpenRequest):
    """
    Open a dispute on a logged bug (usually by PR author).
    Only one open dispute is allowed per bug.
    """
    try:
        dispute = bug_service.open_dispute(bug_id, req.opened_by, req.reason)
        return dispute
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# PUBLIC_INTERFACE
@router.get(
    "/bugs/{bug_id}/disputes",
    response_model=List[DisputeDTO],
    tags=["Dispute Resolution Workflow"],
)
def list_disputes_for_bug(bug_id: str):
    """
    List all disputes (open and closed) for this bug.
    """
    return bug_service.list_disputes_for_bug(bug_id)


# PUBLIC_INTERFACE
@router.get(
    "/disputes/{dispute_id}",
    response_model=DisputeDTO,
    tags=["Dispute Resolution Workflow"],
)
def get_dispute(dispute_id: str):
    """
    Get the details of a single dispute (including votes).
    """
    d = bug_service.get_dispute(dispute_id)
    if not d:
        raise HTTPException(status_code=404, detail="Dispute not found")
    return d


# PUBLIC_INTERFACE
@router.post(
    "/disputes/{dispute_id}/vote",
    response_model=VoteDTO,
    tags=["Dispute Resolution Workflow"],
    status_code=status.HTTP_201_CREATED
)
def vote_on_dispute(
    dispute_id: str,
    req: VoteRequest
):
    """
    Cast a peer vote on an open dispute.
    """
    try:
        return bug_service.cast_vote(dispute_id, req.voter, req.choice)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# PUBLIC_INTERFACE
@router.get(
    "/disputes/{dispute_id}/votes",
    response_model=List[VoteDTO],
    tags=["Dispute Resolution Workflow"],
)
def list_votes_for_dispute(dispute_id: str):
    """
    List all votes cast for a given dispute.
    """
    return bug_service.list_votes_for_dispute(dispute_id)


# PUBLIC_INTERFACE
@router.post(
    "/disputes/{dispute_id}/resolve",
    response_model=DisputeDTO,
    tags=["Dispute Resolution Workflow"],
)
def resolve_dispute(
    dispute_id: str,
    req: DisputeResolveRequest = Body(...)
):
    """
    Resolve a dispute either via peer voting or admin override.
    If as_admin is true, perform admin override; otherwise finalize by peer votes.
    """
    try:
        if req.as_admin:
            if req.accept is None:
                raise HTTPException(
                    status_code=400,
                    detail="Must specify 'accept' for admin resolution"
                )
            return bug_service.admin_override_dispute(
                dispute_id, req.resolved_by, req.accept, req.notes
            )
        else:
            return bug_service.close_dispute_peer(
                dispute_id, req.resolved_by, req.notes
            )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
