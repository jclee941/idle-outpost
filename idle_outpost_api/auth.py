from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

import httpx

from .endpoints import PROD

LOGGER = logging.getLogger(__name__)


@dataclass
class FirebaseToken:
    id_token: str
    refresh_token: str | None = None
    expires_at: float = 0.0
    user_id: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def is_expired(self) -> bool:
        return time.time() >= (self.expires_at - 60)


@dataclass
class GameAuthSession:
    firebase: FirebaseToken
    game_session_token: str | None = None
    realm_id: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


def load_token_from_capture(flows_path: str) -> FirebaseToken | None:
    from mitmproxy.io import FlowReader

    with open(flows_path, "rb") as fh:
        reader = FlowReader(fh)
        for flow in reader.stream():
            req = getattr(flow, "request", None)
            if req is None:
                continue
            auth_header = req.headers.get("Authorization", "") if req.headers else ""
            if auth_header.startswith("Bearer ") and "rockbitegames" in req.host:
                token = auth_header[len("Bearer "):]
                LOGGER.info("found Bearer token in flow to %s%s", req.host, req.path)
                return FirebaseToken(id_token=token)
    return None


def post_login(
    firebase_id_token: str,
    *,
    base_url: str = PROD.gameauth,
    timeout: float = 15.0,
) -> dict[str, Any]:
    url = base_url.rstrip("/") + "/login"
    LOGGER.info("POST %s", url)
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(
            url,
            headers={
                "Authorization": f"Bearer {firebase_id_token}",
                "Content-Type": "application/json",
            },
            json={},
        )
        resp.raise_for_status()
        return resp.json()
