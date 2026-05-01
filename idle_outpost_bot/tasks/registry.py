from __future__ import annotations

import logging
import random
import time

from ..actions import TapAction, tap
from ..safety import (
    ACTIONABLE_WORDS,
    CLOSE_WORDS,
    Postcondition,
    Snapshot,
    capture,
    safe_close,
    watch_ad_flow,
)
from ..vision import find_alert_badges
from .base import Task, TaskContext, TaskResult

LOGGER = logging.getLogger(__name__)

_TAP_JITTER_PX = 12

MAIN_BUTTONS = {
    "inbox": (860, 135),
    "menu": (1030, 131),
    "calendar": (75, 348),
    "wheel": (75, 491),
    "tasks": (75, 636),
    "quest_board": (75, 780),
    "cards": (75, 936),
    "ad_tv": (77, 1242),
    "right_event": (993, 316),
    "trophy": (1005, 522),
    "pass": (1004, 701),
    "enter_trade": (316, 1890),
    "enter_fight": (760, 1890),
    "event_banner": (548, 365),
}


def _jitter_tap(ctx: TaskContext, x: int, y: int, label: str) -> None:
    jx = random.randint(-_TAP_JITTER_PX, _TAP_JITTER_PX)
    jy = random.randint(-_TAP_JITTER_PX, _TAP_JITTER_PX)
    tap(ctx.driver, TapAction(x=x + jx, y=y + jy, label=label), dry_run=ctx.settings.dry_run)


def _refresh_snapshot(ctx: TaskContext) -> Snapshot:
    snap = capture(ctx.driver, ctx.ocr)
    ctx.snapshot = snap
    return snap


def _tap_main_button(ctx: TaskContext, button_name: str) -> bool:
    coords = MAIN_BUTTONS.get(button_name)
    if not coords:
        return False
    _jitter_tap(ctx, coords[0], coords[1], f"main.{button_name}")
    return True


def _tap_text(ctx: TaskContext, snap: Snapshot, needle: str) -> bool:
    hit = snap.find(needle, min_conf=0.55)
    if hit is None or hit.cx <= 0:
        return False
    _jitter_tap(ctx, hit.cx, hit.cy, f"text:{needle}")
    return True


def _open_and_close(
    ctx: TaskContext,
    button_name: str,
    inner_action: str | None = None,
    settle_s: float = 1.5,
) -> tuple[bool, str]:
    if not _tap_main_button(ctx, button_name):
        return False, f"no button {button_name}"
    time.sleep(settle_s)
    snap = _refresh_snapshot(ctx)
    detail = f"opened {button_name}"
    if inner_action:
        if _tap_text(ctx, snap, inner_action):
            detail += f", tapped '{inner_action}'"
            time.sleep(1.0)
            snap = _refresh_snapshot(ctx)
    safe_close(ctx.driver, ctx.ocr, snap, dry_run=ctx.settings.dry_run)
    time.sleep(0.5)
    return True, detail


def _claim_afk_rewards(ctx: TaskContext) -> TaskResult:
    snap = ctx.snapshot or _refresh_snapshot(ctx)
    if not snap.has_text("수령") and not snap.has_text("Claim"):
        return TaskResult(name="claim_afk_rewards", executed=False, detail="no claim button visible")
    success = _tap_text(ctx, snap, "수령") or _tap_text(ctx, snap, "Claim")
    if not success:
        return TaskResult(name="claim_afk_rewards", executed=False, detail="tap failed")
    time.sleep(1.5)
    return TaskResult(name="claim_afk_rewards", executed=True, detail="tapped 수령")


def _claim_inbox(ctx: TaskContext) -> TaskResult:
    ok, detail = _open_and_close(ctx, "inbox", inner_action="모두 수령", settle_s=1.5)
    return TaskResult(name="claim_inbox", executed=ok, detail=detail)


