from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

LOGGER = logging.getLogger(__name__)


@dataclass
class BotState:
    last_iteration_at: str | None = None
    iterations: int = 0
    last_prestige_at: str | None = None
    prestige_count: int = 0
    ad_claims_today: int = 0
    ad_claims_date: str | None = None
    last_error: str | None = None
    task_runs: dict[str, int] = field(default_factory=dict)


def _state_to_dict(state: BotState) -> dict[str, object]:
    return {
        "last_iteration_at": state.last_iteration_at,
        "iterations": state.iterations,
        "last_prestige_at": state.last_prestige_at,
        "prestige_count": state.prestige_count,
        "ad_claims_today": state.ad_claims_today,
        "ad_claims_date": state.ad_claims_date,
        "last_error": state.last_error,
        "task_runs": dict(state.task_runs),
    }


def load_state(path: Path) -> BotState:
    if not path.exists():
        return BotState()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        LOGGER.warning("state file invalid JSON at %s, starting fresh", path)
        return BotState()
    if not isinstance(raw, dict):
        return BotState()
    task_runs_raw = raw.get("task_runs", {})
    task_runs = {
        str(k): int(v) for k, v in task_runs_raw.items() if isinstance(task_runs_raw, dict)
    } if isinstance(task_runs_raw, dict) else {}
    return BotState(
        last_iteration_at=_optional_str(raw.get("last_iteration_at")),
        iterations=int(raw.get("iterations", 0)),
        last_prestige_at=_optional_str(raw.get("last_prestige_at")),
        prestige_count=int(raw.get("prestige_count", 0)),
        ad_claims_today=int(raw.get("ad_claims_today", 0)),
        ad_claims_date=_optional_str(raw.get("ad_claims_date")),
        last_error=_optional_str(raw.get("last_error")),
        task_runs=task_runs,
    )


def save_state(path: Path, state: BotState) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = _state_to_dict(state)
    _ = path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def today_utc() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def reset_daily_counters_if_needed(state: BotState) -> None:
    today = today_utc()
    if state.ad_claims_date != today:
        state.ad_claims_date = today
        state.ad_claims_today = 0


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    return str(value)
