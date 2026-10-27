from pydantic import BaseModel
from uuid import UUID


class TokenClaims(BaseModel):
    user_id: UUID
    tenant_id: UUID
    role: str