def _spin_wheel(ctx: TaskContext) -> TaskResult:
    if ctx.state.ad_claims_today >= 30:
        return TaskResult(name="spin_wheel", executed=False, detail="daily ad cap 30 reached")
    if not _tap_main_button(ctx, "wheel"):
        return TaskResult(name="spin_wheel", executed=False, detail="no wheel button")
    time.sleep(3.0)
    snap = _refresh_snapshot(ctx)
    spin_hit = snap.find("돌리기", min_conf=0.55)
    counter_hit = None
    for h in snap.hits:
        if "/3)" in h.text or "/3" in h.text:
            counter_hit = h
            break
    if spin_hit is None:
        safe_close(ctx.driver, ctx.ocr, snap, dry_run=ctx.settings.dry_run)
        return TaskResult(name="spin_wheel", executed=False, detail="not on wheel screen")
    before_counter = counter_hit.text if counter_hit else "?"
    _jitter_tap(ctx, spin_hit.cx, spin_hit.cy, "wheel.spin")
    time.sleep(3.0)
    snap = _refresh_snapshot(ctx)
    if snap.find("광고 보기", min_conf=0.55) is None:
        safe_close(ctx.driver, ctx.ocr, snap, dry_run=ctx.settings.dry_run)
        return TaskResult(name="spin_wheel", executed=False,
                          detail=f"no ad dialog after spin (counter={before_counter})")
    watch_btn = None
    for h in snap.hits:
        if "광고 보기" in h.text and h.cx > 500:
            watch_btn = h
            break
    if watch_btn is None:
        for h in snap.hits:
            if "광고 보기" in h.text:
                watch_btn = h
                break
    if watch_btn is None:
        return TaskResult(name="spin_wheel", executed=False, detail="watch button vanished")
    _jitter_tap(ctx, watch_btn.cx, watch_btn.cy, "wheel.watch_ad")
    LOGGER.info("ad started, watching up to 90s")
    ok, ad_detail = watch_ad_flow(ctx.driver, ctx.ocr, max_seconds=90,
                                   dry_run=ctx.settings.dry_run)
    if not ok:
        return TaskResult(name="spin_wheel", executed=False, detail=f"ad: {ad_detail}")
    ctx.state.ad_claims_today += 1
    time.sleep(2.0)
    after = _refresh_snapshot(ctx)
    cancel_hit = after.find("취소", min_conf=0.55)
    if cancel_hit:
        _jitter_tap(ctx, cancel_hit.cx, cancel_hit.cy, "wheel.cancel_next_ad")
        time.sleep(1.5)
        after = _refresh_snapshot(ctx)
    after_counter = "?"
    for h in after.hits:
        if "/3)" in h.text or "/3" in h.text:
            after_counter = h.text
            break
    _jitter_tap(ctx, 154, 1229, "wheel.close_x")
    time.sleep(1.5)
    detail = f"spun {before_counter}→{after_counter} (ads_today={ctx.state.ad_claims_today})"
    return TaskResult(name="spin_wheel", executed=True, detail=detail)


def _claim_daily_streak(ctx: TaskContext) -> TaskResult:
    snap = ctx.snapshot or _refresh_snapshot(ctx)
    if snap.has_text("일일 연속") or snap.has_text("Daily Streak"):
        if _tap_text(ctx, snap, "수령") or _tap_text(ctx, snap, "Claim"):
            time.sleep(1.5)
            return TaskResult(name="claim_daily_streak", executed=True, detail="streak claimed")
    return TaskResult(name="claim_daily_streak", executed=False, detail="streak dialog not present")


def _claim_daily_quests(ctx: TaskContext) -> TaskResult:
    ok, detail = _open_and_close(ctx, "tasks", inner_action="모두 수령", settle_s=1.5)
    return TaskResult(name="claim_daily_quests", executed=ok, detail=detail)


def _claim_event_rewards(ctx: TaskContext) -> TaskResult:
    ok, detail = _open_and_close(ctx, "calendar", inner_action="수령", settle_s=2.0)
    return TaskResult(name="claim_event_rewards", executed=ok, detail=detail)


def _claim_pass_free(ctx: TaskContext) -> TaskResult:
    ok, detail = _open_and_close(ctx, "quest_board", inner_action="무료", settle_s=2.0)
    return TaskResult(name="claim_pass_free", executed=ok, detail=detail)


def _claim_card_daily(ctx: TaskContext) -> TaskResult:
    ok, detail = _open_and_close(ctx, "cards", inner_action="일일 보상", settle_s=2.0)
    return TaskResult(name="claim_card_daily", executed=ok, detail=detail)


