"""
Service logic for PR Integration & Repository Management.

Handles:
- Listing supported providers
- Listing repositories for the user
- Listing/retrieving pull requests for a repository

Stubbed for now, to be connected with real git APIs in the future.

Classes:
    - GitProvider: Enum of supported git providers
    - RepositoryDTO: DTO for a repository
    - PullRequestDTO: DTO for a pull request
    - PRService: Service class for PR/repo operations
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

# PUBLIC_INTERFACE
class GitProvider(str, Enum):
    github = "github"
    gitlab = "gitlab"
    bitbucket = "bitbucket"


# PUBLIC_INTERFACE


class RepositoryDTO(BaseModel):
    """Minimal repo data for listing."""
    id: str
    name: str
    description: Optional[str]
    provider: GitProvider
    url: str


# PUBLIC_INTERFACE
class PullRequestDTO(BaseModel):
    """Minimal PR data for listing/details."""
    id: str
    title: str
    author: str
    status: str
    url: str
    repository_id: str
    provider: GitProvider


# PUBLIC_INTERFACE
class PRService:
    """
    Service logic for repositories and PRs.
    Replace with real git API integration in production.
    """

    # PUBLIC_INTERFACE
    def list_repositories(
        self, provider: GitProvider, user_token: str
    ) -> List[RepositoryDTO]:
        """
        Returns a (mock) list of repositories for a user given a git provider and token.
        """
        # Simulated test data for all providers
        return [
            RepositoryDTO(
                id=f"{provider}-repo-1",
                name=f"Sample Repo 1 ({provider.value.title()})",
                description="A sample repo",
                provider=provider,
                url=f"https://{provider.value}.com/user/repo-1",
            ),
            RepositoryDTO(
                id=f"{provider}-repo-2",
                name=f"Sample Repo 2 ({provider.value.title()})",
                description="Another repo",
                provider=provider,
                url=f"https://{provider.value}.com/user/repo-2",
            ),
        ]

    # PUBLIC_INTERFACE
    def list_pull_requests(
        self, provider: GitProvider, repo_id: str, user_token: str
    ) -> List[PullRequestDTO]:
        """
        Returns a (mock) list of pull requests for a given repo.
        """
        # Simulated PRs per repo
        return [
            PullRequestDTO(
                id=f"{repo_id}-pr-1",
                title="Fix bug in main.py",
                author="alice",
                status="open",
                url=f"https://{provider.value}.com/pr/1",
                repository_id=repo_id,
                provider=provider,
            ),
            PullRequestDTO(
                id=f"{repo_id}-pr-2",
                title="Improve docs of feature X",
                author="bob",
                status="closed",
                url=f"https://{provider.value}.com/pr/2",
                repository_id=repo_id,
                provider=provider,
            ),
        ]

    # PUBLIC_INTERFACE
    def get_pull_request(
        self, provider: GitProvider, repo_id: str, pr_id: str, user_token: str
    ) -> Optional[PullRequestDTO]:
        """
        Returns details for a single PR (mock).
        """
        prs = self.list_pull_requests(provider, repo_id, user_token)
        for pr in prs:
            if pr.id == pr_id:
                return pr
        return None
