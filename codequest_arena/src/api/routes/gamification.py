"""
FastAPI router for Gamification Engine.

Handles:
- User endpoints to track, list, and get their own points, badges, levels, achievements
- Admin endpoints to award, reset, or list all users' gamification status

TODO: Hook up to real auth for restricting admin endpoints.
"""

from fastapi import APIRouter
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from ..services.gamification_service import (
    PointsReason,
    PointsTransactionDTO,
    BadgeType,
    BadgeDTO,
    LevelDTO,
    LevelRank,
    AchievementType,
    AchievementDTO,
    GamificationService
)

router = APIRouter()
service = GamificationService()


# ---- USER ENDPOINTS ----


# PUBLIC_INTERFACE
@router.get("/users/{user_id}/points", response_model=int, tags=["Gamification Engine"])
def get_points_balance(user_id: str):
    """Returns total points balance for a user."""
    return service.get_points_balance(user_id)


# PUBLIC_INTERFACE
@router.get(
    "/users/{user_id}/points/history",
    response_model=List[PointsTransactionDTO],
    tags=[
        "Gamification Engine"
    ]
)
def list_points_transactions(user_id: str):
    """Lists all points transactions for a user."""
    return service.list_points_transactions(user_id)


# PUBLIC_INTERFACE
@router.get("/users/{user_id}/badges", response_model=List[BadgeDTO], tags=["Gamification Engine"])
def list_badges(user_id: str):
    """Lists all badges earned by a user."""
    return service.list_badges(user_id)


# PUBLIC_INTERFACE
@router.get("/users/{user_id}/level", response_model=Optional[LevelDTO], tags=["Gamification Engine"])
def get_level(user_id: str):
    """Returns the user's level/rank."""
    return service.get_level(user_id)


# PUBLIC_INTERFACE
@router.get(
    "/users/{user_id}/achievements",
    response_model=List[AchievementDTO],
    tags=[
        "Gamification Engine"
    ]
)
def list_achievements(user_id: str):
    """Lists all achievements unlocked by user."""
    return service.list_achievements(user_id)


# ---- ADMIN/AWARD ENDPOINTS ----


class AwardPointsRequest(BaseModel):
    user_id: str
    points: int
    reason: PointsReason = PointsReason.CUSTOM
    meta: Optional[Dict[str, Any]] = None


class AwardBadgeRequest(BaseModel):
    user_id: str
    type: BadgeType = BadgeType.CUSTOM
    meta: Optional[Dict[str, Any]] = None


class AwardAchievementRequest(BaseModel):
    user_id: str
    type: AchievementType = AchievementType.CUSTOM
    meta: Optional[Dict[str, Any]] = None


# PUBLIC_INTERFACE
@router.post("/admin/award/points", response_model=PointsTransactionDTO, tags=["Gamification Engine"])
def admin_award_points(req: AwardPointsRequest):
    """ADMIN: Award points to a user for a reason."""
    tx = service.award_points(req.user_id, req.points, req.reason, meta=req.meta)
    service.update_level(req.user_id)
    return tx


# PUBLIC_INTERFACE
@router.post("/admin/award/badge", response_model=BadgeDTO, tags=["Gamification Engine"])
def admin_award_badge(req: AwardBadgeRequest):
    """ADMIN: Award a badge to a user."""
    return service.award_badge(req.user_id, req.type, req.meta)


# PUBLIC_INTERFACE
@router.post(
    "/admin/award/achievement",
    response_model=AchievementDTO,
    tags=[
        "Gamification Engine"
    ]
)
def admin_award_achievement(req: AwardAchievementRequest):
    """ADMIN: Award an achievement to a user."""
    return service.award_achievement(req.user_id, req.type, req.meta)


# PUBLIC_INTERFACE
@router.post("/admin/level/recompute/{user_id}", response_model=LevelDTO, tags=["Gamification Engine"])
def admin_recompute_level(user_id: str):
    """ADMIN: Force recompute user's level/rank based on current points."""
    return service.update_level(user_id)


# PUBLIC_INTERFACE
@router.post("/admin/reset/{user_id}", tags=["Gamification Engine"])
def admin_reset_user(user_id: str):
    """ADMIN: Reset all gamification progress for a user."""
    service.reset_user(user_id)
    return {"success": True}


# PUBLIC_INTERFACE
@router.get("/admin/list-users", response_model=List[str], tags=["Gamification Engine"])
def admin_list_all_users():
    """ADMIN: List all users with gamification activity."""
    return service.list_all_users()


# ---- ENUM REFERENCE ENDPOINTS ----


@router.get("/meta/points-reasons", response_model=List[str], tags=["Gamification Engine"])
def list_points_reasons():
    """List all possible points reasons."""
    return [r.value for r in PointsReason]


@router.get("/meta/badge-types", response_model=List[str], tags=["Gamification Engine"])
def list_badge_types():
    """List all possible badge types."""
    return [b.value for b in BadgeType]


@router.get("/meta/level-ranks", response_model=List[str], tags=["Gamification Engine"])
def list_level_ranks():
    """List all possible level ranks."""
    return [rank.value for rank in LevelRank]


@router.get("/meta/achievement-types", response_model=List[str], tags=["Gamification Engine"])
def list_achievement_types():
    """List all possible achievement types."""
    return [a.value for a in AchievementType]