def _claim_offline_earnings(ctx: TaskContext) -> TaskResult:
    snap = ctx.snapshot or _refresh_snapshot(ctx)
    if snap.has_text("오프라인 수입") or snap.has_text("Offline"):
        if _tap_text(ctx, snap, "수령") or _tap_text(ctx, snap, "Claim"):
            time.sleep(1.5)
            return TaskResult(name="claim_offline_earnings", executed=True, detail="offline claimed")
    return TaskResult(name="claim_offline_earnings", executed=False, detail="offline dialog not present")


def _dismiss_blocking_dialog(ctx: TaskContext) -> TaskResult:
    snap = ctx.snapshot or _refresh_snapshot(ctx)
    has_close = snap.has_any(CLOSE_WORDS)
    has_actionable = snap.has_any(ACTIONABLE_WORDS)
    if not (has_close or has_actionable):
        return TaskResult(name="dismiss_blocking_dialog", executed=False, detail="no dialog")
    result = safe_close(ctx.driver, ctx.ocr, snap, dry_run=ctx.settings.dry_run)
    return TaskResult(
        name="dismiss_blocking_dialog",
        executed=result.closed,
        detail=f"method={result.method} tried={result.candidates_tried}",
    )


def _trade_collect_and_send(ctx: TaskContext) -> TaskResult:
    main_btn = ctx.snapshot.find("거래", min_conf=0.7) if ctx.snapshot else None
    if main_btn is None or main_btn.cy < 1700:
        return TaskResult(name="trade_collect", executed=False, detail="거래 button not on main")
    _jitter_tap(ctx, main_btn.cx, main_btn.cy, "main.enter_trade")
    time.sleep(4.0)
    snap = _refresh_snapshot(ctx)
    actions: list[str] = []
    collect_hit = snap.find("수집", min_conf=0.55)
    if collect_hit and snap.has_text("수령 가능"):
        _jitter_tap(ctx, collect_hit.cx, collect_hit.cy, "trade.collect")
        time.sleep(2.5)
        actions.append("collect")
        snap = _refresh_snapshot(ctx)
    confirm_hit = snap.find("확인", min_conf=0.55)
    if confirm_hit:
        _jitter_tap(ctx, confirm_hit.cx, confirm_hit.cy, "trade.confirm")
        time.sleep(1.5)
        actions.append("confirm")
        snap = _refresh_snapshot(ctx)
    send_hit = snap.find("보내기", min_conf=0.55)
    if send_hit and snap.has_text("(6/6)"):
        _jitter_tap(ctx, send_hit.cx, send_hit.cy, "trade.send")
        time.sleep(2.0)
        actions.append("send")
        snap = _refresh_snapshot(ctx)
    confirm_hit = snap.find("확인", min_conf=0.55)
    if confirm_hit:
        _jitter_tap(ctx, confirm_hit.cx, confirm_hit.cy, "trade.confirm2")
        time.sleep(1.5)
        actions.append("confirm2")
    safe_close(ctx.driver, ctx.ocr, _refresh_snapshot(ctx),
               dry_run=ctx.settings.dry_run)
    return TaskResult(name="trade_collect", executed=bool(actions),
                       detail=f"actions={actions}")


def _fight_collect(ctx: TaskContext) -> TaskResult:
    main_btn = ctx.snapshot.find("전투", min_conf=0.7) if ctx.snapshot else None
    if main_btn is None or main_btn.cy < 1700:
        return TaskResult(name="fight_collect", executed=False, detail="전투 button not on main")
    _jitter_tap(ctx, main_btn.cx, main_btn.cy, "main.enter_fight")
    time.sleep(4.0)
    snap = _refresh_snapshot(ctx)
    actions: list[str] = []
    for word in ("수령", "수집", "노획", "Loot"):
        hit = snap.find(word, min_conf=0.55)
        if hit:
            _jitter_tap(ctx, hit.cx, hit.cy, f"fight.{word}")
            actions.append(word)
            time.sleep(2.0)
            snap = _refresh_snapshot(ctx)
    safe_close(ctx.driver, ctx.ocr, _refresh_snapshot(ctx),
               dry_run=ctx.settings.dry_run)
    return TaskResult(name="fight_collect", executed=bool(actions),
                       detail=f"actions={actions}")


_GOAL_NAV_BUTTONS = ((94, 2238, "target"), (296, 2238, "workshop"),
                      (788, 2238, "shield"), (985, 2238, "shop"))


