from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx

from auth import STORE_API_BASE, TIMEOUT_SECONDS, auth_headers, get_user_ids, login
from scraper import Code

LOGGER = logging.getLogger(__name__)
ALLOWED_REDEEM_HOSTS = {"store.xsolla.com"}


@dataclass(slots=True)
class RedeemAttempt:
    code_text: str
    redeemed: bool
    message: str


def attempt_redeem(code: Code) -> RedeemAttempt:
    """Try to redeem a promo code for all configured user accounts."""
    user_ids = get_user_ids()
    if not user_ids:
        message = "auto-redeem skipped: no USER_IDS configured"
        LOGGER.info("%s for %s", message, code.code_text)
        return RedeemAttempt(code_text=code.code_text, redeemed=False, message=message)

    all_attempts: list[str] = []

    for user_id in user_ids:
        label = user_id[:8]
        try:
            with httpx.Client(timeout=TIMEOUT_SECONDS) as client:
                token = login(client, user_id)
                result = _redeem_for_user(client, token, code.code_text, label)
                all_attempts.append(result.message)
                if result.redeemed:
                    return RedeemAttempt(
                        code_text=code.code_text,
                        redeemed=True,
                        message=result.message,
                    )
        except httpx.HTTPError as exc:
            msg = f"[{label}] login failed: {exc.__class__.__name__}"
            LOGGER.warning("%s for %s", msg, code.code_text)
            all_attempts.append(msg)

    message = " ; ".join(all_attempts) if all_attempts else "no user IDs configured"
    return RedeemAttempt(code_text=code.code_text, redeemed=False, message=message)


@dataclass(slots=True)
class _UserRedeemResult:
    redeemed: bool
    message: str


def _redeem_for_user(
    client: httpx.Client,
    token: str,
    code_text: str,
    label: str,
) -> _UserRedeemResult:
    """Attempt redemption for a single authenticated user."""
    headers = auth_headers(token)
    attempts: list[str] = []

    # 1. Try promocode/redeem (primary — requires cart ID)
    cart_id = _get_cart_id(client, headers)
    if cart_id:
        promo_result = _try_promocode(client, headers, code_text, cart_id, label)
        attempts.append(promo_result.message)
        if promo_result.redeemed:
            return promo_result

    # 2. Fallback: coupon/redeem
    coupon_result = _try_coupon(client, headers, code_text, label)
    attempts.append(coupon_result.message)
    if coupon_result.redeemed:
        return coupon_result

    return _UserRedeemResult(
        redeemed=False,
        message=" ; ".join(attempts),
    )


def _get_cart_id(client: httpx.Client, headers: dict[str, str]) -> str:
    """Fetch the current cart ID for authenticated user."""
    url = f"{STORE_API_BASE}/cart"
    try:
        resp = client.get(url, headers=headers)
        resp.raise_for_status()
        cart_id = resp.json().get("cart_id", "")
        LOGGER.debug("cart_id: %s", cart_id)
        return str(cart_id)
    except httpx.HTTPError as exc:
        LOGGER.warning("cart fetch failed: %s", exc.__class__.__name__)
        return ""


def _try_promocode(
    client: httpx.Client,
    headers: dict[str, str],
    code_text: str,
    cart_id: str,
    label: str,
) -> _UserRedeemResult:
    """POST promocode/redeem with cart (primary endpoint)."""
    url = f"{STORE_API_BASE}/promocode/redeem"
    if not _is_allowed_url(url):
        return _UserRedeemResult(False, f"[{label}] promocode: blocked URL")

    payload = {"coupon_code": code_text, "cart": {"id": cart_id}}
    return _post_redeem(client, headers, url, payload, f"[{label}] promocode")


def _try_coupon(
    client: httpx.Client,
    headers: dict[str, str],
    code_text: str,
    label: str,
) -> _UserRedeemResult:
    """POST coupon/redeem (fallback endpoint)."""
    url = f"{STORE_API_BASE}/coupon/redeem"
    if not _is_allowed_url(url):
        return _UserRedeemResult(False, f"[{label}] coupon: blocked URL")

    payload = {"coupon_code": code_text}
    return _post_redeem(client, headers, url, payload, f"[{label}] coupon")


def _post_redeem(
    client: httpx.Client,
    headers: dict[str, str],
    url: str,
    payload: dict[str, object],
    context: str,
) -> _UserRedeemResult:
    """Send a POST redeem request and evaluate the response."""
    try:
        resp = client.post(url, json=payload, headers=headers)
    except httpx.HTTPError as exc:
        msg = f"{context}: request error ({exc.__class__.__name__})"
        LOGGER.warning(msg)
        return _UserRedeemResult(False, msg)

    body_preview = _compact_text(resp.text)
    msg = f"{context}: HTTP {resp.status_code} {body_preview}"

    if resp.is_success:
        try:
            body_json: object = resp.json()
        except json.JSONDecodeError:
            body_json = None

        if _looks_like_success(body_json, body_preview):
            LOGGER.info("redeem success via %s", context)
            return _UserRedeemResult(True, msg)

    LOGGER.debug(msg)
    return _UserRedeemResult(False, msg)


def _looks_like_success(response_json: object, body_preview: str) -> bool:
    if isinstance(response_json, dict):
        success = response_json.get("success")
        redeemed = response_json.get("redeemed")
        status = response_json.get("status")
        coupon = response_json.get("coupon")

        if success is True or redeemed is True:
            return True
        if isinstance(status, str) and status.lower() in {
            "success",
            "completed",
            "applied",
            "redeemed",
        }:
            return True
        if isinstance(coupon, dict):
            coupon_redeemed = coupon.get("redeemed")
            coupon_status = coupon.get("status")
            if coupon_redeemed is True:
                return True
            if isinstance(coupon_status, str) and coupon_status.lower() in {
                "success",
                "completed",
                "applied",
                "redeemed",
            }:
                return True

    lowered = body_preview.lower()
    failure_markers = ["invalid", "failed", "error", "denied"]
    if any(m in lowered for m in failure_markers):
        return False
    success_markers = ["success", "redeemed", "applied", "completed"]
    return any(m in lowered for m in success_markers)


def _is_allowed_url(url: str) -> bool:
    return urlparse(url).netloc in ALLOWED_REDEEM_HOSTS


def _compact_text(value: str, limit: int = 160) -> str:
    cleaned = re.sub(r"\s+", " ", value).strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 3] + "..."
