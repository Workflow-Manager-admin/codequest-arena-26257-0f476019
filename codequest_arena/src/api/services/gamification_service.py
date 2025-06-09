"""
Gamification Engine Service: points, badges, levels, and achievements logic for CodeQuest Arena.

Provides in-memory, thread-safe APIs for awarding, tracking, and managing gamification attributes.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import threading
import uuid
import datetime


# --- ENUMS ---


# PUBLIC_INTERFACE
class PointsReason(str, Enum):
    BUG_LOGGED = "BUG_LOGGED"
    BUG_FIXED = "BUG_FIXED"
    REVIEW_COMPLETED = "REVIEW_COMPLETED"
    BUG_DISPUTE_WON = "BUG_DISPUTE_WON"
    CUSTOM = "CUSTOM"


# PUBLIC_INTERFACE
class BadgeType(str, Enum):
    FAST_REVIEWER = "FAST_REVIEWER"
    BUG_HUNTER = "BUG_HUNTER"
    PEER_MENTOR = "PEER_MENTOR"
    LEVEL_MASTER = "LEVEL_MASTER"
    CUSTOM = "CUSTOM"


# PUBLIC_INTERFACE
class AchievementType(str, Enum):
    FIRST_BUG = "FIRST_BUG"
    TEN_BUGS = "TEN_BUGS"
    FLAWLESS_PR = "FLAWLESS_PR"
    COMMUNITY_CHAMP = "COMMUNITY_CHAMP"
    CUSTOM = "CUSTOM"


# PUBLIC_INTERFACE
class LevelRank(str, Enum):
    NOVICE = "NOVICE"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    EXPERT = "EXPERT"
    LEGEND = "LEGEND"


# --- DTOs (MODELS) ---


# PUBLIC_INTERFACE
class PointsTransactionDTO(BaseModel):
    transaction_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    points: int
    reason: PointsReason
    meta: Optional[Dict[str, Any]] = None
    awarded_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


# PUBLIC_INTERFACE
class BadgeDTO(BaseModel):
    badge_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    type: BadgeType
    awarded_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    meta: Optional[Dict[str, Any]] = None


# PUBLIC_INTERFACE
class LevelDTO(BaseModel):
    user_id: str
    level: int
    rank: LevelRank
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    next_level_points: Optional[int] = None


# PUBLIC_INTERFACE
class AchievementDTO(BaseModel):
    achievement_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    type: AchievementType
    awarded_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    meta: Optional[Dict[str, Any]] = None


# --- SERVICE ---


# PUBLIC_INTERFACE
class GamificationService:
    """
    Service for managing points, badges, levels, and achievements for users (in-memory/thread-safe).
    """

    _lock = threading.Lock()
    _points_by_user: Dict[str, List[PointsTransactionDTO]] = {}
    _badges_by_user: Dict[str, List[BadgeDTO]] = {}
    _levels_by_user: Dict[str, LevelDTO] = {}
    _achievements_by_user: Dict[str, List[AchievementDTO]] = {}

    # --- Points ---

    # PUBLIC_INTERFACE
    def award_points(
        self,
        user_id: str,
        points: int,
        reason: PointsReason,
        meta: Optional[Dict[str, Any]] = None
    ) -> PointsTransactionDTO:
        """Award points to a user with a transaction reason."""
        tx = PointsTransactionDTO(user_id=user_id, points=points, reason=reason, meta=meta)
        with self._lock:
            self._points_by_user.setdefault(user_id, []).append(tx)
        return tx

    # PUBLIC_INTERFACE
    def get_points_balance(self, user_id: str) -> int:
        """Return total points balance for a user."""
        with self._lock:
            return sum(tx.points for tx in self._points_by_user.get(user_id, []))

    # PUBLIC_INTERFACE
    def list_points_transactions(self, user_id: str) -> List[PointsTransactionDTO]:
        """List all point transactions for a given user."""
        with self._lock:
            return list(self._points_by_user.get(user_id, []))

    # --- Badges ---

    # PUBLIC_INTERFACE
    def award_badge(
        self,
        user_id: str,
        badge_type: BadgeType,
        meta: Optional[Dict[str, Any]] = None
    ) -> BadgeDTO:
        """Award a badge of a specific type to a user."""
        badge = BadgeDTO(user_id=user_id, type=badge_type, meta=meta)
        with self._lock:
            self._badges_by_user.setdefault(user_id, []).append(badge)
        return badge

    # PUBLIC_INTERFACE
    def list_badges(self, user_id: str) -> List[BadgeDTO]:
        """List all badges earned by a user."""
        with self._lock:
            return list(self._badges_by_user.get(user_id, []))

    # --- Levels ---
    _LEVEL_THRESHOLDS = [
        (0, LevelRank.NOVICE),
        (100, LevelRank.INTERMEDIATE),
        (300, LevelRank.ADVANCED),
        (600, LevelRank.EXPERT),
        (1000, LevelRank.LEGEND),
    ]

    # PUBLIC_INTERFACE
    def update_level(self, user_id: str):
        """
        Computes and updates the user's level based on points.
        Called after awarding points.
        """
        balance = self.get_points_balance(user_id)
        current_level = 0
        current_rank = LevelRank.NOVICE
        next_pts = None
        for pts, rank in self._LEVEL_THRESHOLDS:
            if balance >= pts:
                current_rank = rank
                current_level += 1
            else:
                next_pts = pts
                break
        dto = LevelDTO(
            user_id=user_id,
            level=current_level,
            rank=current_rank,
            next_level_points=next_pts
        )
        with self._lock:
            self._levels_by_user[user_id] = dto
        return dto

    # PUBLIC_INTERFACE
    def get_level(self, user_id: str) -> Optional[LevelDTO]:
        """Get the user's level/rank and points needed for next level."""
        with self._lock:
            return self._levels_by_user.get(user_id)

    # --- Achievements ---

    # PUBLIC_INTERFACE
    def award_achievement(
        self,
        user_id: str,
        achievement_type: AchievementType,
        meta: Optional[Dict[str, Any]] = None
    ) -> AchievementDTO:
        """Award a new achievement to a user."""
        achievement = AchievementDTO(user_id=user_id, type=achievement_type, meta=meta)
        with self._lock:
            self._achievements_by_user.setdefault(user_id, []).append(achievement)
        return achievement

    # PUBLIC_INTERFACE
    def list_achievements(self, user_id: str) -> List[AchievementDTO]:
        """List all achievements unlocked by user."""
        with self._lock:
            return list(self._achievements_by_user.get(user_id, []))

    # --- Admin / Reset ---

    # PUBLIC_INTERFACE
    def reset_user(self, user_id: str) -> bool:
        """Reset all gamification data for a user."""
        with self._lock:
            self._points_by_user.pop(user_id, None)
            self._badges_by_user.pop(user_id, None)
            self._levels_by_user.pop(user_id, None)
            self._achievements_by_user.pop(user_id, None)
        return True

    # PUBLIC_INTERFACE
    def list_all_users(self) -> List[str]:
        """List all user IDs with gamification records."""
        with self._lock:
            all_users = (
                set(self._points_by_user.keys())
                | set(self._badges_by_user.keys())
                | set(self._levels_by_user.keys())
                | set(self._achievements_by_user.keys())
            )
        return list(all_users)
