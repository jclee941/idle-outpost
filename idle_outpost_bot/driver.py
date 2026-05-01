from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Iterator

from .settings import Settings

if TYPE_CHECKING:
    from appium.webdriver.webdriver import WebDriver

LOGGER = logging.getLogger(__name__)


def _build_capabilities(settings: Settings) -> dict[str, Any]:
    caps: dict[str, Any] = {
        "platformName": "Android",
        "appium:automationName": "UiAutomator2",
        "appium:deviceName": settings.device_name,
        "appium:noReset": True,
        "appium:newCommandTimeout": 600,
        "appium:autoGrantPermissions": True,
        "appium:disableWindowAnimation": True,
    }
    if settings.package_name:
        caps["appium:appPackage"] = settings.package_name
    if settings.activity_name:
        caps["appium:appActivity"] = settings.activity_name
    return caps


def create_driver(settings: Settings) -> "WebDriver":
    from appium import webdriver
    from appium.options.android import UiAutomator2Options

    options = UiAutomator2Options().load_capabilities(_build_capabilities(settings))
    LOGGER.info("connecting to Appium at %s", settings.appium_url)
    driver = webdriver.Remote(settings.appium_url, options=options)
    return driver


@contextmanager
def session(settings: Settings) -> Iterator["WebDriver"]:
    driver = create_driver(settings)
    try:
        yield driver
    finally:
        try:
            driver.quit()
        except Exception:  # noqa: BLE001
            LOGGER.warning("driver.quit() raised", exc_info=True)
