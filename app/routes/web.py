"""
routes/web.py
-------------
Browser-facing routes that return rendered HTML pages.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.auth import create_session_token, get_current_user, verify_password
from app.config import settings
from app.ros_node import robot_state

router = APIRouter(tags=["web"])
templates = Jinja2Templates(directory="app/templates")


# ---------------------------------------------------------------------------
# GET /  →  redirect to login
# ---------------------------------------------------------------------------
@router.get("/", response_class=RedirectResponse)
async def root():
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)


# ---------------------------------------------------------------------------
# GET /login
# ---------------------------------------------------------------------------
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = ""):
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": error, "app_name": settings.APP_NAME},
    )


# ---------------------------------------------------------------------------
# POST /login
# ---------------------------------------------------------------------------
@router.post("/login")
async def login_submit(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
):
    if not verify_password(username, password):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Invalid credentials. Try admin / r0b0t123",
                "app_name": settings.APP_NAME,
            },
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    token = create_session_token(username)
    redirect = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    redirect.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=settings.SESSION_MAX_AGE,
    )
    return redirect


# ---------------------------------------------------------------------------
# GET /dashboard  (protected)
# ---------------------------------------------------------------------------
@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    current_user: str = Depends(get_current_user),
):
    metrics = robot_state.get_metrics()
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "username": current_user,
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
            "metrics": metrics,
        },
    )


# ---------------------------------------------------------------------------
# POST /logout
# ---------------------------------------------------------------------------
@router.post("/logout")
async def logout():
    redirect = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    redirect.delete_cookie(settings.SESSION_COOKIE_NAME)
    return redirect
