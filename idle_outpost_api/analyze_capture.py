from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger(__name__)


def _safe_json(text: str) -> Any | None:
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return None


def _summarize_keys(obj: Any, prefix: str = "") -> set[str]:
    keys: set[str] = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            path = f"{prefix}.{k}" if prefix else k
            keys.add(path)
            keys |= _summarize_keys(v, path)
    elif isinstance(obj, list) and obj:
        keys |= _summarize_keys(obj[0], prefix + "[]")
    return keys


def _redact(text: str) -> str:
    """Remove Authorization headers and token-like values from text."""
    if not text:
        return text
    redacted = re.sub(r'Bearer\s+[A-Za-z0-9_-]+', 'Bearer <REDACTED>', text)
    redacted = re.sub(r'"token"\s*:\s*"[^"]+"', '"token": "<REDACTED>"', redacted)
    return redacted


def analyze(flows_path: Path) -> dict[str, Any]:
    from mitmproxy.io import FlowReader

    by_endpoint: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"count": 0, "methods": Counter(), "status_codes": Counter(),
                 "auth_header_seen": False, "request_keys": set(), "response_keys": set(),
                 "sample_request": None, "sample_response": None}
    )

    with flows_path.open("rb") as fh:
        reader = FlowReader(fh)
        for flow in reader.stream():
            req = getattr(flow, "request", None)
            resp = getattr(flow, "response", None)
            if req is None:
                continue
            host = req.host or ""
            if not any(d in host for d in ("rockbitegames", "appquantum")):
                continue
            key = f"{req.method} https://{host}{req.path.split('?')[0]}"
            entry = by_endpoint[key]
            entry["count"] += 1
            entry["methods"][req.method] += 1
            if resp is not None:
                entry["status_codes"][resp.status_code] += 1

            auth = req.headers.get("Authorization", "") if req.headers else ""
            if auth.startswith("Bearer "):
                entry["auth_header_seen"] = True

            req_text = req.get_text() or ""
            req_json = _safe_json(req_text)
            if req_json is not None:
                entry["request_keys"] |= _summarize_keys(req_json)
            if entry["sample_request"] is None:
                entry["sample_request"] = _redact(req_text)[:500]

            if resp is not None:
                resp_text = resp.get_text() or ""
                resp_json = _safe_json(resp_text)
                if resp_json is not None:
                    entry["response_keys"] |= _summarize_keys(resp_json)
                if entry["sample_response"] is None:
                    entry["sample_response"] = _redact(resp_text)[:500]

    out = {
        "total_endpoints": len(by_endpoint),
        "auth_required_count": sum(
            1 for d in by_endpoint.values() if d["auth_header_seen"]
        ),
        "endpoints": {},
    }
    for ep, data in sorted(by_endpoint.items(), key=lambda kv: -kv[1]["count"]):
        out["endpoints"][ep] = {
            "count": data["count"],
            "methods": dict(data["methods"]),
            "status_codes": dict(data["status_codes"]),
            "auth_required": data["auth_header_seen"],
            "request_keys": sorted(data["request_keys"]),
            "response_keys": sorted(data["response_keys"]),
            "sample_request": data["sample_request"],
            "sample_response": data["sample_response"],
        }
    return out


def main() -> int:
    parser = argparse.ArgumentParser(prog="analyze_capture")
    _ = parser.add_argument("--flows", default="/var/log/idle-outpost/flows.bin")
    _ = parser.add_argument("--out", default="-")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    flows = Path(args.flows)
    if not flows.exists() or flows.stat().st_size == 0:
        print(f"no flows yet at {flows}", file=sys.stderr)
        return 1
    result = analyze(flows)
    text = json.dumps(result, indent=2, ensure_ascii=False, default=str)
    if args.out == "-":
        print(text)
    else:
        Path(args.out).write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
