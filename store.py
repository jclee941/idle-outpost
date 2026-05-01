from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import TypedDict

from scraper import Code

STORE_DIR = Path.home() / ".local" / "share" / "idle-outpost-codes"
STORE_PATH = STORE_DIR / "codes.json"
LOGGER = logging.getLogger(__name__)


class StoreEntry(TypedDict):
    code_text: str
    first_seen: str
    source: str
    redeemed: bool
    redeem_result: str | None


class StorePayload(TypedDict):
    codes: dict[str, StoreEntry]


def get_new_codes(scraped: list[Code]) -> list[Code]:
    payload = _load_store()
    known_codes = set(payload["codes"].keys())
    return [code for code in scraped if code.code_text not in known_codes]


def get_retryable_codes() -> list[Code]:
    payload = _load_store()
    retryable: list[Code] = []

    for entry in payload["codes"].values():
        if entry["redeemed"]:
            continue

        retryable.append(
            Code(
                code_text=entry["code_text"],
                source_url=entry["source"],
                scraped_at=_parse_datetime(entry["first_seen"]),
            )
        )

    return retryable


def save_codes(codes: list[Code]) -> None:
    payload = _load_store()
    store_codes = payload["codes"]

    for code in codes:
        if code.code_text in store_codes:
            existing = store_codes[code.code_text]
            existing.setdefault("source", code.source_url)
            continue

        store_codes[code.code_text] = {
            "code_text": code.code_text,
            "first_seen": _isoformat(code.scraped_at),
            "source": code.source_url,
            "redeemed": False,
            "redeem_result": None,
        }

    _write_store(payload)


def mark_redeem_result(code_text: str, redeemed: bool, redeem_result: str) -> None:
    payload = _load_store()
    store_codes = payload["codes"]
    entry = store_codes.get(code_text)
    if entry is None:
        new_entry: StoreEntry = {
            "code_text": code_text,
            "first_seen": _isoformat(datetime.now(timezone.utc)),
            "source": "",
            "redeemed": False,
            "redeem_result": None,
        }
        store_codes[code_text] = new_entry
        entry = new_entry

    entry["redeemed"] = redeemed
    entry["redeem_result"] = redeem_result
    _write_store(payload)


def list_all() -> list[StoreEntry]:
    payload = _load_store()
    entries = list(payload["codes"].values())
    return sorted(entries, key=lambda item: item["first_seen"], reverse=True)


def _load_store() -> StorePayload:
    if not STORE_PATH.exists():
        return {"codes": {}}

    try:
        raw = json.loads(STORE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        LOGGER.warning("store file is invalid JSON, using empty state: %s", STORE_PATH)
        return {"codes": {}}

    if not isinstance(raw, dict):
        return {"codes": {}}

    raw_codes = raw.get("codes")
    if not isinstance(raw_codes, dict):
        return {"codes": {}}

    normalized: dict[str, StoreEntry] = {}
    for code_text, entry in raw_codes.items():
        if not isinstance(code_text, str) or not isinstance(entry, dict):
            continue

        normalized_entry: StoreEntry = {
            "code_text": str(entry.get("code_text", code_text)),
            "first_seen": str(entry.get("first_seen", "")),
            "source": str(entry.get("source", "")),
            "redeemed": bool(entry.get("redeemed", False)),
            "redeem_result": _normalize_optional_string(entry.get("redeem_result")),
        }
        normalized[code_text] = normalized_entry

    return {"codes": normalized}


def _write_store(payload: StorePayload) -> None:
    STORE_DIR.mkdir(parents=True, exist_ok=True)
    _ = STORE_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _isoformat(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat()


def _normalize_optional_string(value: object) -> str | None:
    if value is None:
        return None
    return str(value)


def _parse_datetime(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return datetime.now(timezone.utc)

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
