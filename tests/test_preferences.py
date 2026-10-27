import pytest
from fastapi.testclient import TestClient
from jose import jwt
from app.main import app
from app.config import settings

client = TestClient(app)


def make_token(user_id: str, tenant_id: str, role: str = "user") -> str:
    payload = {"user_id": user_id, "tenant_id": tenant_id, "role": role}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


ACME_TENANT = "a1000000-0000-0000-0000-000000000001"
GLOBEX_TENANT = "b2000000-0000-0000-0000-000000000002"
ALICE_ID = "c3000000-0000-0000-0000-000000000001"
BOB_ID = "c3000000-0000-0000-0000-000000000002"
CAROL_ID = "c3000000-0000-0000-0000-000000000003"
DAVE_ID = "d4000000-0000-0000-0000-000000000001"


def auth_header(user_id, tenant_id, role="user"):
    return {"Authorization": f"Bearer {make_token(user_id, tenant_id, role)}"}


class TestGetPreferences:
    def test_user_can_read_own_preferences(self):
        resp = client.get(f"/api/v1/users/{ALICE_ID}/preferences", headers=auth_header(ALICE_ID, ACME_TENANT))
        assert resp.status_code == 200

    def test_user_cannot_read_another_users_preferences(self):
        resp = client.get(f"/api/v1/users/{BOB_ID}/preferences", headers=auth_header(ALICE_ID, ACME_TENANT))
        assert resp.status_code == 403

    def test_admin_can_read_any_user_in_same_tenant(self):
        resp = client.get(f"/api/v1/users/{ALICE_ID}/preferences", headers=auth_header(CAROL_ID, ACME_TENANT, role="admin"))
        assert resp.status_code == 200

    def test_admin_cannot_read_user_in_different_tenant(self):
        resp = client.get(f"/api/v1/users/{DAVE_ID}/preferences", headers=auth_header(CAROL_ID, ACME_TENANT, role="admin"))
        assert resp.status_code == 403

    def test_get_response_includes_etag_header(self):
        resp = client.get(f"/api/v1/users/{ALICE_ID}/preferences", headers=auth_header(ALICE_ID, ACME_TENANT))
        assert resp.status_code == 200
        assert "etag" in resp.headers


class TestPutPreferences:
    def test_put_without_if_match_is_rejected(self):
        resp = client.put(
            f"/api/v1/users/{ALICE_ID}/preferences",
            json={"sms_enabled": True},
            headers=auth_header(ALICE_ID, ACME_TENANT),
        )
        assert resp.status_code in (400, 428)

    def test_put_with_matching_etag_succeeds(self):
        get_resp = client.get(f"/api/v1/users/{BOB_ID}/preferences", headers=auth_header(BOB_ID, ACME_TENANT))
        etag = get_resp.headers["etag"]
        put_resp = client.put(
            f"/api/v1/users/{BOB_ID}/preferences",
            json={"sms_enabled": False},
            headers={**auth_header(BOB_ID, ACME_TENANT), "If-Match": etag},
        )
        assert put_resp.status_code == 200

    def test_put_with_stale_etag_returns_412(self):
        get_resp = client.get(f"/api/v1/users/{CAROL_ID}/preferences", headers=auth_header(CAROL_ID, ACME_TENANT))
        etag = get_resp.headers["etag"]
        client.put(
            f"/api/v1/users/{CAROL_ID}/preferences",
            json={"push_enabled": False},
            headers={**auth_header(CAROL_ID, ACME_TENANT), "If-Match": etag},
        )
        stale_resp = client.put(
            f"/api/v1/users/{CAROL_ID}/preferences",
            json={"email_enabled": False},
            headers={**auth_header(CAROL_ID, ACME_TENANT), "If-Match": etag},
        )
        assert stale_resp.status_code == 412

    def test_cross_tenant_put_is_rejected(self):
        get_resp = client.get(f"/api/v1/users/{DAVE_ID}/preferences", headers=auth_header(DAVE_ID, GLOBEX_TENANT))
        etag = get_resp.headers.get("etag", '"1"')
        resp = client.put(
            f"/api/v1/users/{DAVE_ID}/preferences",
            json={"email_enabled": False},
            headers={**auth_header(CAROL_ID, ACME_TENANT, role="admin"), "If-Match": etag},
        )
        assert resp.status_code == 403
