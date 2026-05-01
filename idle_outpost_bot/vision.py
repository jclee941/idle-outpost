from __future__ import annotations

import base64
import io
import logging
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from appium.webdriver.webdriver import WebDriver

LOGGER = logging.getLogger(__name__)

_NUMBER_SUFFIX = {
    "K": 1_000,
    "M": 1_000_000,
    "B": 1_000_000_000,
    "T": 1_000_000_000_000,
}
_NUMBER_RE = re.compile(r"([0-9][0-9.,]*)\s*([KMBT]?)", re.IGNORECASE)

_ALERT_BADGE_RGB = (255, 82, 47)
_ALERT_TOLERANCE = 40
_ALERT_MIN_PIXELS = 700
_ALERT_MAX_PIXELS = 2000
_ALERT_MIN_SIZE = 25
_ALERT_MAX_SIZE = 60


@dataclass(frozen=True)
class Region:
    x: int
    y: int
    w: int
    h: int


@dataclass(frozen=True)
class AlertBadge:
    cx: int
    cy: int
    w: int
    h: int
    pixel_count: int


@dataclass(frozen=True)
class OcrHit:
    text: str
    confidence: float
    x1: int = 0
    y1: int = 0
    x2: int = 0
    y2: int = 0

    @property
    def cx(self) -> int:
        return (self.x1 + self.x2) // 2

    @property
    def cy(self) -> int:
        return (self.y1 + self.y2) // 2

    @property
    def w(self) -> int:
        return self.x2 - self.x1

    @property
    def h(self) -> int:
        return self.y2 - self.y1


class Ocr:
    def __init__(self, lang: str = "korean") -> None:
        self._lang = lang
        self._engine: Any | None = None

    def _ensure_engine(self) -> Any:
        if self._engine is None:
            from paddleocr import PaddleOCR

            self._engine = PaddleOCR(
                lang=self._lang,
                enable_mkldnn=False,
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
                text_detection_model_name="PP-OCRv5_mobile_det",
                text_recognition_model_name="korean_PP-OCRv5_mobile_rec",
            )
        return self._engine

    def read(self, png_bytes: bytes, region: Region | None = None) -> list[OcrHit]:
        from PIL import Image
        import numpy as np

        image = Image.open(io.BytesIO(png_bytes)).convert("RGB")
        if region is not None:
            image = image.crop((region.x, region.y, region.x + region.w, region.y + region.h))
        arr = np.asarray(image)
        engine = self._ensure_engine()
        raw_result = engine.predict(arr)
        hits: list[OcrHit] = []
        offset_x = region.x if region is not None else 0
        offset_y = region.y if region is not None else 0
        for page in raw_result or []:
            res = page if isinstance(page, dict) else getattr(page, "res", None) or page
            if isinstance(res, dict):
                texts = res.get("rec_texts", [])
                scores = res.get("rec_scores", [])
                boxes = res.get("rec_boxes", [])
            else:
                texts = getattr(res, "rec_texts", [])
                scores = getattr(res, "rec_scores", [])
                boxes = getattr(res, "rec_boxes", [])
            box_list = list(boxes) if boxes is not None else []
            for idx, (text, score) in enumerate(zip(texts, scores)):
                x1 = y1 = x2 = y2 = 0
                if idx < len(box_list):
                    raw = box_list[idx]
                    if hasattr(raw, "tolist"):
                        raw = raw.tolist()
                    if len(raw) >= 4:
                        x1, y1, x2, y2 = (int(raw[0]) + offset_x, int(raw[1]) + offset_y,
                                          int(raw[2]) + offset_x, int(raw[3]) + offset_y)
                hits.append(OcrHit(text=str(text), confidence=float(score),
                                   x1=x1, y1=y1, x2=x2, y2=y2))
        return hits


def grab_screenshot(driver: "WebDriver") -> bytes:
    raw = driver.get_screenshot_as_base64()
    return base64.b64decode(raw)


def parse_stylized_number(text: str) -> int | None:
    match = _NUMBER_RE.search(text.replace(" ", ""))
    if match is None:
        return None
    digits = match.group(1).replace(",", "")
    suffix = match.group(2).upper()
    try:
        value = float(digits)
    except ValueError:
        return None
    multiplier = _NUMBER_SUFFIX.get(suffix, 1)
    return int(value * multiplier)


def find_text(hits: list[OcrHit], needle: str, min_confidence: float = 0.6) -> OcrHit | None:
    needle_lower = needle.lower()
    for hit in hits:
        if hit.confidence < min_confidence:
            continue
        if needle_lower in hit.text.lower():
            return hit
    return None


def find_alert_badges(png_bytes: bytes, region: Region | None = None) -> list[AlertBadge]:
    import io
    from PIL import Image
    import numpy as np
    from scipy import ndimage

    image = Image.open(io.BytesIO(png_bytes)).convert("RGB")
    if region is not None:
        image = image.crop((region.x, region.y, region.x + region.w, region.y + region.h))
    arr = np.asarray(image)
    target = np.array(_ALERT_BADGE_RGB)
    diff = np.abs(arr.astype(int) - target).sum(axis=2)
    mask = (diff < _ALERT_TOLERANCE * 3).astype(np.uint8)
    labeled, num = ndimage.label(mask)
    badges: list[AlertBadge] = []
    offset_x = region.x if region is not None else 0
    offset_y = region.y if region is not None else 0
    for i in range(1, num + 1):
        ys, xs = np.where(labeled == i)
        size = len(xs)
        if size < _ALERT_MIN_PIXELS or size > _ALERT_MAX_PIXELS:
            continue
        bw = int(xs.max() - xs.min() + 1)
        bh = int(ys.max() - ys.min() + 1)
        if not (_ALERT_MIN_SIZE < bw < _ALERT_MAX_SIZE and _ALERT_MIN_SIZE < bh < _ALERT_MAX_SIZE):
            continue
        aspect = bw / max(bh, 1)
        if not (0.6 < aspect < 1.6):
            continue
        cx = int(xs.mean()) + offset_x
        cy = int(ys.mean()) + offset_y
        badges.append(AlertBadge(cx=cx, cy=cy, w=bw, h=bh, pixel_count=size))
    badges.sort(key=lambda b: (b.cy, b.cx))
    return badges
