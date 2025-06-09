"""
FastAPI router for Analytics Dashboard (personal/team dashboards, trends, heatmaps, metrics).

Handles:
- /analytics/dashboard: Personal dashboard metrics (PRs reviewed, bugs found, points, badges, etc.)
- /analytics/team-dashboard: Team-level aggregates (team performance, bug fix rate, top reviewers)
- /analytics/trends: Activity trends (bug/PR trends over time)
- /analytics/heatmap: Contribution/activity heatmap (calendar-style per-user or team)
- /analytics/performance: Performance metrics (review speed, team stats, etc.)

Returns mock/demo data with proper structure for now; replace with real DB aggregates in production.
"""

from fastapi import APIRouter, Query
from typing import Optional

from ..services.analytics_service import (
    AnalyticsDashboardDTO,
    AnalyticsTrendsDTO,
    AnalyticsHeatmapDTO,
    AnalyticsPerformanceDTO,
    AnalyticsTeamDashboardDTO,
    AnalyticsService,
)

router = APIRouter()
service = AnalyticsService()


# PUBLIC_INTERFACE
@router.get("/dashboard", response_model=AnalyticsDashboardDTO, tags=["Analytics"])
def personal_dashboard(user_id: str = Query(...)):
    """
    Returns user's personal analytics dashboard: PRs reviewed, bugs found, points, badges, etc.
    """
    return service.get_personal_dashboard(user_id)


# PUBLIC_INTERFACE
@router.get("/team-dashboard", response_model=AnalyticsTeamDashboardDTO, tags=["Analytics"])
def team_dashboard(team_id: str = Query(...)):
    """
    Returns analytics dashboard for a team: aggregate metrics and comparisons.
    """
    return service.get_team_dashboard(team_id)


# PUBLIC_INTERFACE
@router.get("/trends", response_model=AnalyticsTrendsDTO, tags=["Analytics"])
def activity_trends(user_id: Optional[str] = None, team_id: Optional[str] = None):
    """
    Returns trends for PRs, bugs, points earned, reviews over time (user and/or team).
    """
    return service.get_trends(user_id=user_id, team_id=team_id)


# PUBLIC_INTERFACE
@router.get("/heatmap", response_model=AnalyticsHeatmapDTO, tags=["Analytics"])
def activity_heatmap(user_id: Optional[str] = None, team_id: Optional[str] = None):
    """
    Returns activity heatmap data for UI calendar view.
    """
    return service.get_heatmap(user_id=user_id, team_id=team_id)


# PUBLIC_INTERFACE
@router.get("/performance", response_model=AnalyticsPerformanceDTO, tags=["Analytics"])
def performance_metrics(user_id: Optional[str] = None, team_id: Optional[str] = None):
    """
    Returns performance metrics such as review speed, bug fix/close rates, leaderboards, etc.
    """
    return service.get_performance(user_id=user_id, team_id=team_id)
