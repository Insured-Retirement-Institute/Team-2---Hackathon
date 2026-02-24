from fastapi import APIRouter

from api.database import fetch_rows
from api.models import PolicyRequest

router = APIRouter(prefix="/v2", tags=["policies"])


@router.post("/policies")
async def get_policy(req: PolicyRequest):
    return await fetch_rows("get_policy", req.policy_number)
