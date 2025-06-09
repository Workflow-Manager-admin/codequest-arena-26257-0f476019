"""
FastAPI router for Notifications & Integrations.

Handles:
- /notifications/slack: Send simulated Slack message.
- /notifications/discord: Send simulated Discord message.
- /notifications/email: Send simulated email.
- /notifications/history: List history of all sent notifications.
- /integrations/jira: Stub endpoint for Jira integration.
- /integrations/trello: Stub endpoint for Trello integration.
- /integrations/asana: Stub endpoint for Asana integration.
"""

from fastapi import APIRouter, HTTPException, Body
from typing import List, Dict, Any

from ..services.notifications_service import (
    NotificationsService,
    NotificationRequestDTO,
    NotificationResponseDTO,
    NotificationChannel,
    NotificationHistoryRecord,
)

router = APIRouter()
service = NotificationsService()


# PUBLIC_INTERFACE
@router.post(
    "/notifications/slack",
    response_model=NotificationResponseDTO,
    tags=["Notifications & Integrations"],
)
def notify_slack(req: NotificationRequestDTO):
    """
    Send a simulated Slack notification.
    """
    if req.channel != NotificationChannel.SLACK:
        raise HTTPException(status_code=400, detail="Channel must be 'slack'")
    return service.send_slack(req.to, req.message, req.meta)


# PUBLIC_INTERFACE
@router.post(
    "/notifications/discord",
    response_model=NotificationResponseDTO,
    tags=["Notifications & Integrations"],
)
def notify_discord(req: NotificationRequestDTO):
    """
    Send a simulated Discord notification.
    """
    if req.channel != NotificationChannel.DISCORD:
        raise HTTPException(status_code=400, detail="Channel must be 'discord'")
    return service.send_discord(req.to, req.message, req.meta)


# PUBLIC_INTERFACE
@router.post(
    "/notifications/email",
    response_model=NotificationResponseDTO,
    tags=["Notifications & Integrations"],
)
def notify_email(req: NotificationRequestDTO):
    """
    Send a simulated Email notification.
    """
    if req.channel != NotificationChannel.EMAIL:
        raise HTTPException(status_code=400, detail="Channel must be 'email'")
    return service.send_email(req.to, req.message, req.meta)


# PUBLIC_INTERFACE
@router.get(
    "/notifications/history",
    response_model=List[NotificationHistoryRecord],
    tags=["Notifications & Integrations"],
)
def get_history():
    """
    Return a log of all simulated notifications sent.
    """
    return service.list_history()


# PUBLIC_INTERFACE
@router.post(
    "/integrations/jira",
    tags=["Notifications & Integrations"],
)
def integration_jira(payload: Dict[str, Any] = Body(...)):
    """
    Simulate sending data to Jira integration (stub).
    """
    return service.notify_jira(payload)


# PUBLIC_INTERFACE
@router.post(
    "/integrations/trello",
    tags=["Notifications & Integrations"],
)
def integration_trello(payload: Dict[str, Any] = Body(...)):
    """
    Simulate sending data to Trello integration (stub).
    """
    return service.notify_trello(payload)


# PUBLIC_INTERFACE
@router.post(
    "/integrations/asana",
    tags=["Notifications & Integrations"],
)
def integration_asana(payload: Dict[str, Any] = Body(...)):
    """
    Simulate sending data to Asana integration (stub).
    """
    return service.notify_asana(payload)
