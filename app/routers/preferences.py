from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from app.middleware.auth import decode_token
from app.models.auth import TokenClaims
from app.models.preferences import PreferencesUpdateRequest, PreferencesResponse
from app.services.preferences_service import fetch_user_preferences, apply_preference_updates

router = APIRouter()


@router.get("/users/{user_id}/preferences", response_model=PreferencesResponse)
def get_preferences(
    user_id: UUID,
    claims: TokenClaims = Depends(decode_token),
):
    prefs = fetch_user_preferences(user_id)
    if not prefs:
        raise HTTPException(status_code=404, detail="Preferences not found")
    return PreferencesResponse(**prefs.model_dump())


@router.put("/users/{user_id}/preferences", response_model=PreferencesResponse)
def update_preferences(
    user_id: UUID,
    body: PreferencesUpdateRequest,
    claims: TokenClaims = Depends(decode_token),
):
    updated = apply_preference_updates(user_id, body)
    if not updated:
        raise HTTPException(status_code=404, detail="Preferences not found")
    return PreferencesResponse(**updated.model_dump())
