from fastapi import APIRouter


router = APIRouter()


@router.get("/")
async def liveness():
    return {"ok": True}


@router.get("/ready")
async def readiness():
    return {"ok": True}

