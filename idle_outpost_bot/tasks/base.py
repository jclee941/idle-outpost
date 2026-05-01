from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Protocol

from ..config_loader import BotConfig
from ..safety import Postcondition, Snapshot
from ..settings import Settings
from ..state import BotState
from ..vision import Ocr

if TYPE_CHECKING:
    from appium.webdriver.webdriver import WebDriver


@dataclass
class TaskContext:
    driver: "WebDriver"
    ocr: Ocr
    config: BotConfig
    state: BotState
    settings: Settings
    snapshot: Snapshot | None = None


@dataclass(frozen=True)
class TaskResult:
    name: str
    executed: bool
    detail: str = ""
    verified: bool = False
    verify_reason: str = ""


class TaskFn(Protocol):
    def __call__(self, ctx: TaskContext) -> TaskResult: ...


@dataclass(frozen=True)
class Task:
    name: str
    priority: int
    run: Callable[[TaskContext], TaskResult]
    cooldown_seconds: float = 0.0
    postconditions: tuple[Postcondition, ...] = field(default_factory=tuple)
    requires_main_screen: bool = False
