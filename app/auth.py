"""
auth.py
-------
Session-based authentication using signed cookies (itsdangerous).
Credentials are hardcoded for demo purposes — swap for DB in production.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
from typing import Optional

from fastapi import Cookie, HTTPException, Request, status
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Hardcoded users  {username: hashed_password}
# Passwords: admin / r0b0t123  — hash with SHA-256 for minimal security hygiene
# ---------------------------------------------------------------------------
_USERS: dict[str, str] = {
    "admin": hashlib.sha256(b"r0b0t123").hexdigest(),
    "devops": hashlib.sha256(b"demo2024").hexdigest(),
}

_serializer = URLSafeTimedSerializer(settings.SECRET_KEY)


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def verify_password(username: str, password: str) -> bool:
    """Return True when credentials are valid."""
    stored_hash = _USERS.get(username)
    if stored_hash is None:
        return False
    candidate_hash = hashlib.sha256(password.encode()).hexdigest()
    return hmac.compare_digest(stored_hash, candidate_hash)


def create_session_token(username: str) -> str:
    """Sign a session token that encodes the username."""
    return _serializer.dumps({"user": username})


def decode_session_token(token: str, max_age: int = 86_400) -> Optional[str]:
    """
    Decode and verify a session token.
    Returns the username or None on failure.
    max_age: token validity in seconds (default 24 h).
    """
    try:
        data = _serializer.loads(token, max_age=max_age)
        return data.get("user")
    except (SignatureExpired, BadSignature):
        return None


def get_current_user(request: Request) -> str:
    """
    FastAPI dependency — extract and validate the session cookie.
    Raises HTTP 401 when unauthenticated.
    """
    token: Optional[str] = request.cookies.get(settings.SESSION_COOKIE_NAME)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    username = decode_session_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid",
        )
    return username
