from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

from .vision import Ocr, grab_screenshot

if TYPE_CHECKING:
    from appium.webdriver.webdriver import WebDriver

LOGGER = logging.getLogger(__name__)


def dump_screen(
    driver: "WebDriver",
    ocr: Ocr | None,
    out_dir: Path,
    label: str,
) -> tuple[Path, Path | None]:
    out_dir.mkdir(parents=True, exist_ok=True)
    png = grab_screenshot(driver)
    png_path = out_dir / f"{label}.png"
    _ = png_path.write_bytes(png)
    LOGGER.info("dumped screenshot %s", png_path)
    if ocr is None:
        return png_path, None
    hits = ocr.read(png)
    yaml_path = out_dir / f"{label}.ocr.yaml"
    payload = {
        "screenshot": str(png_path.name),
        "screen_size": driver.get_window_size(),
        "ocr_hits": [
            {"text": h.text, "confidence": round(h.confidence, 3)} for h in hits
        ],
    }
    _ = yaml_path.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")
    LOGGER.info("dumped OCR %s", yaml_path)
    return png_path, yaml_path
