"""
Demo unit test for core backend service logic (GamificationService) in CodeQuest Arena.

Note: This is a minimal sample; actual tests should be expanded for real coverage.
"""

from src.api.services.gamification_service import GamificationService, PointsReason


# PUBLIC_INTERFACE
def test_award_points_increases_balance():
    """Test that awarding points increases user's balance."""
    svc = GamificationService()
    user = "unittest-user-1"
    before = svc.get_points_balance(user)
    svc.award_points(user, 50, PointsReason.BUG_LOGGED)
    after = svc.get_points_balance(user)
    assert after == before + 50


# PUBLIC_INTERFACE
def test_reset_user_zeros_balance():
    """Test that reset_user zeros out all records for the user."""
    svc = GamificationService()
    uid = "reset-user-1"
    svc.award_points(uid, 100, PointsReason.BUG_FIXED)
    assert svc.get_points_balance(uid) > 0
    svc.reset_user(uid)
    assert svc.get_points_balance(uid) == 0
    assert svc.list_points_transactions(uid) == []
    assert svc.list_badges(uid) == []
    assert svc.list_achievements(uid) == []
