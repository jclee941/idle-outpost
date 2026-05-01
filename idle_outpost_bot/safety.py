from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .actions import TapAction, tap
from .vision import Ocr, OcrHit, find_text, grab_screenshot, parse_stylized_number

if TYPE_CHECKING:
    from appium.webdriver.webdriver import WebDriver

LOGGER = logging.getLogger(__name__)

CLOSE_WORDS: tuple[str, ...] = (
    "닫기", "취소", "나중에", "다음에요", "내일 알려주세요", "확인",
    "건너뛰기", "skip", "Skip", "Cancel", "Close", "Later", "OK",
)

DANGER_WORDS: tuple[str, ...] = (
    "돼지 저금통", "Piggy", "구독", "Subscribe", "Subscription",
    "구매", "Purchase", "Buy ", "구매 확정",
    "서버 전환", "Switch Server", "계정 전환", "Switch Account",
    "이용권", "AdTicket", "Ad Ticket",
    "보석으로 구매", "Buy with diamonds", "다이아몬드",
    "Power Pack", "Starter Pack", "Pack",
    "$", "₩", "€",
)

ACTIONABLE_WORDS: tuple[str, ...] = (
    "수령", "모두 수령", "Claim", "광고 보기", "Watch",
    "돌리기", "Spin", "받기", "Free",
)

ABSOLUTE_X_FALLBACKS: tuple[tuple[int, int], ...] = (
    (63, 1889),
    (1020, 130),
    (1000, 200),
    (815, 809),
    (50, 130),
    (540, 2200),
    (154, 1229),
    (74, 1239),
    (88, 1253),
)

MAIN_NAV_KEYWORDS: tuple[str, ...] = ("거래", "전투")
GAME_PACKAGE = "com.rockbite.zombieoutpost"
GAME_ACTIVITY = "com.rockbite.engine.AndroidLauncher"


@dataclass(frozen=True)
class Snapshot:
    png: bytes
    hits: list[OcrHit]
    ts: float

    def find(self, needle: str, min_conf: float = 0.6) -> OcrHit | None:
        return find_text(self.hits, needle, min_conf)

    def find_any(self, needles: tuple[str, ...], min_conf: float = 0.6) -> OcrHit | None:
        for n in needles:
            hit = self.find(n, min_conf)
            if hit is not None:
                return hit
        return None

    def has_text(self, needle: str, min_conf: float = 0.6) -> bool:
        return self.find(needle, min_conf) is not None

    def has_any(self, needles: tuple[str, ...], min_conf: float = 0.6) -> bool:
        return self.find_any(needles, min_conf) is not None

    def coin_value(self) -> int | None:
        for h in self.hits:
            if h.confidence < 0.6:
                continue
            if h.cx > 700 or h.cy > 200:
                continue
            value = parse_stylized_number(h.text)
            if value and value >= 1000:
                return value
        return None


def capture(driver: "WebDriver", ocr: Ocr) -> Snapshot:
    png = grab_screenshot(driver)
    hits = ocr.read(png)
    return Snapshot(png=png, hits=hits, ts=time.monotonic())


def detect_mode(driver: "WebDriver", snap: Snapshot) -> str:
    try:
        pkg = driver.current_package
    except Exception:
        pkg = None
    if pkg and pkg != GAME_PACKAGE:
        return "external"

    central_hits = [h for h in snap.hits if 200 < h.cy < 2000 and h.confidence >= 0.6]
    central_texts = " ".join(h.text for h in central_hits)
    for kw in (*ACTIONABLE_WORDS, *CLOSE_WORDS, *DANGER_WORDS):
        if kw in central_texts:
            return "dialog"

    for h in snap.hits:
        if h.cy > 1700 and any(kw in h.text for kw in MAIN_NAV_KEYWORDS):
            return "main"

    return "main"


@dataclass
class SafeCloseResult:
    closed: bool
    method: str = ""
    candidates_tried: int = 0


def safe_close(
    driver: "WebDriver",
    ocr: Ocr,
    initial_snap: Snapshot,
    *,
    dry_run: bool = False,
    verify_timeout_s: float = 1.5,
) -> SafeCloseResult:
    if detect_mode(driver, initial_snap) != "dialog":
        return SafeCloseResult(closed=True, method="not-a-dialog")

    candidates: list[tuple[int, int, str]] = []

    for h in initial_snap.hits:
        if h.confidence < 0.55:
            continue
        for word in CLOSE_WORDS:
            if word in h.text:
                if h.cx > 0 and h.cy > 0:
                    candidates.append((h.cx, h.cy, f"ocr:{word}"))
                break

    for x, y in ABSOLUTE_X_FALLBACKS:
        candidates.append((x, y, f"abs:{x},{y}"))

    tried = 0
    for x, y, method in candidates:
        if x <= 0 or y <= 0:
            continue
        tried += 1
        tap(driver, TapAction(x=x, y=y, label=f"safe_close[{method}]"), dry_run=dry_run)
        time.sleep(0.6)
        if dry_run:
            return SafeCloseResult(closed=True, method=f"dry:{method}", candidates_tried=tried)

        deadline = time.monotonic() + verify_timeout_s
        while time.monotonic() < deadline:
            snap = capture(driver, ocr)
            if detect_mode(driver, snap) != "dialog":
                LOGGER.info("safe_close: closed via %s after %d attempts", method, tried)
                return SafeCloseResult(closed=True, method=method, candidates_tried=tried)
            time.sleep(0.4)

    LOGGER.warning("safe_close: failed after %d attempts", tried)
    return SafeCloseResult(closed=False, candidates_tried=tried)


