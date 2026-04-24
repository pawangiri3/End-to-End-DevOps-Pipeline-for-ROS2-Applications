"""
main.py
-------
Application entry point.

• Configures structured JSON logging
• Creates the FastAPI app and mounts routers
• Manages ROS2 node lifecycle (startup / shutdown hooks)
• Runs uvicorn in production mode (no reload, no debug)
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
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routes.api import router as api_router
from app.routes.web import router as web_router


# ---------------------------------------------------------------------------
# Structured JSON logging setup
# ---------------------------------------------------------------------------
class _JSONFormatter(logging.Formatter):
    """Emit log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:  # noqa: A003
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
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

    # -- CORS (restrict in production to your actual domain) ---------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],          # tighten for real deployments
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # -- Request timing middleware ------------------------------------------
    @app.middleware("http")
    async def add_timing_header(request: Request, call_next):
        t0 = time.perf_counter()
        response = await call_next(request)
        elapsed = round((time.perf_counter() - t0) * 1000, 2)
        response.headers["X-Process-Time-Ms"] = str(elapsed)
        return response

    # -- Global exception handler -------------------------------------------
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
    app.include_router(web_router)   # HTML pages (no prefix)
    app.include_router(api_router)   # REST API  (/api/...)

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
        from app.ros_node import ros2_manager
        ros2_manager.start()
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
# Direct execution (python -m app.main)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
        workers=1,        # Keep at 1: ROS2 node is not fork-safe
    )
