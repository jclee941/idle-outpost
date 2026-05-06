from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import httpx

from .auth import GameAuthSession
from .endpoints import PROD, ServiceEndpoints

LOGGER = logging.getLogger(__name__)


@dataclass
class ApiClient:
    session: GameAuthSession
    endpoints: ServiceEndpoints = PROD
    timeout: float = 30.0
    user_agent: str = "RockbiteIdleOutpost/2.1.1 (libgdx; Linux Android 16)"

    def _headers(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        headers: dict[str, str] = {
            "Authorization": f"Bearer {self.session.firebase.id_token}",
            "Content-Type": "application/json",
            "User-Agent": self.user_agent,
            "Accept": "application/json",
        }
        if extra:
            headers.update(extra)
        return headers

    def _client(self) -> httpx.Client:
        return httpx.Client(timeout=self.timeout, follow_redirects=False)

    def request(
        self,
        method: str,
        url: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        with self._client() as client:
            LOGGER.debug("%s %s", method, url)
            resp = client.request(
                method,
                url,
                headers=self._headers(extra_headers),
                json=json,
                params=params,
            )
            LOGGER.info("%s %s -> %d", method, url, resp.status_code)
            return resp

    def gameauth_login(self) -> dict[str, Any]:
        return self.request("POST", self.endpoints.gameauth.rstrip("/") + "/login").json()

    def gameauth_refresh(self) -> dict[str, Any]:
        return self.request("POST", self.endpoints.gameauth.rstrip("/") + "/refresh").json()

    def player_state(self) -> dict[str, Any]:
        return self.request("GET", self.endpoints.outpost.rstrip("/") + "/api/player/state").json()

    def claim_idle_rewards(self) -> dict[str, Any]:
        return self.request("POST", self.endpoints.outpost.rstrip("/") + "/api/idle/claim").json()

    def upgrade_station(self, station_id: str, levels: int = 1) -> dict[str, Any]:
        return self.request(
            "POST",
            self.endpoints.outpost.rstrip("/") + "/api/station/upgrade",
            json={"stationId": station_id, "levels": levels},
        ).json()

    def claim_daily_reward(self) -> dict[str, Any]:
        return self.request("POST", self.endpoints.outpost.rstrip("/") + "/api/daily/claim").json()

    def fetch_inbox(self) -> dict[str, Any]:
        return self.request("GET", self.endpoints.inbox).json()

    def realm_list(self) -> dict[str, Any]:
        return self.request("GET", self.endpoints.realm + "realms").json()

    def event_state(self) -> dict[str, Any]:
        return self.request("GET", self.endpoints.event + "events").json()
