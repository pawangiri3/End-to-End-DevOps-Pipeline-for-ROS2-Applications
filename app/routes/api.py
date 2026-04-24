"""
routes/api.py
-------------
JSON REST API endpoints consumed by the dashboard frontend (AJAX).
All endpoints except /health require a valid session.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, field_validator

from app.auth import get_current_user
from app.config import settings
from app.ros_node import robot_state, ros2_manager

router = APIRouter(prefix="/api", tags=["api"])


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------
ALLOWED_COMMANDS = {"MOVE_FORWARD", "TURN_LEFT", "TURN_RIGHT", "STOP", "RESET"}


class CommandRequest(BaseModel):
    command: str

    @field_validator("command")
    @classmethod
    def validate_command(cls, v: str) -> str:
        v = v.upper().strip()
        if v not in ALLOWED_COMMANDS:
            raise ValueError(
                f"Unknown command '{v}'. Allowed: {', '.join(sorted(ALLOWED_COMMANDS))}"
            )
        return v


class CommandResponse(BaseModel):
    success: bool
    command: str
    status: str
    message_count: int


class MetricsResponse(BaseModel):
    command_count: int
    current_status: str
    last_command: str
    uptime_seconds: float
    ros2_enabled: bool
    app_version: str


# ---------------------------------------------------------------------------
# POST /api/command
# ---------------------------------------------------------------------------
@router.post("/command", response_model=CommandResponse)
async def send_command(
    body: CommandRequest,
    current_user: str = Depends(get_current_user),
) -> CommandResponse:
    """Publish a robot command via ROS2 (or simulation)."""
    ros2_manager.publish_command(body.command)
    metrics = robot_state.get_metrics()
    return CommandResponse(
        success=True,
        command=body.command,
        status=robot_state.get_status(),
        message_count=metrics["command_count"],
    )


# ---------------------------------------------------------------------------
# GET /api/status
# ---------------------------------------------------------------------------
@router.get("/status")
async def get_status(
    current_user: str = Depends(get_current_user),
) -> Dict[str, Any]:
    """Current robot status and message count (polled by dashboard)."""
    metrics = robot_state.get_metrics()
    return {
        "robot_status": metrics["current_status"],
        "command_count": metrics["command_count"],
        "last_command": metrics["last_command"],
    }


# ---------------------------------------------------------------------------
# GET /api/logs
# ---------------------------------------------------------------------------
@router.get("/logs")
async def get_logs(
    limit: int = 50,
    current_user: str = Depends(get_current_user),
) -> Dict[str, Any]:
    """Return the last N log entries (newest last)."""
    if limit < 1 or limit > settings.MAX_LOG_ENTRIES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"limit must be between 1 and {settings.MAX_LOG_ENTRIES}",
        )
    logs = robot_state.get_logs(limit=limit)
    return {"logs": logs, "count": len(logs)}


# ---------------------------------------------------------------------------
# GET /api/metrics
# ---------------------------------------------------------------------------
@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(
    current_user: str = Depends(get_current_user),
) -> MetricsResponse:
    """Expose operational metrics (Prometheus-friendly structure)."""
    m = robot_state.get_metrics()
    return MetricsResponse(
        command_count=m["command_count"],
        current_status=m["current_status"],
        last_command=m["last_command"],
        uptime_seconds=m["uptime_seconds"],
        ros2_enabled=settings.ROS2_ENABLED,
        app_version=settings.APP_VERSION,
    )


# ---------------------------------------------------------------------------
# GET /health   (public — used by k8s liveness/readiness probes)
# ---------------------------------------------------------------------------
@router.get("/health", tags=["health"])
async def health() -> Dict[str, Any]:
    """
    Health check endpoint — no auth required.
    Returns HTTP 200 when the service is operational.
    """
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "robot_status": robot_state.get_status(),
        "uptime_seconds": robot_state.get_metrics()["uptime_seconds"],
        "timestamp": time.time(),
    }
