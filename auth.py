from __future__ import annotations

import logging
import os

import httpx

LOGGER = logging.getLogger(__name__)

PROJECT_ID = 256000
MERCHANT_ID = 329415
LOGIN_ID = "048e3522-75bd-43f5-95da-6ec145b9723a"
WEBHOOK_URL = "https://vd.appquantum.tech/webhook/user_validation"
LOGIN_ENDPOINT = "https://sb-user-id-service.xsolla.com/api/v1/user-id"
STORE_API_BASE = f"https://store.xsolla.com/api/v2/project/{PROJECT_ID}"
TIMEOUT_SECONDS = 15.0


def login(client: httpx.Client, user_id: str) -> str:
    """Authenticate with Xsolla user-id service and return a JWT token."""
    resp = client.post(
        LOGIN_ENDPOINT,
        json={
            "settings": {"projectId": PROJECT_ID, "merchantId": MERCHANT_ID},
            "loginId": LOGIN_ID,
            "webhookUrl": WEBHOOK_URL,
            "user": {"id": user_id, "country": "KR"},
            "isUserIdFromWebhook": False,
        },
    )
    resp.raise_for_status()
    token: str = resp.json()["token"]
    LOGGER.debug("login ok for %s (token %s...)", user_id[:8], token[:20])
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
