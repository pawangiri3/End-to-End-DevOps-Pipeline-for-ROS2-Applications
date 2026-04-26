"""
app/main.py
-----------
Application entry point.

• Configures structured JSON logging
• Creates the FastAPI app and mounts routers
• Manages ROS2 node lifecycle (startup / shutdown hooks)
• Exposes /metrics for Prometheus scraping
• Runs uvicorn in production mode (no reload, no debug)

Import order (dependency graph — no cycles):
  config  ←  metrics  ←  ros_node  ←  routes  ←  main
"""

from __future__ import annotations

import json
import logging
import sys
import time
from typing import Any

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.config import settings

# ── metrics must be imported before ros_node / routes so the Counter
#    objects exist before any other module tries to .inc() them ──────────────
from app.metrics import (                          # noqa: E402
    http_requests_total,
    request_duration_seconds,
    update_robot_status_gauge,
    uptime_seconds_gauge,
)
from app.routes.api import router as api_router
from app.routes.web import router as web_router


# ---------------------------------------------------------------------------
# Structured JSON logging
# ---------------------------------------------------------------------------
class _JSONFormatter(logging.Formatter):
    """Emit log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:  # noqa: A003
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level":     record.levelname,
            "logger":    record.name,
            "message":   record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def _configure_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    if settings.LOG_FORMAT == "json":
        handler.setFormatter(_JSONFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
        )
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(settings.LOG_LEVEL.upper())


_configure_logging()
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# FastAPI application factory
# ---------------------------------------------------------------------------
def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # -- CORS ---------------------------------------------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],          # tighten for real deployments
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # -- Observability middleware -------------------------------------------
    # Records request latency + count into Prometheus metrics
    @app.middleware("http")
    async def observability_middleware(request: Request, call_next):
        t0 = time.perf_counter()
        response = await call_next(request)
        elapsed = time.perf_counter() - t0

        # Skip /metrics itself to avoid self-scrape noise
        if request.url.path != "/metrics":
            endpoint = request.url.path
            method   = request.method
            status   = str(response.status_code)

            request_duration_seconds.labels(method=method, endpoint=endpoint).observe(elapsed)
            http_requests_total.labels(method=method, endpoint=endpoint, status_code=status).inc()

        response.headers["X-Process-Time-Ms"] = str(round(elapsed * 1000, 2))
        return response

    # -- Global exception handler ------------------------------------------
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception on %s %s", request.method, request.url)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error — check logs for details"},
        )

    # -- Static files -------------------------------------------------------
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    # -- Routers ------------------------------------------------------------
    app.include_router(web_router)    # HTML pages  (no prefix)
    app.include_router(api_router)    # REST API    (/api/...)

    # ── /metrics ─────────────────────────────────────────────────────────────
    # Prometheus scrape endpoint — returns text/plain in exposition format.
    # No auth required (standard for internal k8s scraping).
    # Kubernetes ServiceMonitor example:
    #   endpoints:
    #     - port: http
    #       path: /metrics
    #       interval: 15s
    @app.get(
        "/metrics",
        include_in_schema=False,   # hide from Swagger — not a REST endpoint
        tags=["observability"],
    )
    async def prometheus_metrics() -> Response:
        """
        Prometheus scrape endpoint.
        Returns metrics in the Prometheus text exposition format.
        """
        data = generate_latest()
        return Response(content=data, media_type=CONTENT_TYPE_LATEST)

    # -- Lifecycle hooks ----------------------------------------------------
    @app.on_event("startup")
    async def on_startup() -> None:
        logger.info(
            "Starting %s v%s on %s:%s",
            settings.APP_NAME,
            settings.APP_VERSION,
            settings.HOST,
            settings.PORT,
        )
        from app.ros_node import robot_state, ros2_manager
        ros2_manager.start()

        # Seed the robot status gauge on boot
        update_robot_status_gauge(robot_state.get_status())

        # Background thread: keep uptime gauge updated every 5 s
        import threading

        def _uptime_loop() -> None:
            from app.ros_node import robot_state as rs
            while True:
                m = rs.get_metrics()
                uptime_seconds_gauge.set(m["uptime_seconds"])
                update_robot_status_gauge(rs.get_status())
                time.sleep(5)

        threading.Thread(target=_uptime_loop, daemon=True, name="metrics-updater").start()
        logger.info("Application startup complete")

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        logger.info("Shutting down — stopping ROS2 node …")
        from app.ros_node import ros2_manager
        ros2_manager.stop()
        logger.info("Shutdown complete")

    return app


app = create_app()


# ---------------------------------------------------------------------------
# Direct execution:  python -m app.main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
        workers=1,        # Keep at 1 — ROS2 node is not fork-safe
    )