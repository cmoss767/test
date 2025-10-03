from urllib.parse import urlencode

from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from ..settings import settings
from ..services.token_store import token_store


router = APIRouter()


AUTHORITY = f"https://login.microsoftonline.com/{settings.MS_TENANT_ID}"
AUTHORIZE_URL = f"{AUTHORITY}/oauth2/v2.0/authorize"
TOKEN_URL = f"{AUTHORITY}/oauth2/v2.0/token"

MS_SCOPES = [
    "offline_access",
    "Calendars.Read",
    "Chat.Read",
    "OnlineMeetings.Read",
]


@router.get("/login")
async def login_ms():
    if not settings.MS_CLIENT_ID or not settings.MS_REDIRECT_URI:
        raise HTTPException(status_code=500, detail="MS OAuth not configured")
    params = {
        "client_id": settings.MS_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": settings.MS_REDIRECT_URI,
        "response_mode": "query",
        "scope": " ".join(MS_SCOPES),
        "state": "dev",  # replace with real state/nonce later
    }
    return RedirectResponse(url=f"{AUTHORIZE_URL}?{urlencode(params)}")


@router.get("/callback")
async def callback_ms(code: str | None = None, state: str | None = None):
    if code is None:
        raise HTTPException(status_code=400, detail="Missing code")
    if not settings.MS_CLIENT_ID or not settings.MS_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="MS OAuth not configured")

    # Exchange code for tokens (simple httpx form post)
    import httpx

    data = {
        "client_id": settings.MS_CLIENT_ID,
        "client_secret": settings.MS_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.MS_REDIRECT_URI,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(TOKEN_URL, data=data)
        if resp.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Token exchange failed: {resp.text}")
        tokens = resp.json()
        token_store["ms"] = tokens
    return {"connected": True}

