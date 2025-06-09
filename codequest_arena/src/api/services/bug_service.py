"""
Service logic for Bug Logging & Peer Review.

Handles:
- Logging bugs in PRs during reviews
- Categorization, severity, and status tracking
- Instant visibility for PR authors
- Basic in-memory storage (thread-safe for demonstration)

Classes:
    - BugSeverity: Enum for bug severity levels
    - BugCategory: Enum for bug category/tags
    - BugStatus: Enum for bug status
    - BugDTO: Data transfer object for bug
    - BugService: Service class for bugs/peer review operations
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import threading
import uuid
import datetime


# PUBLIC_INTERFACE
class BugSeverity(str, Enum):
    MINOR = "MINOR"
    MAJOR = "MAJOR"
    CRITICAL = "CRITICAL"


# PUBLIC_INTERFACE
class BugCategory(str, Enum):
    FUNCTIONAL = "FUNCTIONAL"
    UI = "UI"
    PERFORMANCE = "PERFORMANCE"
    SECURITY = "SECURITY"
    DOCUMENTATION = "DOCUMENTATION"
    OTHER = "OTHER"


# PUBLIC_INTERFACE
class BugStatus(str, Enum):
    LOGGED = "LOGGED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    FIXED = "FIXED"
    REJECTED = "REJECTED"


# PUBLIC_INTERFACE
class BugDTO(BaseModel):
    """Data transfer object for a logged bug in PR."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    repo_id: str
    pr_id: str
    logged_by: str  # username or ID
    title: str
    description: Optional[str]
    severity: BugSeverity
    category: BugCategory
    instant_visible: bool = True  # For now always visible
    status: BugStatus = BugStatus.LOGGED
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    updated_at: Optional[datetime.datetime] = None

    class Config:
        schema_extra = {
            "example": {
                "id": "uuid-string",
                "repo_id": "github-repo-1",
                "pr_id": "github-repo-1-pr-2",
                "logged_by": "reviewer-name",
                "title": "Missing null check",
                "description": "Function X does not handle None type.",
                "severity": "MAJOR",
                "category": "FUNCTIONAL",
                "instant_visible": True,
                "status": "LOGGED",
                "created_at": "2023-01-01T12:00:00Z",
                "updated_at": None
            }
        }


# PUBLIC_INTERFACE
class BugService:
    """
    Service for bug logging & peer review.
    NOTE: In-memory storage for demonstration; swap with DB for production.
    """
    _lock = threading.Lock()
    # Indexed as (repo_id, pr_id) -> List[BugDTO]
    _bugs_by_pr: Dict[str, List[BugDTO]] = {}

    def _make_pr_key(self, repo_id: str, pr_id: str) -> str:
        return f"{repo_id}::{pr_id}"

    # PUBLIC_INTERFACE
    def log_bug(self, bug: BugDTO) -> BugDTO:
        """Log a new bug and make it instantly visible to PR author."""
        key = self._make_pr_key(bug.repo_id, bug.pr_id)
        with self._lock:
            if key not in self._bugs_by_pr:
                self._bugs_by_pr[key] = []
            self._bugs_by_pr[key].append(bug)
        return bug

    # PUBLIC_INTERFACE
    def list_bugs(self, repo_id: str, pr_id: str) -> List[BugDTO]:
        """List all bugs logged for this PR."""
        key = self._make_pr_key(repo_id, pr_id)
        with self._lock:
            return list(self._bugs_by_pr.get(key, []))

    # PUBLIC_INTERFACE
    def get_bug(self, bug_id: str) -> Optional[BugDTO]:
        """Get a bug by its ID (linear scan)."""
        with self._lock:
            for bug_list in self._bugs_by_pr.values():
                for bug in bug_list:
                    if bug.id == bug_id:
                        return bug
        return None

    # PUBLIC_INTERFACE
    def update_bug(self, bug_id: str, data: Dict[str, Any]) -> Optional[BugDTO]:
        """Update a bug (status, description, etc)."""
        with self._lock:
            for bug_list in self._bugs_by_pr.values():
                for idx, bug in enumerate(bug_list):
                    if bug.id == bug_id:
                        updated_bug = bug.copy(
                            update={**data, "updated_at": datetime.datetime.utcnow()},
                            deep=True,
                        )
                        bug_list[idx] = updated_bug
                        return updated_bug
        return None

    # PUBLIC_INTERFACE
    def delete_bug(self, bug_id: str) -> bool:
        """Delete a bug by its ID."""
        with self._lock:
            for key, bug_list in self._bugs_by_pr.items():
                for idx, bug in enumerate(bug_list):
                    if bug.id == bug_id:
                        del bug_list[idx]
                        return True
        return False