def _detect_goal_alerts(ctx: TaskContext) -> list[tuple[int, int]]:
    snap = ctx.snapshot or _refresh_snapshot(ctx)
    badges = find_alert_badges(snap.png)
    coords: list[tuple[int, int]] = []
    for b in badges:
        if b.cy < 2050 and b.cx > 950 and b.cx < 1080:
            coords.append((b.cx - 30, b.cy + 30))
    return coords


def _claim_goals(ctx: TaskContext) -> TaskResult:
    _jitter_tap(ctx, 94, 2238, "nav.target")
    time.sleep(4.0)
    snap = _refresh_snapshot(ctx)
    if not (snap.has_text("진행도") or snap.has_text("열쇠")):
        return TaskResult(name="claim_goals", executed=False,
                          detail="not on goals screen")
    alert_targets = _detect_goal_alerts(ctx)
    if not alert_targets:
        _jitter_tap(ctx, 541, 2230, "goal.no_alerts_back")
        time.sleep(2.0)
        return TaskResult(name="claim_goals", executed=False,
                          detail="no alert badges (no rewards available)")
    total_claims = 0
    missions_processed = 0
    for badge_x, badge_y in alert_targets:
        _jitter_tap(ctx, badge_x, badge_y, f"goal.alert_{badge_x},{badge_y}")
        time.sleep(3.0)
        snap = _refresh_snapshot(ctx)
        if not snap.has_text("이전 수령"):
            _jitter_tap(ctx, 73, 2160, "goal.exit_no_prev")
            time.sleep(2.0)
            continue
        missions_processed += 1
        for _attempt in range(15):
            snap = _refresh_snapshot(ctx)
            prev = snap.find("이전 수령", min_conf=0.55)
            if prev is None:
                break
            _jitter_tap(ctx, prev.cx, prev.cy, "goal.claim_prev")
            time.sleep(1.5)
            snap = _refresh_snapshot(ctx)
            confirm = snap.find("확인", min_conf=0.55)
            if confirm:
                _jitter_tap(ctx, confirm.cx, confirm.cy, "goal.confirm")
                time.sleep(1.2)
                total_claims += 1
        _jitter_tap(ctx, 73, 2160, "goal.exit_done")
        time.sleep(2.5)
    _jitter_tap(ctx, 541, 2230, "goal.back_home")
    time.sleep(2.0)
    return TaskResult(name="claim_goals",
                      executed=total_claims > 0,
                      detail=f"alerts={len(alert_targets)} missions={missions_processed} claims={total_claims}")


def _watch_any_ad(ctx: TaskContext) -> TaskResult:
    if ctx.state.ad_claims_today >= 30:
        return TaskResult(name="watch_any_ad", executed=False,
                          detail="daily ad cap 30")
    snap = ctx.snapshot or _refresh_snapshot(ctx)
    watch_btn = None
    for h in snap.hits:
        if h.confidence < 0.55:
            continue
        if "광고 보기" in h.text or "Watch Ad" in h.text:
            if h.cy > 250 and h.cy < 1500:
                watch_btn = h
                break
    if watch_btn is None:
        return TaskResult(name="watch_any_ad", executed=False,
                          detail="no '광고 보기' button visible")
    _jitter_tap(ctx, watch_btn.cx, watch_btn.cy, "any_ad.watch")
    LOGGER.info("opportunistic ad watch starting (~90s)")
    ok, ad_detail = watch_ad_flow(ctx.driver, ctx.ocr, max_seconds=90,
                                   dry_run=ctx.settings.dry_run)
    if not ok:
        return TaskResult(name="watch_any_ad", executed=False, detail=f"ad: {ad_detail}")
    ctx.state.ad_claims_today += 1
    time.sleep(2.0)
    after = _refresh_snapshot(ctx)
    cancel = after.find("취소", min_conf=0.55)
    if cancel:
        _jitter_tap(ctx, cancel.cx, cancel.cy, "any_ad.cancel_repeat")
        time.sleep(1.5)
    return TaskResult(name="watch_any_ad", executed=True,
                      detail=f"ads_today={ctx.state.ad_claims_today}")


