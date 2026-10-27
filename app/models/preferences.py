from pydantic import BaseModel, field_validator
from typing import Optional
from uuid import UUID


class NotificationPreferences(BaseModel):
    user_id: UUID
    tenant_id: UUID
    email_enabled: bool
    sms_enabled: bool
    push_enabled: bool
    frequency: str
    version: int


class PreferencesUpdateRequest(BaseModel):
    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    frequency: Optional[str] = None

    @field_validator("frequency")
    @classmethod
    def validate_frequency(cls, v):
        allowed = {"realtime", "daily", "weekly", "never"}
        if v is not None and v not in allowed:
            raise ValueError(f"frequency must be one of {allowed}")
        return v


class PreferencesResponse(BaseModel):
    user_id: UUID
    email_enabled: bool
    sms_enabled: bool
    push_enabled: bool
    frequency: str
