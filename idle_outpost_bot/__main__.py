from __future__ import annotations

import argparse
import json
import logging
import sys
from typing import NoReturn

from dotenv import load_dotenv

from .config_loader import load_config
from .discover import discover
from .settings import Settings
from .state import load_state, save_state
from .vision import Ocr


class CLIError(Exception):
    pass


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise CLIError(message)


def _build_parser() -> argparse.ArgumentParser:
    parser = _Parser(prog="idle-outpost-bot", description="Idle Outpost Android automation")
    _ = parser.add_argument("--verbose", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)

    _ = sub.add_parser("run", help="run the automation loop forever")
    _ = sub.add_parser("once", help="run a single iteration")
    cal = sub.add_parser("calibrate", help="dump current screen + OCR for config tuning")
    _ = cal.add_argument("--label", default="current", help="output filename label")
    _ = cal.add_argument("--no-ocr", action="store_true", help="skip OCR (faster, no PaddleOCR)")
    _ = sub.add_parser("status", help="print current bot state JSON")
    _ = sub.add_parser("discover", help="find Idle Outpost package on the connected device")
    _ = sub.add_parser("config-check", help="load YAML config and print summary")
    return parser


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    if not verbose:
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)


def _handle_status(settings: Settings) -> int:
    state = load_state(settings.state_path)
    print(
        json.dumps(
            {
                "iterations": state.iterations,
                "last_iteration_at": state.last_iteration_at,
                "prestige_count": state.prestige_count,
                "last_prestige_at": state.last_prestige_at,
                "ad_claims_today": state.ad_claims_today,
                "ad_claims_date": state.ad_claims_date,
                "task_runs": state.task_runs,
                "last_error": state.last_error,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


def _handle_discover(settings: Settings) -> int:
    found = discover(settings.device_name)
    if not found:
        print("no Idle Outpost packages detected on device", file=sys.stderr)
        return 1
    for cand in found:
        print(f"package={cand.package}  activity={cand.main_activity or '(unknown)'}")
    return 0


def _handle_config_check(settings: Settings) -> int:
    if not settings.config_path.exists():
        print(f"config not found: {settings.config_path}", file=sys.stderr)
        return 1
    config = load_config(settings.config_path)
    summary = {
        name: {
            "detect_text": s.detect_text,
            "buttons": list(s.buttons.keys()),
            "regions": list(s.regions.keys()),
        }
        for name, s in config.screens.items()
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


def _handle_calibrate(settings: Settings, label: str, no_ocr: bool) -> int:
    from .calibrate import dump_screen
    from .driver import session

    ocr = None if no_ocr else Ocr(lang=settings.ocr_lang)
    with session(settings) as driver:
        png_path, yaml_path = dump_screen(driver, ocr, settings.screenshot_dir, label)
    print(f"screenshot: {png_path}")
    if yaml_path is not None:
        print(f"ocr dump:   {yaml_path}")
    return 0


def _handle_once(settings: Settings) -> int:
    from .driver import session
    from .loop import run_once

    if not settings.config_path.exists():
        print(f"config not found: {settings.config_path}", file=sys.stderr)
        return 1
    config = load_config(settings.config_path)
    state = load_state(settings.state_path)
    ocr = Ocr(lang=settings.ocr_lang)
    with session(settings) as driver:
        actions = run_once(driver, settings, config, ocr, state)
    save_state(settings.state_path, state)
    if actions:
        for line in actions:
            print(line)
    else:
        print("no actions executed this iteration")
    return 0


def _handle_run(settings: Settings) -> int:
    from .driver import session
    from .loop import run_loop

    if not settings.config_path.exists():
        print(f"config not found: {settings.config_path}", file=sys.stderr)
        return 1
    config = load_config(settings.config_path)
    state = load_state(settings.state_path)
    ocr = Ocr(lang=settings.ocr_lang)
    with session(settings) as driver:
        run_loop(driver, settings, config, ocr, state)
    return 0


def main() -> int:
    _ = load_dotenv()
    parser = _build_parser()
    try:
        args = parser.parse_args()
    except CLIError as exc:
        parser.print_usage(sys.stderr)
        print(f"error: {exc}", file=sys.stderr)
        return 2

    _configure_logging(bool(getattr(args, "verbose", False)))
    settings = Settings.from_env()

    command = str(getattr(args, "command", ""))
    try:
        if command == "status":
            return _handle_status(settings)
        if command == "discover":
            return _handle_discover(settings)
        if command == "config-check":
            return _handle_config_check(settings)
        if command == "calibrate":
            return _handle_calibrate(
                settings,
                str(getattr(args, "label", "current")),
                bool(getattr(args, "no_ocr", False)),
            )
        if command == "once":
            return _handle_once(settings)
        if command == "run":
            return _handle_run(settings)
    except Exception as exc:  # noqa: BLE001
        logging.exception("command failed: %s", exc)
        return 1
    return 1


if __name__ == "__main__":
    sys.exit(main())
