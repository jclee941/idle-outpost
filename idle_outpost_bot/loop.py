from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from .config_loader import BotConfig
from .notify import notify_event
from .safety import (
    capture,
    detect_mode,
    handle_danger_dialog,
    handle_external_overlay,
    safe_close,
    verify,
)
from .settings import Settings
from .state import BotState, now_utc_iso, reset_daily_counters_if_needed, save_state
from .tasks import Task, TaskContext, default_tasks
from .vision import Ocr

if TYPE_CHECKING:
    from appium.webdriver.webdriver import WebDriver

LOGGER = logging.getLogger(__name__)


def _select_task(
    tasks: list[Task],
    last_run: dict[str, float],
    skip_in_iter: set[str],
    mode: str,
    now: float,
) -> Task | None:
    for task in sorted(tasks, key=lambda t: t.priority):
        if task.name in skip_in_iter:
            continue
        prev = last_run.get(task.name, 0.0)
        if task.cooldown_seconds and (now - prev) < task.cooldown_seconds:
            continue
        if task.requires_main_screen and mode != "main":
            continue
        return task
    return None


def _execute_task(ctx: TaskContext, task: Task) -> tuple[bool, bool, str, str]:
    before = ctx.snapshot or capture(ctx.driver, ctx.ocr)
    ctx.snapshot = before
    LOGGER.info("running task %s (priority=%d)", task.name, task.priority)
    try:
        result = task.run(ctx)
    except Exception as exc:
        LOGGER.exception("task %s raised", task.name)
        ctx.state.last_error = f"{task.name}: {exc.__class__.__name__}: {exc}"
        return False, False, "", str(exc)

    if not result.executed:
        return False, False, result.detail, "not executed"

    time.sleep(1.5)
    after = capture(ctx.driver, ctx.ocr)
    ctx.snapshot = after

    if not task.postconditions:
        return True, False, result.detail, "MISSING postcondition (treat as unverified)"

    ok, reason = verify(list(task.postconditions), before, after)
    return True, ok, result.detail, reason


def run_once(
    driver: "WebDriver",
    settings: Settings,
    config: BotConfig,
    ocr: Ocr,
    state: BotState,
) -> list[str]:
    reset_daily_counters_if_needed(state)
    ctx = TaskContext(driver=driver, ocr=ocr, config=config, state=state, settings=settings)
    actions: list[str] = []

    snap = capture(driver, ocr)
    ctx.snapshot = snap

    if handle_external_overlay(driver, ocr, snap, dry_run=settings.dry_run):
        actions.append("recovered: external overlay")
        ctx.snapshot = capture(driver, ocr)
    elif handle_danger_dialog(driver, ocr, snap, dry_run=settings.dry_run):
        actions.append("dismissed: danger dialog")
        ctx.snapshot = capture(driver, ocr)

    snap = ctx.snapshot
    mode = detect_mode(driver, snap)
    LOGGER.info("mode=%s, hits=%d", mode, len(snap.hits))

    last_run: dict[str, float] = {}
    skip_in_iter: set[str] = set()
    tasks = default_tasks()
    iterations = 0
    max_iter = len(tasks)
    while iterations < max_iter:
        iterations += 1
        if iterations > 1:
            ctx.snapshot = capture(driver, ocr)
            mode = detect_mode(driver, ctx.snapshot)
            if handle_external_overlay(driver, ocr, ctx.snapshot, dry_run=settings.dry_run):
                actions.append(f"iter{iterations}: ext overlay recovered")
                continue
            if handle_danger_dialog(driver, ocr, ctx.snapshot, dry_run=settings.dry_run):
                actions.append(f"iter{iterations}: danger dismissed")
                continue
        task = _select_task(tasks, last_run, skip_in_iter, mode, time.monotonic())
        if task is None:
            LOGGER.info("no eligible task at iter=%d (mode=%s)", iterations, mode)
            break
        executed, verified, detail, reason = _execute_task(ctx, task)
        skip_in_iter.add(task.name)
        if executed:
            last_run[task.name] = time.monotonic()
            state.task_runs[task.name] = state.task_runs.get(task.name, 0) + 1
        actions.append(f"{task.name}: exec={executed} verify={verified} ({detail} | {reason})")
        if executed and detect_mode(driver, ctx.snapshot or capture(driver, ocr)) == "dialog":
            safe_close(driver, ocr, ctx.snapshot, dry_run=settings.dry_run)

    state.iterations += 1
    state.last_iteration_at = now_utc_iso()
    save_state(settings.state_path, state)
    return actions


def run_loop(
    driver: "WebDriver",
    settings: Settings,
    config: BotConfig,
    ocr: Ocr,
    state: BotState,
) -> None:
    notify_event("Idle Outpost bot started", [f"device={settings.device_name}"])
    try:
        while True:
            actions = run_once(driver, settings, config, ocr, state)
            if actions:
                LOGGER.info("iteration #%d: %s", state.iterations, "; ".join(actions))
            else:
                LOGGER.debug("iteration #%d idle", state.iterations)
            time.sleep(settings.loop_interval_seconds)
    except KeyboardInterrupt:
        notify_event("Idle Outpost bot stopped", [f"iterations={state.iterations}"])
