from __future__ import annotations

import logging
import os
from urllib.parse import urlparse

import httpx

LOGGER = logging.getLogger(__name__)
TIMEOUT_SECONDS = 10.0


def post_slack(message: str) -> None:
    webhook_url = os.getenv("IDLE_OUTPOST_SLACK_WEBHOOK", "").strip()
    if not webhook_url:
        LOGGER.info("slack webhook not configured; notification suppressed")
        return
    try:
        with httpx.Client(timeout=TIMEOUT_SECONDS) as client:
            response = client.post(webhook_url, json={"text": message})
            _ = response.raise_for_status()
    except httpx.HTTPError as exc:
        host = urlparse(webhook_url).netloc or "unknown-host"
        LOGGER.warning("slack send failed host=%s error=%s", host, exc.__class__.__name__)
        LOGGER.info("slack notification suppressed due to delivery failure")


def notify_event(title: str, lines: list[str]) -> None:
    body = "\n".join([f"🤖 {title}", "", *lines])
    post_slack(body)
