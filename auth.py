from __future__ import annotations

import logging
import os

import httpx

LOGGER = logging.getLogger(__name__)

def _get_xsolla_project_id() -> int:
    raw = os.getenv("IDLE_OUTPOST_XSOLLA_PROJECT_ID", "").strip()
    if not raw:
        raise RuntimeError(
            "IDLE_OUTPOST_XSOLLA_PROJECT_ID is not set. "
            "Add it to your .env file (was 256000)."
        )
    return int(raw)


def _get_xsolla_merchant_id() -> int:
    raw = os.getenv("IDLE_OUTPOST_XSOLLA_MERCHANT_ID", "").strip()
    if not raw:
        raise RuntimeError(
            "IDLE_OUTPOST_XSOLLA_MERCHANT_ID is not set. "
            "Add it to your .env file (was 329415)."
        )
    return int(raw)


def _get_xsolla_login_id() -> str:
    raw = os.getenv("IDLE_OUTPOST_XSOLLA_LOGIN_ID", "").strip()
    if not raw:
        raise RuntimeError(
            "IDLE_OUTPOST_XSOLLA_LOGIN_ID is not set. "
            "Add it to your .env file (was 048e3522-75bd-43f5-95da-6ec145b9723a)."
        )
    return raw


def _get_xsolla_webhook_url() -> str:
    raw = os.getenv("IDLE_OUTPOST_XSOLLA_WEBHOOK_URL", "").strip()
    if not raw:
        raise RuntimeError(
            "IDLE_OUTPOST_XSOLLA_WEBHOOK_URL is not set. "
            "Add it to your .env file (was https://vd.appquantum.tech/webhook/user_validation)."
        )
    return raw


LOGIN_ENDPOINT = "https://sb-user-id-service.xsolla.com/api/v1/user-id"
TIMEOUT_SECONDS = 15.0


def get_store_api_base() -> str:
    return f"https://store.xsolla.com/api/v2/project/{_get_xsolla_project_id()}"



def login(client: httpx.Client, user_id: str) -> str:
    """Authenticate with Xsolla user-id service and return a JWT token."""
    resp = client.post(
        LOGIN_ENDPOINT,
        json={
            "settings": {
                "projectId": _get_xsolla_project_id(),
                "merchantId": _get_xsolla_merchant_id(),
            },
            "loginId": _get_xsolla_login_id(),
            "webhookUrl": _get_xsolla_webhook_url(),
            "user": {"id": user_id, "country": "KR"},
            "isUserIdFromWebhook": False,
        },
    )
    resp.raise_for_status()
    token: str = resp.json()["token"]
    LOGGER.debug("login ok for %s", user_id[:8])
    return token


def get_user_ids() -> list[str]:
    """Read user IDs from environment, supporting comma-separated values."""
    raw = os.getenv("IDLE_OUTPOST_USER_IDS", "").strip()
    if not raw:
        raw = os.getenv("IDLE_OUTPOST_USER_ID", "").strip()
    if not raw:
        return []
    return [uid.strip() for uid in raw.split(",") if uid.strip()]


def auth_headers(token: str) -> dict[str, str]:
    """Build Authorization header dict for Xsolla API requests."""
    return {"Authorization": f"Bearer {token}"}
