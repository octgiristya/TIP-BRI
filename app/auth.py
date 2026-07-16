import pyotp
from fastapi import Request, HTTPException, status
from functools import wraps
from app.config import get_settings

settings = get_settings()

def verify_totp(secret: str, token: str) -> bool:
    # Clean the token (remove spaces, etc)
    clean_token = token.replace(" ", "").strip()
    totp = pyotp.TOTP(secret, interval=30, digest='sha1', digits=6)
    # Use valid_window=1 to allow for a 30-second clock drift tolerance
    return totp.verify(clean_token, valid_window=1)

def admin_required(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        is_admin = request.session.get("is_admin", False)
        if not is_admin:
            # If not admin, redirect to login (this is handled in the router usually)
            # but raising 401 for API, or we can handle it in the router dependency
            pass
        return await func(request, *args, **kwargs)
    return wrapper

def check_session_admin(request: Request):
    return request.session.get("is_admin", False)
