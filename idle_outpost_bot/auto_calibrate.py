from __future__ import annotations

import argparse
import json
import logging
import sys
from collections import Counter
from pathlib import Path

import yaml

from .settings import Settings
from .vision import Ocr

LOGGER = logging.getLogger(__name__)


def _ocr_directory(ocr: Ocr, image_dir: Path) -> dict[str, list[dict[str, object]]]:
    results: dict[str, list[dict[str, object]]] = {}
    for png in sorted(image_dir.glob("*.png")):
        png_bytes = png.read_bytes()
        hits = ocr.read(png_bytes)
        results[png.name] = [
            {"text": h.text, "confidence": round(h.confidence, 3)} for h in hits
        ]
        LOGGER.info("%s: %d hits", png.name, len(hits))
    return results


def _classify_screen(texts: list[str]) -> str:
    joined = " ".join(t.lower() for t in texts)
    rules: list[tuple[str, list[str]]] = [
        ("daily_reward_dialog", ["daily reward", "day 1", "day 2", "데일리"]),
        ("ad_reward_dialog", ["watch ad", "free", "광고"]),
        ("upgrade_panel", ["upgrade", "level up", "업그레이드"]),
        ("manager_panel", ["manager", "hire", "매니저"]),
        ("fight_mode", ["fight", "loot", "shovel", "전투", "삽"]),
        ("tasks_screen", ["tasks", "daily", "weekly", "임무"]),
        ("event_screen", ["event", "limited", "이벤트"]),
        ("connection_lost", ["no internet", "reconnect", "연결"]),
        ("update_required", ["update", "new version", "업데이트"]),
        ("main_screen", ["coins", "gems", "scrap", "trade", "코인"]),
    ]
    for name, kws in rules:
        if any(kw in joined for kw in kws):
            return name
    return "unknown"


def write_yaml_skeleton(ocr_dump: dict[str, list[dict[str, object]]], out_path: Path) -> None:
    screens: dict[str, dict[str, object]] = {}
    for frame, hits in ocr_dump.items():
        texts = [str(h["text"]) for h in hits]
        label = _classify_screen(texts)
        if label not in screens:
            screens[label] = {
                "detect_text": "",
                "detect_region": None,
                "regions": {},
                "buttons": {},
                "_observed_in": [frame],
                "_top_texts": Counter(texts).most_common(10),
            }
        else:
            obs = screens[label]["_observed_in"]
            assert isinstance(obs, list)
            obs.append(frame)
    payload = {"screens": screens}
    out_path.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8")
    LOGGER.info("wrote %s with %d screens", out_path, len(screens))


def main() -> int:
    parser = argparse.ArgumentParser(prog="auto_calibrate")
    _ = parser.add_argument("--frames", required=True, help="dir of PNG screenshots")
    _ = parser.add_argument("--out", required=True, help="output YAML path")
    _ = parser.add_argument("--dump-json", help="write raw OCR JSON here")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
    settings = Settings.from_env()
    ocr = Ocr(lang=settings.ocr_lang)

    frames_dir = Path(args.frames)
    if not frames_dir.is_dir():
        print(f"frames dir not found: {frames_dir}", file=sys.stderr)
        return 1

    ocr_dump = _ocr_directory(ocr, frames_dir)
    if args.dump_json:
        Path(args.dump_json).write_text(json.dumps(ocr_dump, ensure_ascii=False, indent=2), encoding="utf-8")
    write_yaml_skeleton(ocr_dump, Path(args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
