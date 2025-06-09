"""
FastAPI router for Security & Fairness Mechanisms.
Handles:
- Rate limiting (middleware or endpoint-supported)
- Peer validation utilities
- Audit trail endpoints/service
- Bias detection and AI suggestion stubs (for future integration)
- Security modular endpoints

To be extended with real DB/caching and ML/AI in production.
"""

from fastapi import APIRouter, Request, HTTPException, status, Depends
from typing import Dict, Any, Optional
import time
import threading

router = APIRouter()


class SimpleRateLimiter:
    """
    In-memory, per-IP rate limiter.
    For demo only – use Redis or DB in production!
    """

    def __init__(self, calls: int = 100, period: int = 60):
        self.calls = calls
        self.period = period
        self.buckets = {}
        self.lock = threading.Lock()

    # PUBLIC_INTERFACE
    def is_allowed(self, key: str) -> bool:
        """Returns True if key (IP) is allowed a call now (within rate), else False."""
        now = int(time.time())
        window = now // self.period
        with self.lock:
            rec = self.buckets.setdefault(key, {})
            if rec.get("window") != window:
                rec["window"] = window
                rec["count"] = 1
            else:
                rec["count"] += 1
            allowed = rec["count"] <= self.calls
        return allowed


rate_limiter = SimpleRateLimiter(calls=30, period=60)  # 30 reqs/min/IP (demo)


def rate_limit_dependency(request: Request):
    ip = request.client.host
    if not rate_limiter.is_allowed(ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again soon."
        )


def validate_peer_info(peer_id: str, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Simulates peer validation (could check for prior bug logs, disputes, reviews, etc).
    Returns peer status and basic trust signals.
    """
    flagged = peer_id == "malicious-user"
    return {
        "peer_id": peer_id,
        "valid": not flagged,
        "flags": ["suspicious_behavior"] if flagged else [],
        "trust_score": 100 if not flagged else 55,
        "meta": meta or {}
    }


# ========== Audit Trail Service/Endpoints ==========

audit_logs = []
audit_lock = threading.Lock()


def log_audit_event(event_type: str, detail: dict, actor: Optional[str]) -> None:
    """Adds an audit event."""
    entry = {
        "timestamp": int(time.time()),
        "event_type": event_type,
        "detail": detail,
        "actor": actor,
    }
    with audit_lock:
        audit_logs.append(entry)


# PUBLIC_INTERFACE
@router.get("/security/audit-trail", tags=["Security & Fairness"])
def get_audit_trail(limit: int = 100):
    """Returns latest audit log events (max 100 by default)."""
    with audit_lock:
        return {"logs": list(reversed(audit_logs))[:limit]}


# ========== Bias Detection & AI Suggestion Placeholders ==========

# PUBLIC_INTERFACE
@router.post("/security/bias-detection", tags=["Security & Fairness"])
def bias_detection_stub(input_data: Dict[str, Any]):
    """
    Placeholder for ML/AI bias detection on reviews or PRs.
    Always returns unbiased (for now).
    """
    return {
        "detected_bias": False,
        "bias_score": 0.0,
        "explanation": "No bias detected (stub, always unbiased)",
        "input_data": input_data
    }


# PUBLIC_INTERFACE
@router.post("/security/ai-suggestion", tags=["Security & Fairness"])
def ai_suggestion_placeholder(input_data: Dict[str, Any]):
    """
    Placeholder for AI smart suggestion (improvements, dispute hints, review assists).
    """
    return {
        "suggestion": "Consider providing a more detailed reasoning for your action. (Stub)",
        "input_data": input_data
    }


# ========== Peer Validation Endpoint ==========

# PUBLIC_INTERFACE
@router.get("/security/peer-validate/{peer_id}", tags=["Security & Fairness"])
def peer_validate_endpoint(peer_id: str, meta: Optional[str] = None):
    """
    Returns simulated peer validation/trust assessment for a user.
    """
    result = validate_peer_info(peer_id, meta={"raw": meta})
    log_audit_event("peer_validation", {"peer_id": peer_id}, actor=peer_id)
    return result


# ========== Rate Limit Demo Protected Endpoint ==========

# PUBLIC_INTERFACE
@router.get(
    "/security/limited-demo",
    dependencies=[Depends(rate_limit_dependency)],
    tags=["Security & Fairness"]
)
def limited_demo_ep():
    """
    Example endpoint protected by rate limiter (Demo: limit 30 req/min per IP).
    """
    log_audit_event("rate_limited_demo_access", {"demo_hit": True}, actor=None)
    return {"detail": "Rate limiting demo succeeded! (not exceeded)"}
