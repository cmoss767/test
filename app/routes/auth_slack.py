from urllib.parse import urlencode

from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from ..settings import settings
from ..services.token_store import token_store


router = APIRouter()


SLACK_AUTHORIZE_URL = "https://slack.com/oauth/v2/authorize"
SLACK_TOKEN_URL = "https://slack.com/api/oauth.v2.access"

SLACK_SCOPES = [
    "channels:read",
    "channels:history",
    "users:read",
]


@router.get("/login")
async def login_slack():
    if not settings.SLACK_CLIENT_ID or not settings.SLACK_REDIRECT_URI:
        raise HTTPException(status_code=500, detail="Slack OAuth not configured")
    params = {
        "client_id": settings.SLACK_CLIENT_ID,
        "scope": ",".join(SLACK_SCOPES),
        "redirect_uri": settings.SLACK_REDIRECT_URI,
        "state": "dev",
    }
    return RedirectResponse(url=f"{SLACK_AUTHORIZE_URL}?{urlencode(params)}")


@router.get("/callback")
async def callback_slack(code: str | None = None, state: str | None = None):
    if code is None:
        raise HTTPException(status_code=400, detail="Missing code")
    if not settings.SLACK_CLIENT_ID or not settings.SLACK_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Slack OAuth not configured")

    import httpx

    params = {
        "code": code,
        "client_id": settings.SLACK_CLIENT_ID,
        "client_secret": settings.SLACK_CLIENT_SECRET,
        "redirect_uri": settings.SLACK_REDIRECT_URI,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(SLACK_TOKEN_URL, data=params)
        data = resp.json()
        if not data.get("ok"):
            raise HTTPException(status_code=500, detail=f"Slack token exchange failed: {data}")
        token_store["slack"] = data
    return {"connected": True}

