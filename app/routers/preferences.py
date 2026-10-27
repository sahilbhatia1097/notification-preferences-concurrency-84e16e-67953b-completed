
import hashlib
import json
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Response

from app.middleware.auth import decode_token
from app.models.auth import TokenClaims
from app.models.preferences import PreferencesUpdateRequest, PreferencesResponse
from app.services.preferences_service import (
    fetch_user_preferences,
    apply_preference_updates,
)

router = APIRouter()


def make_etag(prefs) -> str:
    # Version-based ETag changes when the stored version changes.
    return f'"{prefs.version}"'


def authorize(user_id: UUID, claims: TokenClaims, prefs) -> None:
    if str(claims.user_id) == str(user_id):
        return

    if claims.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access these preferences",
        )

    if str(claims.tenant_id) != str(prefs.tenant_id):
        raise HTTPException(
            status_code=403,
            detail="Cross-tenant access is forbidden",
        )


@router.get("/users/{user_id}/preferences", response_model=PreferencesResponse)
def get_preferences(
    user_id: UUID,
    response: Response,
    claims: TokenClaims = Depends(decode_token),
):
    prefs = fetch_user_preferences(user_id)

    if not prefs:
        raise HTTPException(status_code=404, detail="Preferences not found")

    authorize(user_id, claims, prefs)
    response.headers["ETag"] = make_etag(prefs)

    return PreferencesResponse(**prefs.model_dump())


@router.put("/users/{user_id}/preferences", response_model=PreferencesResponse)
def update_preferences(
    user_id: UUID,
    body: PreferencesUpdateRequest,
    response: Response,
    if_match: str | None = Header(default=None, alias="If-Match"),
    claims: TokenClaims = Depends(decode_token),
):
    if if_match is None:
        raise HTTPException(
            status_code=428,
            detail="If-Match header is required",
        )

    current = fetch_user_preferences(user_id)

    if not current:
        raise HTTPException(status_code=404, detail="Preferences not found")

    authorize(user_id, claims, current)

    if if_match.strip() != make_etag(current):
        raise HTTPException(
            status_code=412,
            detail="ETag does not match the current preferences",
        )
    updated = apply_preference_updates(
    user_id, body, current.version
)

    if not updated:
        raise HTTPException(
        status_code=412,
        detail="Preferences changed; fetch the latest ETag and retry",
    )
    

   
    response.headers["ETag"] = make_etag(updated)
    return PreferencesResponse(**updated.model_dump())
