"""
FastAPI router for PR Integration & Repository Management.

Handles:
- Connecting/authorizing with GitHub, GitLab, or Bitbucket.
- Fetching and displaying user repositories.
- Listing pull requests for repositories.
- (Stub) Further repo management endpoints.

Endpoints here are stubs and should be linked to real services or API integrations.

Extend as needed for OAuth/token management, scheduled import, etc.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from ..services.pr_service import (
    GitProvider,
    PRService,
    RepositoryDTO,
    PullRequestDTO,
)


router = APIRouter()

# Service instance (would be DI-managed or cached in production)
pr_service = PRService()


# PUBLIC_INTERFACE
@router.get("/providers", tags=["PR Integration"])
def list_supported_providers() -> List[str]:
    """
    Returns a list of supported git providers (GitHub, GitLab, Bitbucket).
    """
    return [provider.value for provider in GitProvider]


# PUBLIC_INTERFACE
@router.get("/connect", tags=["PR Integration"])
def connect_to_provider(
    provider: GitProvider,
    redirect_uri: Optional[str] = None,
):
    """
    Stub endpoint to initiate OAuth/connection with a git provider.
    Returns the (fake) authorization URL or connection status.
    """
    # TODO: Implement full OAuth, just simulate here.
    base_url = f"https://fake-oauth.{provider.value}.com/auth"
    rd_uri = redirect_uri or 'urn:localhost'
    return {
        "provider": provider.value,
        "auth_url": f"{base_url}?redirect_uri={rd_uri}",
        "message": (
            "Use this URL to authenticate and connect your account (stub)."
        ),
    }


# PUBLIC_INTERFACE
@router.get(
    "/repositories",
    response_model=List[RepositoryDTO],
    tags=["PR Integration"]
)
def list_repositories(
    provider: GitProvider,
    user_token: str = Query(..., description="OAuth token for demo purposes"),
):
    """
    Lists repositories accessible by the authenticated user on the specified provider.
    """
    return pr_service.list_repositories(provider, user_token)


# PUBLIC_INTERFACE
@router.get(
    "/repositories/{repo_id}/prs",
    response_model=List[PullRequestDTO],
    tags=["PR Integration"]
)
def list_pull_requests(
    provider: GitProvider,
    repo_id: str,
    user_token: str = Query(..., description="OAuth token for demo purposes"),
):
    """
    Lists pull requests for a repository.
    """
    return pr_service.list_pull_requests(provider, repo_id, user_token)


# PUBLIC_INTERFACE
@router.get(
    "/repositories/{repo_id}/prs/{pr_id}",
    response_model=PullRequestDTO,
    tags=["PR Integration"]
)
def get_pull_request(
    provider: GitProvider,
    repo_id: str,
    pr_id: str,
    user_token: str = Query(..., description="OAuth token for demo purposes"),
):
    """
    Retrieve metadata on a specific pull request.
    """
    pr = pr_service.get_pull_request(provider, repo_id, pr_id, user_token)
    if pr is None:
        raise HTTPException(
            status_code=404,
            detail="PR not found"
        )
    return pr