def _claim_afk_popup(ctx: TaskContext) -> TaskResult:
    snap = ctx.snapshot or _refresh_snapshot(ctx)
    has_offline = (snap.has_text("오프라인 수입") or snap.has_text("Offline")
                   or snap.has_text("AFK") or snap.has_text("부재중"))
    if not has_offline:
        return TaskResult(name="claim_afk_popup", executed=False, detail="no AFK dialog")
    if ctx.state.ad_claims_today < 30:
        x2_btn = None
        for h in snap.hits:
            if h.confidence < 0.55:
                continue
            if "광고 보기" in h.text or "x2" in h.text.lower() or "2배" in h.text:
                x2_btn = h
                break
        if x2_btn:
            _jitter_tap(ctx, x2_btn.cx, x2_btn.cy, "afk.claim_x2_ad")
            ok, _detail = watch_ad_flow(ctx.driver, ctx.ocr, max_seconds=90,
                                         dry_run=ctx.settings.dry_run)
            if ok:
                ctx.state.ad_claims_today += 1
                time.sleep(2.0)
                return TaskResult(name="claim_afk_popup", executed=True,
                                  detail=f"AFK x2 ad watched (ads={ctx.state.ad_claims_today})")
    free_btn = None
    for h in snap.hits:
        if h.confidence < 0.55:
            continue
        if any(w in h.text for w in ("수령", "Claim", "받기")):
            if h.cx > 0 and h.cy > 0:
                free_btn = h
                break
    if free_btn is None:
        return TaskResult(name="claim_afk_popup", executed=False, detail="no claim button")
    _jitter_tap(ctx, free_btn.cx, free_btn.cy, "afk.claim_free")
    time.sleep(2.0)
    return TaskResult(name="claim_afk_popup", executed=True, detail="AFK free claimed")


def _watch_ad_reward(ctx: TaskContext) -> TaskResult:
    if ctx.state.ad_claims_today >= 30:
        return TaskResult(name="watch_ad_reward", executed=False, detail="daily cap 30 reached")
    if not _tap_main_button(ctx, "ad_tv"):
        return TaskResult(name="watch_ad_reward", executed=False, detail="no ad_tv button")
    time.sleep(2.0)
    snap = _refresh_snapshot(ctx)
    if not _tap_text(ctx, snap, "광고 보기"):
        safe_close(ctx.driver, ctx.ocr, snap, dry_run=ctx.settings.dry_run)
        return TaskResult(name="watch_ad_reward", executed=False, detail="no Watch button visible")
    LOGGER.info("ad started, waiting up to 60s")
    deadline = time.monotonic() + 60.0
    while time.monotonic() < deadline:
        time.sleep(3.0)
        snap = _refresh_snapshot(ctx)
        if snap.has_any(("거래", "전투")) and not snap.has_text("광고 보기"):
            ctx.state.ad_claims_today += 1
            return TaskResult(name="watch_ad_reward", executed=True,
                              detail=f"ad_claims_today={ctx.state.ad_claims_today}")
    safe_close(ctx.driver, ctx.ocr, snap, dry_run=ctx.settings.dry_run)
    return TaskResult(name="watch_ad_reward", executed=False, detail="ad did not finish in 60s")


def default_tasks() -> list[Task]:
    dialog_gone = (Postcondition(kind="dialog_gone"),)
    return [
        Task(name="dismiss_blocking_dialog", priority=1,
             run=_dismiss_blocking_dialog, postconditions=dialog_gone,
             requires_main_screen=False),
        Task(name="watch_any_ad", priority=2,
             run=_watch_any_ad, cooldown_seconds=120.0,
             requires_main_screen=False),
        Task(name="claim_afk_popup", priority=5,
             run=_claim_afk_popup, cooldown_seconds=300.0,
             postconditions=dialog_gone, requires_main_screen=False),
        Task(name="claim_goals", priority=15,
             run=_claim_goals, cooldown_seconds=600.0,
             requires_main_screen=True),
        Task(name="trade_collect", priority=20,
             run=_trade_collect_and_send, cooldown_seconds=300.0,
             requires_main_screen=True),
        Task(name="fight_collect", priority=25,
             run=_fight_collect, cooldown_seconds=600.0,
             requires_main_screen=True),
        Task(name="spin_wheel", priority=30,
             run=_spin_wheel, cooldown_seconds=600.0,
             postconditions=(Postcondition(kind="text_disappeared", text="(3/3)"),),
             requires_main_screen=True),
    ]
