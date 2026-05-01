#!/usr/bin/env python3
"""Idle Outpost 웹샵 데일리 무료 보너스 — 순수 HTTP API (브라우저 불필요)"""

from __future__ import annotations

import json
import logging
import os
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

import httpx
from dotenv import load_dotenv

from auth import STORE_API_BASE, TIMEOUT_SECONDS, auth_headers, get_user_ids, login

KST = ZoneInfo("Asia/Seoul")
LOG = logging.getLogger("claim_api")


@dataclass(slots=True)
class ClaimResult:
    name: str
    sku: str
    status: str  # ok | skip | limit | error
    detail: str


def get_giveaway_items(client: httpx.Client, token: str) -> list[dict[str, object]]:
    resp = client.get(
        f"{STORE_API_BASE}/items/virtual_items/group",
        params={"external_id[]": "giveaway", "locale": "en", "limit": "50"},
        headers=auth_headers(token),
    )
    resp.raise_for_status()
    items: list[dict[str, object]] = resp.json().get("items", [])
    LOG.info("giveaway items: %d", len(items))
    return items


def claim_item(client: httpx.Client, token: str, sku: str) -> int:
    resp = client.post(
        f"{STORE_API_BASE}/free/item/{sku}",
        headers=auth_headers(token),
    )
    return resp.status_code


def claim_all(user_id: str) -> list[ClaimResult]:
    results: list[ClaimResult] = []
    with httpx.Client(timeout=TIMEOUT_SECONDS) as client:
        token = login(client, user_id)
        items = get_giveaway_items(client, token)

        for item in items:
            sku = str(item.get("sku", ""))
            name = str(item.get("name", ""))
            limits = item.get("limits")
            per_user = (limits if isinstance(limits, dict) else {}).get("per_user", {})
            available = (per_user if isinstance(per_user, dict) else {}).get("available", 0)
            recurrent = (per_user if isinstance(per_user, dict) else {}).get(
                "recurrent_schedule", {}
            )
            interval = (recurrent if isinstance(recurrent, dict) else {}).get("interval_type", "?")

            if not isinstance(available, int) or available <= 0:
                results.append(ClaimResult(name, sku, "skip", f"이미 수집됨 ({interval})"))
                LOG.info("skip %s — already claimed (%s)", name, interval)
                continue

            status_code = claim_item(client, token, sku)
            if status_code in (200, 201, 204):
                results.append(ClaimResult(name, sku, "ok", "수집 완료"))
                LOG.info("claimed %s", name)
            elif status_code == 422:
                results.append(ClaimResult(name, sku, "limit", "한도 도달"))
                LOG.info("limit %s", name)
            else:
                results.append(ClaimResult(name, sku, "error", f"HTTP {status_code}"))
                LOG.warning("error %s — HTTP %s", name, status_code)

    return results


def format_message(user_results: dict[str, list[ClaimResult]]) -> str:
    icons = {"ok": "✅", "skip": "⏭️", "limit": "⏭️", "error": "⚠️"}
    sections: list[str] = []
    for label, results in user_results.items():
        lines = [f"{icons.get(r.status, '•')} {r.name} — {r.detail}" for r in results]
        sections.append(f"👤 {label}\n" + "\n".join(lines))
    ts = datetime.now(tz=KST).strftime("%Y-%m-%d %H:%M KST")
    return "🎁 Idle Outpost 데일리 보너스\n\n" + "\n\n".join(sections) + f"\n\n📅 {ts}"


def notify_slack(message: str) -> None:
    webhook = os.getenv("IDLE_OUTPOST_SLACK_WEBHOOK", "").strip()
    if not webhook:
        print(message)
        return
    try:
        resp = httpx.post(webhook, json={"text": message}, timeout=10.0)
        resp.raise_for_status()
        LOG.info("slack sent")
    except httpx.HTTPError as exc:
        webhook_host = urlparse(webhook).netloc or "unknown-host"
        LOG.warning("slack failed (host=%s): %s", webhook_host, exc)
        print(message)


def run_claim(json_mode: bool = False) -> int:
    """Execute daily claim for all configured users. Returns exit code."""
    user_ids = get_user_ids()
    if not user_ids:
        LOG.error("IDLE_OUTPOST_USER_IDS not set")
        return 1

    user_results: dict[str, list[ClaimResult]] = {}
    for idx, uid in enumerate(user_ids, start=1):
        label = f"Account {idx}"
        try:
            user_results[label] = claim_all(uid)
        except httpx.HTTPError as exc:
            LOG.error("%s HTTP error: %s", label, exc)
            user_results[label] = [ClaimResult("login", "", "error", str(exc))]

    message = format_message(user_results)

    if json_mode:
        flat = {k: [asdict(r) for r in v] for k, v in user_results.items()}
        print(json.dumps({"message": message, "results": flat}, ensure_ascii=False))
    else:
        notify_slack(message)

    return 0


def main() -> int:
    load_dotenv()
    logging.basicConfig(
        level=logging.DEBUG if "--verbose" in sys.argv else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return run_claim(json_mode="--json" in sys.argv)


if __name__ == "__main__":
    sys.exit(main())
