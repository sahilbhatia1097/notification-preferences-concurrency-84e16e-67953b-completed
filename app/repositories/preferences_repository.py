
from uuid import UUID
from typing import Optional

from app.database import get_db
from app.models.preferences import NotificationPreferences


COLUMNS = {
    "email_enabled",
    "sms_enabled",
    "push_enabled",
    "frequency",
}

RETURNING = (
    "user_id, tenant_id, email_enabled, sms_enabled, "
    "push_enabled, frequency, version"
)


def get_preferences_by_user(
    user_id: UUID,
) -> Optional[NotificationPreferences]:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT {RETURNING} FROM notification_preferences "
                "WHERE user_id = %s",
                (str(user_id),),
            )
            row = cur.fetchone()
            return NotificationPreferences(**row) if row else None


def update_preferences(
    user_id: UUID,
    updates: dict,
    expected_version: int,
) -> Optional[NotificationPreferences]:
    if not set(updates).issubset(COLUMNS):
        raise ValueError("Invalid preference field")

    if not updates:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT {RETURNING} FROM notification_preferences "
                    "WHERE user_id = %s AND version = %s",
                    (str(user_id), expected_version),
                )
                row = cur.fetchone()
                return NotificationPreferences(**row) if row else None

    set_clauses = ", ".join(f"{key} = %s" for key in updates)
    values = list(updates.values())

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE notification_preferences "
                f"SET {set_clauses}, version = version + 1, updated_at = NOW() "
                f"WHERE user_id = %s AND version = %s "
                f"RETURNING {RETURNING}",
                values + [str(user_id), expected_version],
            )
            row = cur.fetchone()
            return NotificationPreferences(**row) if row else None
