"""
Service logic for Analytics Dashboard endpoints.
Aggregates in-memory data from other service modules to produce personal/team dashboards,
trends, heatmaps, and performance metrics. Returns demo analytics suitable for UI.

Classes:
    - AnalyticsDashboardDTO
    - AnalyticsTeamDashboardDTO
    - AnalyticsTrendsDTO
    - AnalyticsHeatmapDTO
    - AnalyticsPerformanceDTO
    - AnalyticsService (handles aggregation)
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
import random

from .gamification_service import GamificationService
from .bug_service import BugService

# For team demo, simulated mapping
TEAM_MEMBERS: Dict[str, List[str]] = {
    "team-red": ["alice", "bob", "clare"],
    "team-blue": ["dave", "eve", "fred"],
    "team-green": ["gina", "hank"],
}


# --- DTOs ---


# PUBLIC_INTERFACE
class AnalyticsDashboardDTO(BaseModel):
    """Personal dashboard metrics for user."""
    user_id: str
    points: int
    level: Optional[str]
    rank: Optional[str]
    badges: int
    achievements: int
    prs_reviewed: int
    bugs_logged: int
    bugs_fixed: int
    bug_severity_breakdown: Dict[str, int]
    last_active: Optional[datetime]


# PUBLIC_INTERFACE
class AnalyticsTeamDashboardDTO(BaseModel):
    """Team dashboard, with aggregates and comparisons."""
    team_id: str
    member_count: int
    total_points: int
    avg_points: float
    top_members: List[Dict[str, Any]]
    total_bugs: int
    bugs_per_member: float
    bug_severity_breakdown: Dict[str, int]
    last_active: Optional[datetime]


# PUBLIC_INTERFACE
class AnalyticsTrendsDTO(BaseModel):
    """Trendlines for PR activity, bugs, etc. for user/team."""
    labels: List[str]  # Dates or periods
    pr_counts: List[int]
    bug_counts: List[int]
    points_earned: List[int]


# PUBLIC_INTERFACE
class AnalyticsHeatmapDTO(BaseModel):
    """Calendar heatmap data (PR or review frequency)."""
    data: Dict[str, int]  # ISO date str -> activity count


# PUBLIC_INTERFACE
class AnalyticsPerformanceDTO(BaseModel):
    """Performance and leaderboard stats."""
    leaderboards: List[Dict[str, Any]]
    avg_review_time_hrs: float
    avg_bug_fix_time_hrs: float
    total_reviews: int
    total_bugs_fixed: int
    bug_fix_rate: float


# --- SERVICE ---


# PUBLIC_INTERFACE
class AnalyticsService:
    """
    Aggregates data from gamification, bug, and (future) PR services for dashboard endpoints.
    """

    def __init__(self):
        self._gamification = GamificationService()
        self._bug = BugService()

    # PUBLIC_INTERFACE
    def get_personal_dashboard(self, user_id: str) -> AnalyticsDashboardDTO:
        """Returns metrics for the user's dashboard."""
        points = self._gamification.get_points_balance(user_id)
        levelobj = self._gamification.get_level(user_id)
        badges = len(self._gamification.list_badges(user_id))
        achievements = len(self._gamification.list_achievements(user_id))
        # Demo: PRs reviewed = bugs found + random for demo; bugs fixed = random
        bugs_logged = sum(
            1 for bugs in self._bug._bugs_by_pr.values()
            for b in bugs if b.logged_by == user_id
        )
        bugs_fixed = random.randint(0, bugs_logged)
        severity = {}
        for bugs in self._bug._bugs_by_pr.values():
            for b in bugs:
                if b.logged_by == user_id:
                    k = b.severity.value
                    severity[k] = severity.get(k, 0) + 1
        # Recent activity: pick a random date in last 7 days for demo
        last_active = datetime.utcnow() - timedelta(days=random.randint(0, 6))

        return AnalyticsDashboardDTO(
            user_id=user_id,
            points=points,
            level=str(levelobj.level) if levelobj else None,
            rank=levelobj.rank.value if levelobj else None,
            badges=badges,
            achievements=achievements,
            prs_reviewed=bugs_logged + random.randint(0, 3),
            bugs_logged=bugs_logged,
            bugs_fixed=bugs_fixed,
            bug_severity_breakdown=severity,
            last_active=last_active,
        )

    # PUBLIC_INTERFACE
    def get_team_dashboard(self, team_id: str) -> AnalyticsTeamDashboardDTO:
        """Aggregate dashboard for a team."""
        member_ids = TEAM_MEMBERS.get(team_id, [])
        total_points = 0
        points_list = []
        last_acts = []
        total_bugs = 0
        bug_severity = {}
        for uid in member_ids:
            pts = self._gamification.get_points_balance(uid)
            total_points += pts
            points_list.append(pts)
            # last_active = demo random date
            last_acts.append(datetime.utcnow() - timedelta(days=random.randint(0, 6)))
            user_bugs = sum(
                1 for bugs in self._bug._bugs_by_pr.values()
                for b in bugs if b.logged_by == uid
            )
            total_bugs += user_bugs
            for bugs in self._bug._bugs_by_pr.values():
                for b in bugs:
                    if b.logged_by == uid:
                        k = b.severity.value
                        bug_severity[k] = bug_severity.get(k, 0) + 1

        avg_points = (sum(points_list) / len(points_list)) if points_list else 0
        bugs_per_member = (total_bugs / len(member_ids)) if member_ids else 0
        last_active = max(last_acts) if last_acts else None
        top_members = [
            {"user_id": uid, "points": self._gamification.get_points_balance(uid)}
            for uid in member_ids
        ]
        top_members.sort(key=lambda x: -x["points"])
        return AnalyticsTeamDashboardDTO(
            team_id=team_id,
            member_count=len(member_ids),
            total_points=total_points,
            avg_points=avg_points,
            top_members=top_members[:3],
            total_bugs=total_bugs,
            bugs_per_member=bugs_per_member,
            bug_severity_breakdown=bug_severity,
            last_active=last_active,
        )

    # PUBLIC_INTERFACE
    def get_trends(
        self, user_id: Optional[str] = None, team_id: Optional[str] = None
    ) -> AnalyticsTrendsDTO:
        """Returns trendlines for PR activity, bugs, and points over past 14 days."""
        now = datetime.utcnow().date()
        labels = [(now - timedelta(days=i)).isoformat() for i in reversed(range(14))]
        pr_counts = [random.randint(0, 3) for _ in labels]
        bug_counts = [random.randint(0, 2) for _ in labels]
        points_earned = [random.randint(0, 25) for _ in labels]
        return AnalyticsTrendsDTO(
            labels=labels,
            pr_counts=pr_counts,
            bug_counts=bug_counts,
            points_earned=points_earned,
        )

    # PUBLIC_INTERFACE
    def get_heatmap(
        self, user_id: Optional[str] = None, team_id: Optional[str] = None
    ) -> AnalyticsHeatmapDTO:
        """Returns calendar heatmap data for the past 60 days."""
        today = datetime.utcnow().date()
        data = {}
        rng = random.Random(user_id or team_id or 0)  # Deterministic demo
        for day in range(60):
            dt = today - timedelta(days=day)
            # Higher activity on recent weekdays for demo
            value = rng.randint(0, 3) if dt.weekday() < 5 else rng.randint(0, 2)
            data[dt.isoformat()] = value
        return AnalyticsHeatmapDTO(data=data)

    # PUBLIC_INTERFACE
    def get_performance(
        self, user_id: Optional[str] = None, team_id: Optional[str] = None
    ) -> AnalyticsPerformanceDTO:
        """Performance stats or leaderboards for user or team."""
        leaderboards = []
        all_user_ids = (
            sum(TEAM_MEMBERS.values(), [])
            if team_id is not None
            else [user_id] if user_id else []
        )
        members_iter = TEAM_MEMBERS.get(team_id, []) if team_id else all_user_ids
        for uid in members_iter:
            pts = self._gamification.get_points_balance(uid)
            bugs = sum(
                1 for bugs in self._bug._bugs_by_pr.values()
                for b in bugs if b.logged_by == uid
            )
            leaderboards.append({
                "user_id": uid,
                "points": pts,
                "bugs_logged": bugs,
                "level": (
                    self._gamification.get_level(uid).rank.value
                    if self._gamification.get_level(uid) else None
                )
            })
        if not leaderboards and user_id:
            pts = self._gamification.get_points_balance(user_id)
            leaderboards.append({
                "user_id": user_id,
                "points": pts,
                "bugs_logged": 0,
                "level": (
                    self._gamification.get_level(user_id).rank.value
                    if self._gamification.get_level(user_id) else None
                )
            })
        # Demo stats
        avg_review_time = random.uniform(2, 8)
        avg_bug_fix_time = random.uniform(6, 36)
        total_reviews = sum(entry["bugs_logged"] for entry in leaderboards)
        total_bugs_fixed = total_reviews - random.randint(0, total_reviews)
        bug_fix_rate = (
            total_bugs_fixed / total_reviews if total_reviews else 0.0
        )
        return AnalyticsPerformanceDTO(
            leaderboards=sorted(leaderboards, key=lambda x: -x["points"]),
            avg_review_time_hrs=avg_review_time,
            avg_bug_fix_time_hrs=avg_bug_fix_time,
            total_reviews=total_reviews,
            total_bugs_fixed=total_bugs_fixed,
            bug_fix_rate=bug_fix_rate,
        )
