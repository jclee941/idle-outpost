from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FirebaseConfig:
    api_key: str = "AIzaSyAJu7iTPgyajiKdbGfu-YBifs5hFsFZpfs"
    app_id: str = "1:531453127205:android:610679a002aa521d72edcc"
    project_number: str = "531453127205"
    project_id: str = "idle-outpost-b1619"
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


CONFIG = FirebaseConfig()
