from fastapi import APIRouter, Request


router = APIRouter()


@router.post("/graph")
async def ms_graph_webhook(request: Request):
    # Graph validation: return validationToken on subscription validation
    validation_token = request.query_params.get("validationToken")
    if validation_token:
        return validation_token

    payload = await request.json()
    # For MVP: just echo and pretend we will enqueue a summarization job
    return {"received": True, "payload": payload}

