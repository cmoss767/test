from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_ENV: str = Field(default="development")
    PORT: int = Field(default=8000)
    API_SECRET_KEY: str = Field(default="change-me")

    PUBLIC_BASE_URL: str = Field(default="http://localhost:8000")

    TWILIO_ACCOUNT_SID: str | None = None
    TWILIO_AUTH_TOKEN: str | None = None
    TWILIO_MESSAGING_SERVICE_SID: str | None = None
    SMS_TO: str | None = None

    MS_CLIENT_ID: str | None = None
    MS_CLIENT_SECRET: str | None = None
    MS_TENANT_ID: str = Field(default="common")
    MS_REDIRECT_URI: str = Field(default="http://localhost:8000/auth/ms/callback")

    SLACK_CLIENT_ID: str | None = None
    SLACK_CLIENT_SECRET: str | None = None
    SLACK_REDIRECT_URI: str = Field(default="http://localhost:8000/auth/slack/callback")

    class Config:
        env_file = ".env"


settings = Settings()

