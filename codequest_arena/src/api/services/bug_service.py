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
class DisputeStatus(str, Enum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"
    ADMIN_OVERRIDE = "ADMIN_OVERRIDE"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


# PUBLIC_INTERFACE
class VoteChoice(str, Enum):
    ACCEPT = "ACCEPT"      # Voter agrees with the bug as valid
    REJECT = "REJECT"      # Voter sides with the dispute, i.e., bug is INVALID


# PUBLIC_INTERFACE
class VoteDTO(BaseModel):
    vote_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    dispute_id: str
    voter: str  # username or id
    choice: VoteChoice
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

    class Config:
        schema_extra = {
            "example": {
                "vote_id": "uuid-string",
                "dispute_id": "dispute-uuid-string",
                "voter": "peer-reviewer",
                "choice": "REJECT",
                "created_at": "2023-01-01T12:34:56Z"
            }
        }


# PUBLIC_INTERFACE
class DisputeDTO(BaseModel):
    dispute_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    bug_id: str  # Which bug is being disputed
    opened_by: str  # Who started the dispute (typically PR author)
    reason: Optional[str]
    status: DisputeStatus = DisputeStatus.OPEN
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    resolved_at: Optional[datetime.datetime] = None
    resolved_by: Optional[str] = None  # username or id, peer or admin
    resolution_notes: Optional[str] = None
    result: Optional[VoteChoice] = None  # Final outcome ACCEPT/REJECT
    votes: Optional[List[VoteDTO]] = None  # Votes for this dispute

    class Config:
        schema_extra = {
            "example": {
                "dispute_id": "uuid-string",
                "bug_id": "bug-uuid-string",
                "opened_by": "pr-author",
                "reason": "I believe this bug is not valid.",
                "status": "OPEN",
                "created_at": "2023-01-01T14:00:00Z",
                "result": None,
                "votes": []
            }
        }


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
    Service for bug logging & peer review and dispute resolution workflow.
    NOTE: In-memory storage for demonstration; swap with DB for production.
    """
    _lock = threading.Lock()
    _bugs_by_pr: Dict[str, List[BugDTO]] = {}
    _disputes_by_bug: Dict[str, List[DisputeDTO]] = {}
    _dispute_by_id: Dict[str, DisputeDTO] = {}
    _votes_by_dispute: Dict[str, List[VoteDTO]] = {}

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

    # PUBLIC_INTERFACE
    def open_dispute(
        self, bug_id: str, opened_by: str, reason: Optional[str] = None
    ) -> DisputeDTO:
        """
        Open a new dispute for a bug. Returns the created DisputeDTO.
        Only one active (OPEN) dispute allowed at a time per bug.
        """
        with self._lock:
            bug = self.get_bug(bug_id)
            if not bug:
                raise ValueError("Bug not found")
            existing_open = [
                d for d in self._disputes_by_bug.get(bug_id, [])
                if d.status == DisputeStatus.OPEN
            ]
            if existing_open:
                raise ValueError("A dispute is already open for this bug")
            dispute = DisputeDTO(
                bug_id=bug_id,
                opened_by=opened_by,
                reason=reason,
                status=DisputeStatus.OPEN,
                votes=[],
            )
            dispute_list = self._disputes_by_bug.setdefault(bug_id, [])
            dispute_list.append(dispute)
            self._dispute_by_id[dispute.dispute_id] = dispute
            self._votes_by_dispute[dispute.dispute_id] = []
            return dispute

    # PUBLIC_INTERFACE
    def list_disputes_for_bug(self, bug_id: str) -> List[DisputeDTO]:
        """List all disputes for a bug (open and resolved)."""
        with self._lock:
            return list(self._disputes_by_bug.get(bug_id, []))

    # PUBLIC_INTERFACE
    def get_dispute(self, dispute_id: str) -> Optional[DisputeDTO]:
        """Get a dispute by its ID."""
        with self._lock:
            dispute = self._dispute_by_id.get(dispute_id)
            if dispute:
                dispute.votes = list(
                    self._votes_by_dispute.get(dispute_id, [])
                )
            return dispute

    # PUBLIC_INTERFACE
    def cast_vote(self, dispute_id: str, voter: str, choice: VoteChoice) -> VoteDTO:
        """
        Cast a peer review vote (ACCEPT/REJECT) on an open dispute.
        Each voter may only vote once per dispute.
        """
        with self._lock:
            dispute = self._dispute_by_id.get(dispute_id)
            if not dispute or dispute.status != DisputeStatus.OPEN:
                raise ValueError("Dispute not found or not open")
            votes = self._votes_by_dispute.get(dispute_id, [])
            if any(v.voter == voter for v in votes):
                raise ValueError("Voter has already voted on this dispute")
            vote = VoteDTO(
                dispute_id=dispute_id,
                voter=voter,
                choice=choice,
            )
            votes.append(vote)
            self._votes_by_dispute[dispute_id] = votes
            dispute.votes = list(votes)
            return vote

    # PUBLIC_INTERFACE
    def close_dispute_peer(
        self, dispute_id: str, resolved_by: str, notes: Optional[str] = None
    ) -> DisputeDTO:
        """
        Peer-based resolution: finalize dispute based on current vote tally.
        Sets result (ACCEPT if majority of votes are ACCEPT, else REJECT).
        """
        with self._lock:
            dispute = self._dispute_by_id.get(dispute_id)
            if not dispute or dispute.status != DisputeStatus.OPEN:
                raise ValueError("Dispute not found or not open")
            votes = self._votes_by_dispute.get(dispute_id, [])
            accept = sum(
                1 for v in votes if v.choice == VoteChoice.ACCEPT
            )
            reject = sum(
                1 for v in votes if v.choice == VoteChoice.REJECT
            )
            if accept == 0 and reject == 0:
                raise ValueError("No votes cast yet")
            result = (
                VoteChoice.ACCEPT if accept > reject else VoteChoice.REJECT
            )
            dispute.status = DisputeStatus.RESOLVED
            dispute.resolved_at = datetime.datetime.utcnow()
            dispute.result = result
            dispute.resolved_by = resolved_by
            dispute.resolution_notes = notes
            dispute.votes = list(votes)
            return dispute

    # PUBLIC_INTERFACE
    def admin_override_dispute(
        self, dispute_id: str, admin: str, accept: bool, notes: Optional[str] = None
    ) -> DisputeDTO:
        """
        Admin resolves dispute regardless of votes. If accept=True, result is ACCEPT (bug is valid);
        else REJECT (dispute succeeds, bug is rejected).
        """
        with self._lock:
            dispute = self._dispute_by_id.get(dispute_id)
            if not dispute or dispute.status != DisputeStatus.OPEN:
                raise ValueError("Dispute not found or not open")
            result = VoteChoice.ACCEPT if accept else VoteChoice.REJECT
            dispute.status = DisputeStatus.ADMIN_OVERRIDE
            dispute.resolved_at = datetime.datetime.utcnow()
            dispute.resolved_by = admin
            dispute.resolution_notes = notes
            dispute.result = result
            dispute.votes = list(
                self._votes_by_dispute.get(dispute_id, [])
            )
            return dispute

    # PUBLIC_INTERFACE
    def list_votes_for_dispute(self, dispute_id: str) -> List[VoteDTO]:
        """List all votes for a dispute (peer voting)."""
        with self._lock:
            return list(self._votes_by_dispute.get(dispute_id, []))
