from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from .vision import Region


@dataclass(frozen=True)
class ButtonConfig:
    name: str
    x: int
    y: int


@dataclass(frozen=True)
class ScreenConfig:
    name: str
    detect_text: str
    detect_region: Region | None
    buttons: dict[str, ButtonConfig]
    regions: dict[str, Region]


@dataclass(frozen=True)
class BotConfig:
    screens: dict[str, ScreenConfig]


def _load_region(raw: object) -> Region | None:
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise ValueError(f"region must be mapping, got {type(raw).__name__}")
    return Region(
        x=int(raw["x"]),
        y=int(raw["y"]),
        w=int(raw["w"]),
        h=int(raw["h"]),
    )


def load_config(path: Path) -> BotConfig:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"config root must be mapping in {path}")
    screens_raw = raw.get("screens", {})
    if not isinstance(screens_raw, dict):
        raise ValueError("config.screens must be mapping")
    screens: dict[str, ScreenConfig] = {}
    for name, screen_raw in screens_raw.items():
        if not isinstance(screen_raw, dict):
            continue
        buttons_raw = screen_raw.get("buttons", {}) or {}
        regions_raw = screen_raw.get("regions", {}) or {}
        buttons = {
            btn_name: ButtonConfig(name=btn_name, x=int(btn["x"]), y=int(btn["y"]))
            for btn_name, btn in buttons_raw.items()
            if isinstance(btn, dict)
        }
        regions = {
            r_name: r
            for r_name, raw_region in regions_raw.items()
            if (r := _load_region(raw_region)) is not None
        }
        screens[name] = ScreenConfig(
            name=name,
            detect_text=str(screen_raw.get("detect_text", "")),
            detect_region=_load_region(screen_raw.get("detect_region")),
            buttons=buttons,
            regions=regions,
        )
    return BotConfig(screens=screens)
