from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .vision import Ocr, OcrHit, Region, find_text, grab_screenshot

if TYPE_CHECKING:
    from appium.webdriver.webdriver import WebDriver

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class TapAction:
    x: int
    y: int
    label: str = ""


def tap(driver: "WebDriver", action: TapAction, *, dry_run: bool = False) -> None:
    LOGGER.info("tap %s at (%d,%d) dry_run=%s", action.label or "?", action.x, action.y, dry_run)
    if dry_run:
        return
    driver.execute_script("mobile: clickGesture", {"x": action.x, "y": action.y})


def swipe(
    driver: "WebDriver",
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    duration_ms: int = 300,
    *,
    dry_run: bool = False,
) -> None:
    LOGGER.info(
        "swipe (%d,%d)->(%d,%d) %dms dry_run=%s",
        start_x, start_y, end_x, end_y, duration_ms, dry_run,
    )
    if dry_run:
        return
    driver.execute_script(
        "mobile: swipeGesture",
        {
            "left": min(start_x, end_x),
            "top": min(start_y, end_y),
            "width": abs(end_x - start_x) or 1,
            "height": abs(end_y - start_y) or 1,
            "direction": "up" if end_y < start_y else "down",
            "percent": 0.9,
        },
    )


def wait_for_text(
    driver: "WebDriver",
    ocr: Ocr,
    needle: str,
    region: Region | None = None,
    timeout_seconds: float = 15.0,
    poll_seconds: float = 1.0,
) -> OcrHit | None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        png = grab_screenshot(driver)
        hits = ocr.read(png, region)
        match = find_text(hits, needle)
        if match is not None:
            return match
        time.sleep(poll_seconds)
    return None
