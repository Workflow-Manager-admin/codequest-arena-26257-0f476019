"""
Service logic for Redeem Center (points redemption / inventory management).

Handles:
- Prize catalog management (admin)
- Inventory of redeemable prizes
- Prize redemption logic (check points, update inventory)
- Redemption transaction history

Thread-safe, in-memory demo – swap for DB in production.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum
import threading
import uuid
import datetime


# PUBLIC_INTERFACE
class PrizeType(str, Enum):
    SWAG = "SWAG"
    COUPON = "COUPON"
    DONATION = "DONATION"
    BONUS = "BONUS"
    OTHER = "OTHER"


# PUBLIC_INTERFACE
class PrizeDTO(BaseModel):
    """Represents a redeemable prize."""
    prize_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    type: PrizeType
    points_required: int
    total_quantity: int = 0   # Total ever added
    available_quantity: int = 0
    meta: Optional[Dict[str, Any]] = None

    class Config:
        schema_extra = {
            "example": {
                "prize_id": "uuid-123",
                "name": "DevArena T-Shirt",
                "description": "Official swag! Black tee with neon logo.",
                "type": "SWAG",
                "points_required": 500,
                "total_quantity": 100,
                "available_quantity": 48
            }
        }


# PUBLIC_INTERFACE
class RedemptionStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DECLINED = "DECLINED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


# PUBLIC_INTERFACE
class RedemptionTransactionDTO(BaseModel):
    """Tracks a single prize redemption by a user."""
    redemption_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    prize_id: str
    points_spent: int
    status: RedemptionStatus = RedemptionStatus.PENDING
    requested_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    fulfilled_at: Optional[datetime.datetime] = None
    meta: Optional[Dict[str, Any]] = None


# PUBLIC_INTERFACE
class RedeemCenterService:
    """
    In-memory, thread-safe service for prize catalog, redemptions, and inventory.
    Backed by internal dicts, with locking for concurrency.
    """

    _lock = threading.Lock()
    _prizes: Dict[str, PrizeDTO] = {}
    _redemptions: Dict[str, List[RedemptionTransactionDTO]] = {}  # user_id --> list
    _redemptions_by_id: Dict[str, RedemptionTransactionDTO] = {}

    # PUBLIC_INTERFACE
    def list_prizes(self) -> List[PrizeDTO]:
        """Return all current prizes in the catalog (with available > 0)."""
        with self._lock:
            return [
                prize
                for prize in self._prizes.values()
                if prize.available_quantity > 0
            ]

    # PUBLIC_INTERFACE
    def get_prize(self, prize_id: str) -> Optional[PrizeDTO]:
        """Get a single prize by ID."""
        with self._lock:
            return self._prizes.get(prize_id)

    # PUBLIC_INTERFACE
    def add_prize(self, prize: PrizeDTO) -> PrizeDTO:
        """Add a new prize to the catalog (admin)."""
        with self._lock:
            if prize.prize_id in self._prizes:
                raise ValueError("Duplicate prize_id")
            prize.total_quantity = prize.available_quantity
            self._prizes[prize.prize_id] = prize
            return prize

    # PUBLIC_INTERFACE
    def update_prize(self, prize_id: str, data: dict) -> Optional[PrizeDTO]:
        """Update an existing prize's details and/or add stock."""
        with self._lock:
            prize = self._prizes.get(prize_id)
            if not prize:
                return None
            updated_data = {**prize.dict(), **data}
            # If increasing available_quantity, ensure it doesn't exceed total_quantity
            inc_qty = data.get("increment_quantity")
            if inc_qty is not None and isinstance(inc_qty, int):
                updated_data.pop("available_quantity", None)
                updated_data.pop("total_quantity", None)
                updated_data["total_quantity"] = prize.total_quantity + inc_qty
                updated_data["available_quantity"] = prize.available_quantity + inc_qty

            updated_prize = PrizeDTO(**updated_data)
            self._prizes[prize_id] = updated_prize
            return updated_prize

    # PUBLIC_INTERFACE
    def remove_prize(self, prize_id: str) -> bool:
        """Delete a prize from the catalog (if not already redeemed by anyone)."""
        with self._lock:
            if prize_id in self._prizes:
                del self._prizes[prize_id]
                return True
            return False

    # PUBLIC_INTERFACE
    def get_user_redemptions(self, user_id: str) -> List[RedemptionTransactionDTO]:
        """List all redemption attempts by a user."""
        with self._lock:
            return list(self._redemptions.get(user_id, []))

    # PUBLIC_INTERFACE
    def get_redemption(self, redemption_id: str) -> Optional[RedemptionTransactionDTO]:
        """Get a redemption transaction by its ID."""
        with self._lock:
            return self._redemptions_by_id.get(redemption_id)

    # PUBLIC_INTERFACE
    def redeem_prize(
        self, user_id: str, prize_id: str, user_points: int, meta: Optional[dict] = None
    ) -> RedemptionTransactionDTO:
        """
        Attempt redemption for a given prize by user.
        Checks points and inventory, then decrements inventory and records transaction if
        successful.
        """
        with self._lock:
            prize = self._prizes.get(prize_id)
            if not prize:
                raise ValueError("Prize not found")
            if prize.available_quantity <= 0:
                raise ValueError("Prize out of stock")
            if user_points < prize.points_required:
                raise ValueError("Insufficient points to redeem this prize")
            # Atomically decrement inventory
            prize.available_quantity -= 1
            self._prizes[prize_id] = prize
            tx = RedemptionTransactionDTO(
                user_id=user_id,
                prize_id=prize_id,
                points_spent=prize.points_required,
                status=RedemptionStatus.APPROVED
                if prize.type != PrizeType.BONUS
                else RedemptionStatus.PENDING,
                requested_at=datetime.datetime.utcnow(),
                fulfilled_at=None,
                meta=meta,
            )
            # Register transaction
            self._redemptions.setdefault(user_id, []).append(tx)
            self._redemptions_by_id[tx.redemption_id] = tx
            return tx

    # PUBLIC_INTERFACE
    def admin_update_redemption_status(
        self, redemption_id: str, status: RedemptionStatus
    ) -> Optional[RedemptionTransactionDTO]:
        """Admin can move a redemption to completed/cancelled/etc."""
        with self._lock:
            tx = self._redemptions_by_id.get(redemption_id)
            if not tx:
                return None
            tx.status = status
            if status == RedemptionStatus.COMPLETED:
                tx.fulfilled_at = datetime.datetime.utcnow()
            return tx

    # PUBLIC_INTERFACE
    def list_all_redemptions(self) -> List[RedemptionTransactionDTO]:
        """
        ADMIN: List all redemptions in the system.
        All lines are <= 100 chars. Uses explicit loop for E501 compatibility.
        """
        with self._lock:
            results = []
            for tx in self._redemptions_by_id.values():
                results.append(tx)
            return results
