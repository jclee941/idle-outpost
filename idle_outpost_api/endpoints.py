from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ServiceEndpoints:
    activity: str = "https://activity.svc.rockbitegames.com"
    analytics: str = "https://analytics.svc.rockbitegames.com/api/external"
    arena: str = "https://arena-service.svc.rockbitegames.com/api/external/"
    auth: str = "https://auth.svc.rockbitegames.com/api/"
    auth_login: str = "https://auth.svc.rockbitegames.com/api/auth/login"
    auth_login_realm_template: str = "https://auth.svc.rockbitegames.com/api/auth/login/realms/"
    chat_rest: str = "https://chat.svc.rockbitegames.com"
    chat_ws: str = "wss://chatws.svc.rockbitegames.com"
    event: str = "https://event-service.svc.rockbitegames.com/api/"
    gameauth_health: str = "https://gameauth.svc.rockbitegames.com/api/health/liveness"
    guild: str = "https://guild-service.svc.rockbitegames.com/api"
    hashresources: str = "https://gr.svc.rockbitegames.com/api/hashresources/"
    inbox: str = "https://inbox.svc.rockbitegames.com/api/inbox/"
    notification: str = "https://notification-service.svc.rockbitegames.com/api/client"
    outpost: str = "https://outpost.svc.rockbitegames.com"
    rc: str = "https://rc.svc.rockbitegames.com/api/"
    rc_remote_configs: str = "https://rc.svc.rockbitegames.com/api/remote-configs"
    rc_account_template: str = "https://rc.svc.rockbitegames.com/api/remote-configs/game-accounts/"
    realm: str = "https://realm-service.svc.rockbitegames.com/api/pub/"
    scheduler: str = "https://scheduler-service.svc.rockbitegames.com/api/"
    translation: str = "https://translation-service.svc.rockbitegames.com/api/"
    ud: str = "https://ud.svc.rockbitegames.com/api/"
    ud_save: str = "https://ud.svc.rockbitegames.com/api/userdata/save"

    GAME_AUTH_APPLICATION: str = "clxylhegq000gg0zzl9tajk06"
    APP_CHECK_ENABLED_KEY: str = "c3po"
    APP_CHECK_DISABLED_VALUE: int = 41


@dataclass(frozen=True)
class StagingEndpoints:
    activity: str = "https://activity-dev.svc.rockbitegames.com"
    arena: str = "https://arena-service-dev.svc.rockbitegames.com/api/external/"
    auth: str = "https://auth-dev.svc.rockbitegames.com/api/"
    chat: str = "https://chat-dev.svc.rockbitegames.com"
    event: str = "https://event-service-dev.svc.rockbitegames.com/api/"
    gameauth: str = "https://gameauth-dev.svc.rockbitegames.com/api/gameauth/"
    guild: str = "https://guild-service-dev.svc.rockbitegames.com/api"
    inbox: str = "https://inbox-dev.svc.rockbitegames.com/api/inbox/"
    notification: str = "https://notification-service-dev.svc.rockbitegames.com/api/client"
    outpost: str = "https://outpost-staging.svc.rockbitegames.com"
    rc: str = "https://rc-dev.svc.rockbitegames.com/api/"
    realm: str = "https://realm-service-dev.svc.rockbitegames.com/api/pub/"
    scheduler: str = "https://scheduler-service-dev.svc.rockbitegames.com/api/"
    translation: str = "https://translation-service-dev.svc.rockbitegames.com/api/"
    ud: str = "https://ud-dev.svc.rockbitegames.com/api/"


PROD = ServiceEndpoints()
STAGING = StagingEndpoints()
