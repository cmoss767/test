from fastapi import APIRouter
from pydantic import BaseModel

from ..services.sms_service import send_sms_message


router = APIRouter()


class SmsRequest(BaseModel):
    to: str
    body: str


@router.post("/send")
async def send_sms(req: SmsRequest):
    message_sid = await send_sms_message(to=req.to, body=req.body)
    return {"sid": message_sid}

