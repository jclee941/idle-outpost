from __future__ import annotations

import os

from dataclasses import dataclass


def _get_firebase_api_key() -> str:
    raw = os.getenv("IDLE_OUTPOST_FIREBASE_API_KEY", "").strip()
    if not raw:
        raise RuntimeError(
            "IDLE_OUTPOST_FIREBASE_API_KEY is not set. "
            "Add it to your .env file (was AIzaSy...)."
        )
    return raw


def _get_firebase_app_id() -> str:
    raw = os.getenv("IDLE_OUTPOST_FIREBASE_APP_ID", "").strip()
    if not raw:
        raise RuntimeError(
            "IDLE_OUTPOST_FIREBASE_APP_ID is not set. "
            "Add it to your .env file (was 1:531453127205:android:...)."
        )
    return raw


def _get_firebase_project_number() -> str:
    raw = os.getenv("IDLE_OUTPOST_FIREBASE_PROJECT_NUMBER", "").strip()
    if not raw:
        raise RuntimeError(
            "IDLE_OUTPOST_FIREBASE_PROJECT_NUMBER is not set. "
            "Add it to your .env file (was 531453127205)."
        )
    return raw


def _get_firebase_project_id() -> str:
    raw = os.getenv("IDLE_OUTPOST_FIREBASE_PROJECT_ID", "").strip()
    if not raw:
        raise RuntimeError(
            "IDLE_OUTPOST_FIREBASE_PROJECT_ID is not set. "
            "Add it to your .env file (was idle-outpost-b1619)."
        )
    return raw


@dataclass(frozen=True)
class FirebaseConfig:
    api_key: str
    app_id: str
    project_number: str
    project_id: str
    storage_bucket: str = ""

    @property
    def identity_toolkit_url(self) -> str:
        return f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={self.api_key}"

    @property
    def secure_token_url(self) -> str:
        return f"https://securetoken.googleapis.com/v1/token?key={self.api_key}"

    @property
    def signin_anon_url(self) -> str:
        return f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.api_key}"

    @property
    def signin_idp_url(self) -> str:
        return f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key={self.api_key}"


CONFIG = FirebaseConfig(
    api_key=_get_firebase_api_key(),
    app_id=_get_firebase_app_id(),
    project_number=_get_firebase_project_number(),
    project_id=_get_firebase_project_id(),
)