def handle_danger_dialog(
    driver: "WebDriver",
    ocr: Ocr,
    snap: Snapshot,
    *,
    dry_run: bool = False,
) -> bool:
    danger_hit = None
    for h in snap.hits:
        if h.confidence < 0.55:
            continue
        for word in DANGER_WORDS:
            if word in h.text:
                danger_hit = h
                break
        if danger_hit is not None:
            break
    if danger_hit is None:
        return False

    LOGGER.warning("DANGER dialog: '%s' at (%d,%d) — closing",
                   danger_hit.text, danger_hit.cx, danger_hit.cy)
    safe_close(driver, ocr, snap, dry_run=dry_run)
    return True


def handle_external_overlay(
    driver: "WebDriver",
    ocr: Ocr,
    snap: Snapshot,
    *,
    dry_run: bool = False,
) -> bool:
    try:
        current = driver.current_package
    except Exception:
        current = None
    if current == GAME_PACKAGE:
        return False
    if current == "com.android.vending":
        LOGGER.info("Play Store opened (likely from ad CTA) — pressing BACK to return")
        if dry_run:
            return True
        try:
            driver.execute_script("mobile: pressKey", {"keycode": 4})
        except Exception:
            try:
                driver.press_keycode(4)
            except Exception:
                pass
        time.sleep(2.0)
        return True
    LOGGER.warning("Game lost foreground (current=%s) — restarting", current)
    if dry_run:
        return True
    try:
        driver.execute_script("mobile: shell", {
            "command": "am",
            "args": ["start", "-n", f"{GAME_PACKAGE}/{GAME_ACTIVITY}"],
        })
    except Exception as exc:
        LOGGER.error("am start via Appium failed: %s — try start_activity", exc)
        try:
            driver.start_activity(GAME_PACKAGE, GAME_ACTIVITY)
        except Exception as exc2:
            LOGGER.error("start_activity also failed: %s", exc2)
            return False
    time.sleep(8.0)
    return True


def watch_ad_flow(
    driver: "WebDriver",
    ocr: Ocr,
    *,
    max_seconds: int = 90,
    dry_run: bool = False,
) -> tuple[bool, str]:
    if dry_run:
        return True, "dry-run"
    deadline = time.monotonic() + max_seconds
    closed_play_store = False
    pressed_back_after_ad = False
    while time.monotonic() < deadline:
        time.sleep(3.0)
        try:
            pkg = driver.current_package
        except Exception:
            pkg = None
        try:
            activity = driver.current_activity
        except Exception:
            activity = None
        if pkg == "com.android.vending" and not closed_play_store:
            LOGGER.info("ad CTA opened Play Store - tapping X")
            for x, y in ((66, 156), (1001, 594), (90, 1473)):
                tap(driver, TapAction(x=x, y=y, label=f"play_store_close_{x},{y}"))
                time.sleep(0.6)
                try:
                    if driver.current_package != "com.android.vending":
                        break
                except Exception:
                    break
            closed_play_store = True
            continue
        if activity and "AdActivity" in activity and not pressed_back_after_ad:
            LOGGER.info("Ad finished, in AdActivity - pressing BACK")
            try:
                driver.execute_script("mobile: pressKey", {"keycode": 4})
            except Exception:
                try:
                    driver.press_keycode(4)
                except Exception:
                    pass
            pressed_back_after_ad = True
            time.sleep(2.0)
            continue
        if pkg == GAME_PACKAGE and (not activity or "AdActivity" not in activity):
            return True, f"returned to game (waited={int(time.monotonic()-(deadline-max_seconds))}s)"
    return False, f"ad watch did not finish in {max_seconds}s"


@dataclass
class Postcondition:
    kind: str
    text: str = ""
    min_delta: int = 0

    def evaluate(self, before: Snapshot, after: Snapshot) -> tuple[bool, str]:
        if self.kind == "dialog_gone":
            had = before.has_any(ACTIONABLE_WORDS) or before.has_any(CLOSE_WORDS)
            still = after.has_any(ACTIONABLE_WORDS) or after.has_any(CLOSE_WORDS)
            if had and not still:
                return True, "dialog gone"
            if not had:
                return False, "no dialog in before"
            return False, "dialog still present"

        if self.kind == "text_disappeared":
            had = before.has_text(self.text)
            still = after.has_text(self.text)
            if had and not still:
                return True, f"'{self.text}' disappeared"
            if not had:
                return False, f"'{self.text}' was not in before"
            return False, f"'{self.text}' still present"

        if self.kind == "text_appeared":
            had = before.has_text(self.text)
            now = after.has_text(self.text)
            if not had and now:
                return True, f"'{self.text}' appeared"
            if had:
                return False, f"'{self.text}' was already present"
            return False, f"'{self.text}' did not appear"

        if self.kind == "coin_increased":
            b = before.coin_value()
            a = after.coin_value()
            if b is None or a is None:
                return False, f"coin parse failed (before={b}, after={a})"
            if a - b >= self.min_delta:
                return True, f"coin {b}→{a} (Δ{a-b})"
            return False, f"coin {b}→{a} insufficient (need Δ≥{self.min_delta})"

        return False, f"unknown kind: {self.kind}"


def verify(
    postconditions: list[Postcondition],
    before: Snapshot,
    after: Snapshot,
) -> tuple[bool, str]:
    if not postconditions:
        return False, "no postconditions"
    reasons: list[str] = []
    for cond in postconditions:
        ok, reason = cond.evaluate(before, after)
        if ok:
            return True, reason
        reasons.append(f"{cond.kind}: {reason}")
    return False, "; ".join(reasons)
