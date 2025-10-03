from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .settings import settings
from .routes import health, sms, auth_ms, webhooks_ms, auth_slack


app = FastAPI(title="SMS Meeting Summary MVP", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(health.router, prefix="/health", tags=["health"]) 
app.include_router(sms.router, prefix="/sms", tags=["sms"]) 
app.include_router(auth_ms.router, prefix="/auth/ms", tags=["auth-ms"]) 
app.include_router(webhooks_ms.router, prefix="/webhooks/ms", tags=["webhooks-ms"]) 
app.include_router(auth_slack.router, prefix="/auth/slack", tags=["auth-slack"]) 


@app.get("/")
def root():
    return {"status": "ok", "env": settings.APP_ENV}

