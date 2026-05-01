from __future__ import annotations

import argparse
import logging
import sys
from typing import NoReturn

from dotenv import load_dotenv

from claim_api import ClaimResult, claim_all, format_message, notify_slack
from notifier import notify_new_codes
from redeemer import attempt_redeem
from scraper import Code, scrape_codes_with_metadata, source_name
from store import get_new_codes, get_retryable_codes, list_all, mark_redeem_result, save_codes


class CLIArgumentError(Exception):
    pass


class CLIArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise CLIArgumentError(message)


def build_parser() -> argparse.ArgumentParser:
    parser = CLIArgumentParser(description="Monitor Idle Outpost promo codes")
    _ = parser.add_argument("--verbose", action="store_true", help="enable debug logging")

    subparsers = parser.add_subparsers(dest="command", required=True)
    _ = subparsers.add_parser("check", help="scrape, detect new codes, notify, and attempt redeem")
    claim_parser = subparsers.add_parser("claim", help="claim daily free giveaway items")
    _ = claim_parser.add_argument("--json", action="store_true", help="output JSON")
    _ = subparsers.add_parser("list", help="show all known codes with status")
    _ = subparsers.add_parser("scrape", help="scrape active codes and print them without saving")
    return parser


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")
    if not verbose:
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)


def _run_scrape() -> tuple[list[Code], int]:
    result = scrape_codes_with_metadata()
    if result.successful_sources == 0:
        logging.error("all code sources failed")
        return result.codes, 1
    return result.codes, 0


def handle_check() -> int:
    scraped, scrape_status = _run_scrape()
    if scrape_status != 0:
        return scrape_status

    new_codes = get_new_codes(scraped)
    if new_codes:
        save_codes(new_codes)
        notify_new_codes(new_codes)

    retryable_codes = get_retryable_codes()
    if not new_codes and not retryable_codes:
        print("No new codes found.")
        return 0

    if not new_codes and retryable_codes:
        print("No new codes found. Retrying pending codes.")

    for code in retryable_codes:
        attempt = attempt_redeem(code)
        mark_redeem_result(code.code_text, redeemed=attempt.redeemed, redeem_result=attempt.message)
        print(f"{code.code_text}: {attempt.message}")

    return 0


def handle_list() -> int:
    entries = list_all()
    if not entries:
        print("No known codes.")
        return 0

    for entry in entries:
        status = _format_status(entry.get("redeemed"), entry.get("redeem_result"))
        result = entry.get("redeem_result") or "-"
        source_url = entry.get("source")
        source_label = (
            source_name(source_url) if isinstance(source_url, str) and source_url else "-"
        )
        print(
            f"{entry['code_text']} | first_seen={entry['first_seen']} | "
            f"source={source_label} | status={status} | result={result}"
        )

    return 0


def handle_scrape() -> int:
    codes, scrape_status = _run_scrape()
    if scrape_status != 0:
        return scrape_status
    if not codes:
        print("No codes scraped.")
        return 0

    for code in codes:
        print(f"{code.code_text} | {source_name(code.source_url)} | {code.scraped_at.isoformat()}")

    return 0


def handle_claim(json_mode: bool) -> int:
    from auth import get_user_ids

    user_ids = get_user_ids()
    if not user_ids:
        logging.error("IDLE_OUTPOST_USER_IDS not set")
        return 1

    user_results: dict[str, list[ClaimResult]] = {}
    for idx, uid in enumerate(user_ids, start=1):
        label = f"Account {idx}"
        try:
            user_results[label] = claim_all(uid)
        except Exception as exc:
            logging.error("%s error: %s", label, exc)
            user_results[label] = [ClaimResult("login", "", "error", str(exc))]

    message = format_message(user_results)

    if json_mode:
        import json
        from dataclasses import asdict

        flat = {k: [asdict(r) for r in v] for k, v in user_results.items()}
        print(json.dumps({"message": message, "results": flat}, ensure_ascii=False))
    else:
        notify_slack(message)

    return 0


def _format_status(redeemed: object, redeem_result: object) -> str:
    if redeemed is True:
        return "redeemed"

    result_text = str(redeem_result or "").lower()
    if not result_text:
        return "pending"
    if "skipped" in result_text:
        return "skipped"
    if "failed" in result_text or "error" in result_text or "blocked" in result_text:
        return "failed"
    return "pending"


def main() -> int:
    load_dotenv()
    parser = build_parser()
    try:
        args = parser.parse_args()
    except CLIArgumentError as exc:
        parser.print_usage(sys.stderr)
        print(f"error: {exc}", file=sys.stderr)
        return 1

    verbose = bool(getattr(args, "verbose", False))
    command = str(getattr(args, "command", ""))
    configure_logging(verbose)

    try:
        if command == "check":
            return handle_check()
        if command == "claim":
            return handle_claim(json_mode=bool(getattr(args, "json", False)))
        if command == "list":
            return handle_list()
        if command == "scrape":
            return handle_scrape()
    except Exception as exc:  # pragma: no cover - CLI safety net
        logging.exception("command failed: %s", exc)
        return 1

    return 1


if __name__ == "__main__":
    sys.exit(main())
