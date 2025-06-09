"""
Main entrypoint for the CodeQuest Arena FastAPI backend.

This sets up modular routing, CORS, config/theme stubs, and prepares
the backend for all declared features:
- PR Integration & Repository Management
- Rule Engine
- Bug Logging & Peer Review
- Dispute Resolution Workflow
- Gamification Engine
- Redeem Center
- Analytics Dashboard
- Notifications & Integrations
- Security & Fairness Mechanisms

Extend individual feature routers in `api/routes/` as needed.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.requests import Request
from typing import Dict

from .routes import pr
from .routes import rule_engine
from .routes import bug
from .routes import gamification
from .routes import redeem_center
from .routes import analytics

# PUBLIC_INTERFACE


def get_settings() -> Dict[str, str]:
    """Returns settings/config for theming and global config (including glassy meta)."""
    # In the future, load from env file/config management
    return {
        "theme": "dark",
        "colors": {
            "primary": "#020d1d",
            "secondary": "#9CA3AF",
            "accent": "#013951",
            "background": "rgba(2,13,29,0.88)",
            "card_bg": "rgba(21,30,48,0.47)",
            "frost": "rgba(255,255,255,0.12)",
            "highlight": "#00eaff",
        },
        "glass": {
            "card_opacity": 0.47,
            "frost_intensity": 8,
            "border_radius": 20,
            "shadow": "0 4px 32px 4px rgba(2,13,29,0.11)",
            "blur_px": 18,
            "border": "1.5px solid rgba(255,255,255,0.12)",
        },
        "neon": {
            "hover_color": "#00eaff",
            "active_color": "#26ffb8",
        },
        "dark_mode": True,
        "layout": {
            "card_spacing": 28,
            "responsive_breakpoints": {
                "sm": 540,
                "md": 900,
                "lg": 1200,
            },
        },
        "meta": {
            "design": "glassmorphism",
            "animations": [
                "frosted-fade",
                "confetti",
                "neon-pulse",
            ],
        },
    }


app = FastAPI(
    title="CodeQuest Arena Backend",
    description=(
        "Backend core for CodeQuest Arena with modular API endpoints "
        "for all supported features."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS across all endpoints for ease of local frontend dev; restrict in production!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this for production security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint


# PUBLIC_INTERFACE
@app.get("/")
async def health_check():
    """Health check endpoint."""
    return {"message": "Healthy"}


# PUBLIC_INTERFACE

@app.get("/config/theme")
async def get_theme_config():
    """
    Retrieve global theme + extended glassmorphism meta config for frontend frosted effects.
    Returns theme, palette, card glass styles, neon configs, layout meta, and global meta info.
    """
    return get_settings()


# PUBLIC_INTERFACE
@app.get("/config/colors")
async def get_color_palette():
    """
    Retrieve the color palette for the glassmorphism UI (frontend may use these for CSS variables).
    """
    return get_settings().get("colors", {})


# PUBLIC_INTERFACE
@app.get("/config/layout")
async def get_layout_config():
    """
    Retrieve meta layout info for glassy dashboard—useful for card spacing, breakpoints, etc.
    """
    return get_settings().get("layout", {})


# ----- Stubs for future modular routers -----
app.include_router(pr.router, prefix="/pr", tags=["PR Integration"])
app.include_router(rule_engine.router, prefix="/rules", tags=["Rule Engine"])
app.include_router(bug.router, prefix="/bug", tags=["Bug Logging & Peer Review"])
app.include_router(gamification.router, prefix="/gamification", tags=["Gamification Engine"])
app.include_router(redeem_center.router, prefix="/redeem", tags=["Redeem Center"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
# Example: from .routes import bugs, dispute, gamification, redeem, analytics, notifications, security
# ...


# PUBLIC_INTERFACE

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Custom 404 error handler."""
    detail_msg = (
        "Path '" + str(request.url.path) +
        "' not found in CodeQuest Arena API."
    )
    return JSONResponse(
        status_code=404,
        content={
            "detail": detail_msg
        },
    )


# PUBLIC_INTERFACE

@app.get("/features")
async def list_features():
    """
    Returns a list of supported/planned features and their enabled status.
    Useful for preflight checks or UI module enabling.
    """
    # Normally, this should come from config/db, here static for backend stub
    return {
        "features": [
            {
                "name": "PR Integration & Repository Management",
                "enabled": True,
            },
            {
                "name": "Rule Engine",
                "enabled": True,
            },
            {
                "name": "Bug Logging & Peer Review",
                "enabled": True,
            },
            {
                "name": "Dispute Resolution Workflow",
                "enabled": True,
            },
            {
                "name": "Gamification Engine",
                "enabled": True,
            },
            {
                "name": "Redeem Center",
                "enabled": True,
            },
            {
                "name": "Analytics Dashboard",
                "enabled": True,
            },
            {
                "name": "Glassy UI & UX Design",
                "enabled": True,
            },
            {
                "name": "Notifications & Integrations",
                "enabled": True,
            },
            {
                "name": "Security & Fairness Mechanisms",
                "enabled": True,
            },
        ]
    }


# PUBLIC_INTERFACE

@app.get("/status")
async def status():
    """Extended system status endpoint."""
    return {
        "status": "ok",
        "theme": get_settings()["theme"],
        "app_version": app.version,
    }
