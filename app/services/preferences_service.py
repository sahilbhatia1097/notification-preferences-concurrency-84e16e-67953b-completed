from uuid import UUID
from typing import Optional
from app.models.preferences import NotificationPreferences, PreferencesUpdateRequest
from app.repositories.preferences_repository import get_preferences_by_user, update_preferences


def fetch_user_preferences(user_id: UUID) -> Optional[NotificationPreferences]:
    return get_preferences_by_user(user_id)


def apply_preference_updates(
    user_id: UUID,
    request: PreferencesUpdateRequest,
) -> Optional[NotificationPreferences]:
    updates = request.model_dump(exclude_none=True)
    return update_preferences(user_id, updates)
