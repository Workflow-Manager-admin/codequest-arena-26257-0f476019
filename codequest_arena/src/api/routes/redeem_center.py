"""
FastAPI router for Redeem Center (points redemption & prize inventory).

Endpoints:
- List prizes, get prize details
- Redeem points for prizes
- Admin: add/update/remove prizes, manage inventory
- List user or all redemption transactions
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from ..services.redeem_center_service import (
    PrizeDTO,
    PrizeType,
    RedeemCenterService,
    RedemptionTransactionDTO,
    RedemptionStatus,
)
from ..services.gamification_service import GamificationService

router = APIRouter()
service = RedeemCenterService()
gamification = GamificationService()


class PrizeCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    type: PrizeType = PrizeType.OTHER
    points_required: int
    available_quantity: int
    meta: Optional[Dict[str, Any]] = None


class PrizeUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[PrizeType] = None
    points_required: Optional[int] = None
    increment_quantity: Optional[int] = None
    meta: Optional[Dict[str, Any]] = None


class RedemptionRequest(BaseModel):
    user_id: str
    prize_id: str
    meta: Optional[Dict[str, Any]] = None


class AdminRedemptionStatusUpdate(BaseModel):
    status: RedemptionStatus


# ----- PUBLIC ENDPOINTS -----

# PUBLIC_INTERFACE
@router.get("/prizes", response_model=List[PrizeDTO], tags=["Redeem Center"])
def list_prizes():
    """List all currently available prizes."""
    return service.list_prizes()


# PUBLIC_INTERFACE
@router.get("/prizes/{prize_id}", response_model=PrizeDTO, tags=["Redeem Center"])
def get_prize(prize_id: str):
    """Get details of a single prize."""
    prize = service.get_prize(prize_id)
    if not prize:
        raise HTTPException(status_code=404, detail="Prize not found")
    return prize


# PUBLIC_INTERFACE
@router.post(
    "/redeem",
    response_model=RedemptionTransactionDTO,
    tags=["Redeem Center"],
    status_code=status.HTTP_201_CREATED,
)
def redeem_prize(req: RedemptionRequest):
    """
    Redeem a prize with your points.
    Checks user's points (from gamification engine), inventory, decrements inventory,
    and records transaction.
    """
    user_points = gamification.get_points_balance(req.user_id)
    try:
        tx = service.redeem_prize(req.user_id, req.prize_id, user_points, req.meta)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    # If redemption successful, deduct points from user
    gamification.award_points(
        req.user_id,
        -tx.points_spent,
        reason="REDEEM",
        meta={"prize_id": req.prize_id}
    )
    return tx


# PUBLIC_INTERFACE
@router.get(
    "/users/{user_id}/redemptions",
    response_model=List[RedemptionTransactionDTO],
    tags=["Redeem Center"]
)
def list_user_redemptions(user_id: str):
    """List all redemptions/transfers made by the user."""
    return service.get_user_redemptions(user_id)


# ----- ADMIN ENDPOINTS -----


# PUBLIC_INTERFACE
@router.post(
    "/admin/prizes",
    response_model=PrizeDTO,
    tags=["Redeem Center (Admin)"],
    status_code=status.HTTP_201_CREATED,
)
def admin_add_prize(req: PrizeCreateRequest):
    """ADMIN: Add a new prize to the catalog."""
    prize = PrizeDTO(
        name=req.name,
        description=req.description,
        type=req.type,
        points_required=req.points_required,
        total_quantity=req.available_quantity,
        available_quantity=req.available_quantity,
        meta=req.meta,
    )
    try:
        return service.add_prize(prize)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# PUBLIC_INTERFACE
@router.put(
    "/admin/prizes/{prize_id}",
    response_model=PrizeDTO,
    tags=["Redeem Center (Admin)"]
)
def admin_update_prize(prize_id: str, req: PrizeUpdateRequest):
    """ADMIN: Update prize details or add inventory quantity."""
    data = req.dict(exclude_unset=True)
    updated = service.update_prize(prize_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Prize not found")
    return updated


# PUBLIC_INTERFACE
@router.delete(
    "/admin/prizes/{prize_id}",
    tags=["Redeem Center (Admin)"]
)
def admin_remove_prize(prize_id: str):
    """ADMIN: Remove a prize (if possible)."""
    ok = service.remove_prize(prize_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Prize not found")
    return {"success": True}


# PUBLIC_INTERFACE
@router.get(
    "/admin/redemptions",
    response_model=List[RedemptionTransactionDTO],
    tags=["Redeem Center (Admin)"]
)
def admin_list_all_redemptions():
    """ADMIN: List all redemption transactions (all users)."""
    return service.list_all_redemptions()


# PUBLIC_INTERFACE
@router.put(
    "/admin/redemptions/{redemption_id}/status",
    response_model=RedemptionTransactionDTO,
    tags=["Redeem Center (Admin)"]
)
def admin_update_redemption_status(redemption_id: str, req: AdminRedemptionStatusUpdate):
    """ADMIN: Set status for a redemption (e.g., completed after approval/review)."""
    updated = service.admin_update_redemption_status(redemption_id, req.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Redemption not found")
    return updated


# PUBLIC_INTERFACE
@router.get(
    "/admin/redemptions/{redemption_id}",
    response_model=RedemptionTransactionDTO,
    tags=["Redeem Center (Admin)"]
)
def admin_get_redemption(redemption_id: str):
    """ADMIN: Get details of a single redemption transaction."""
    tx = service.get_redemption(redemption_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Redemption not found")
    return tx
