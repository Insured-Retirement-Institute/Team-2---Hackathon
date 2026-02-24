from pydantic import BaseModel


class PolicyRequest(BaseModel):
    policy_number: str
