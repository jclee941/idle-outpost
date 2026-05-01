from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    appium_url: str
    device_name: str
    package_name: str
    activity_name: str
    state_path: Path
    screenshot_dir: Path
    config_path: Path
    loop_interval_seconds: float
    dry_run: bool
    ocr_lang: str

    @classmethod
    def from_env(cls) -> "Settings":
        state_dir = Path(
            os.getenv(
                "IDLE_OUTPOST_BOT_STATE_DIR",
                str(Path.home() / ".local" / "share" / "idle-outpost-bot"),
            )
        )
        config_path = Path(
            os.getenv(
                "IDLE_OUTPOST_BOT_CONFIG",
                str(Path(__file__).resolve().parent / "config" / "screens.yaml"),
            )
        )
        return cls(
            appium_url=os.getenv("APPIUM_SERVER_URL", "http://192.168.50.220:4723"),
            device_name=os.getenv("ANDROID_DEVICE_NAME", "emulator-5554"),
            package_name=os.getenv("IDLE_OUTPOST_PACKAGE", ""),
            activity_name=os.getenv("IDLE_OUTPOST_ACTIVITY", ""),
            state_path=state_dir / "state.json",
            screenshot_dir=state_dir / "screenshots",
            config_path=config_path,
            loop_interval_seconds=float(os.getenv("IDLE_OUTPOST_LOOP_INTERVAL", "30")),
            dry_run=os.getenv("IDLE_OUTPOST_DRY_RUN", "0").lower() in ("1", "true", "yes"),
            ocr_lang=os.getenv("IDLE_OUTPOST_OCR_LANG", "korean"),
        )
