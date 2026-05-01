from __future__ import annotations

import logging
import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup, Tag

LOGGER = logging.getLogger(__name__)
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
)
TIMEOUT_SECONDS = 10.0
SOURCE_URLS = [
    "https://levelgeeks.org/idle-outpost-codes/",
    "https://levelgeeks.net/idle-outpost-codes/",
]
CODE_PATTERN = re.compile(r"\b[A-Z0-9]{4,}\b")


@dataclass(slots=True)
class Code:
    code_text: str
    source_url: str
    scraped_at: datetime


@dataclass(slots=True)
class ScrapeResult:
    codes: list[Code]
    attempted_sources: int
    successful_sources: int


def scrape_codes() -> list[Code]:
    return scrape_codes_with_metadata().codes


def scrape_codes_with_metadata() -> ScrapeResult:
    found_codes: dict[str, Code] = {}
    attempted_sources = len(SOURCE_URLS)
    successful_sources = 0

    for source_url in SOURCE_URLS:
        source_codes, fetched = scrape_source(source_url)
        if fetched:
            successful_sources += 1
        for code in source_codes:
            _ = found_codes.setdefault(code.code_text, code)

    return ScrapeResult(
        codes=sorted(found_codes.values(), key=lambda item: item.code_text),
        attempted_sources=attempted_sources,
        successful_sources=successful_sources,
    )


def scrape_source(source_url: str) -> tuple[list[Code], bool]:
    headers = {"User-Agent": USER_AGENT}

    try:
        with httpx.Client(
            timeout=TIMEOUT_SECONDS, headers=headers, follow_redirects=True
        ) as client:
            response = client.get(source_url)
            _ = response.raise_for_status()
    except httpx.HTTPError as exc:
        LOGGER.warning("failed to fetch %s: %s", source_url, exc)
        return [], False

    return _parse_codes(response.text, source_url), True


def _parse_codes(html: str, source_url: str) -> list[Code]:
    soup = BeautifulSoup(html, "html.parser")
    active_section = _find_active_section(soup)
    if active_section is None:
        LOGGER.warning("active section not found for %s", source_url)
        return []

    scraped_at = datetime.now(timezone.utc)
    seen: set[str] = set()
    codes: list[Code] = []

    for candidate in _iter_code_candidates(active_section):
        code_text = candidate.strip().upper()
        if not CODE_PATTERN.fullmatch(code_text):
            continue
        if code_text in seen:
            continue
        seen.add(code_text)
        codes.append(Code(code_text=code_text, source_url=source_url, scraped_at=scraped_at))

    if not codes:
        LOGGER.warning("no active codes parsed from %s", source_url)

    return codes


def _find_active_section(soup: BeautifulSoup) -> Tag | None:
    active_heading: Tag | None = None
    expired_heading: Tag | None = None

    for heading in soup.find_all(re.compile(r"^h[1-6]$")):
        text = heading.get_text(" ", strip=True).lower()
        if active_heading is None and "active idle outpost codes" in text:
            active_heading = heading
        elif active_heading is None and text.startswith("active") and "code" in text:
            active_heading = heading

        if expired_heading is None and text.startswith("expired"):
            expired_heading = heading

    if active_heading is None:
        return None

    collected: list[str] = []
    for sibling in active_heading.next_siblings:
        if isinstance(sibling, Tag):
            if sibling is expired_heading:
                break
            if sibling.name and re.fullmatch(r"h[1-6]", sibling.name):
                break
            collected.append(str(sibling))

    if not collected:
        return None

    return BeautifulSoup("".join(collected), "html.parser")


def _iter_code_candidates(active_section: Tag) -> Iterable[str]:
    for element in active_section.find_all(["b", "strong", "code"]):
        text = element.get_text(" ", strip=True)
        for match in CODE_PATTERN.findall(text):
            yield match


def source_name(source_url: str) -> str:
    return urlparse(source_url).netloc
