from twilio.rest import Client
import asyncio

from ..settings import settings


_twilio_client: Client | None = None


def _get_twilio_client() -> Client:
    global _twilio_client
    if _twilio_client is None:
        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
            raise RuntimeError("Twilio not configured")
        _twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    return _twilio_client


async def send_sms_message(to: str, body: str) -> str:
    try:
        client = _get_twilio_client()
        loop = asyncio.get_running_loop()
        def _send():
            msg = client.messages.create(
                messaging_service_sid=settings.TWILIO_MESSAGING_SERVICE_SID,
                to=to,
                body=body,
            )
            return msg.sid
        sid = await loop.run_in_executor(None, _send)
        return sid
    except Exception as e:
        raise RuntimeError(f"SMS send failed: {str(e)}")

