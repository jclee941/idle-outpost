from __future__ import annotations

import logging
import os
from urllib.parse import urlparse

import httpx

from scraper import Code, source_name

LOGGER = logging.getLogger(__name__)
TIMEOUT_SECONDS = 10.0


def notify_new_codes(codes: list[Code]) -> None:
    if not codes:
        return

    message = _build_message(codes)
    webhook_url = os.getenv("IDLE_OUTPOST_SLACK_WEBHOOK", "").strip()
    if not webhook_url:
        print(message)
        return

    try:
        with httpx.Client(timeout=TIMEOUT_SECONDS) as client:
            response = client.post(webhook_url, json={"text": message})
            _ = response.raise_for_status()
    except httpx.HTTPError as exc:
        webhook_host = urlparse(webhook_url).netloc or "unknown-host"
        LOGGER.warning(
            "slack webhook send failed for host=%s error=%s",
            webhook_host,
            exc.__class__.__name__,
        )
        print(message)


def _build_message(codes: list[Code]) -> str:
    lines = ["🎟️ Idle Outpost 새 코드 발견!", ""]
    for code in codes:
        lines.append(f"• `{code.code_text}` (출처: {source_name(code.source_url)})")

    lines.extend(["", "리딤: https://idleoutpost-store.appquantum.com/"])
    return "\n".join(lines)
