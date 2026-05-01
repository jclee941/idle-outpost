# Idle Outpost (com.rockbite.zombieoutpost) API Research

**Game Version**: Unknown (jadx decompiled source at `/tmp/io_apk_pull/jadx_out/sources`)
**Research Date**: 2026-04-27
**Source Files**: `/tmp/io_apk_pull/jadx_out/sources/com/rockbite/`

---

## Section 1: Backend API Endpoints

### A. `*.svc.rockbitegames.com` Endpoints

| URL | Service | Auth Required | App Check | Bot Callable |
|------|---------|---------------|-----------|-------------|
| `https://gameauth.svc.rockbitegames.com/api/health/liveness` | Health Check | ❌ NONE | ❌ None | ✅ **YES** |
| `https://gameauth.svc.rockbitegames.com/api/gameauth/` | Game Auth | ✅ Bearer Token | ✅ Yes | ❌ No |
| `https://rc.svc.rockbitegames.com/api/` | Remote Config | ✅ Bearer Token | ✅ Yes | ❌ No |
| `https://gr.svc.rockbitegames.com/api/hashresources/` | Hash Resources | ✅ Bearer Token | ✅ Yes | ❌ No |
| `https://inbox.svc.rockbitegames.com/api/inbox/` | Inbox Service | ✅ Bearer Token | ✅ Yes | ❌ No |
| `https://event-service.svc.rockbitegames.com/api/` | Event Service | ✅ Bearer Token | ✅ Yes | ❌ No |
| `https://ud.svc.rockbitegames.com/api/` | User Data | ✅ Bearer Token | ✅ Yes | ❌ No |
| `https://scheduler-service.svc.rockbitegames.com/api/` | Scheduler | ✅ Bearer Token | ✅ Yes | ❌ No |
| `https://chat.svc.rockbitegames.com` | Chat REST | ✅ Bearer Token | ✅ Yes | ❌ No |
| `https://chatws.svc.rockbitegames.com` | Chat WebSocket | ✅ Bearer Token | ✅ Yes | ❌ No |
| `https://realm-service.svc.rockbitegames.com/api/pub/` | Realm | ✅ Bearer Token | ✅ Yes | ❌ No |
| `https://notification-service.svc.rockbitegames.com/api/client` | Notifications | ✅ Bearer Token | ✅ Yes | ❌ No |
| `https://activity.svc.rockbitegames.com` | Activity | ✅ Bearer Token | ✅ Yes | ❌ No |
| `https://arena-service.svc.rockbitegames.com/api/external/` | Arena | ✅ Bearer Token | ✅ Yes | ❌ No |
| `https://guild-service.svc.rockbitegames.com/api` | Guild | ✅ Bearer Token | ✅ Yes | ❌ No |
| `https://outpost.svc.rockbitegames.com` | Backend Base | ✅ Bearer Token | ✅ Yes | ❌ No |
| `https://analytics.svc.rockbitegames.com/api/external` | Analytics | ✅ Bearer Token | ✅ Yes | ❌ No |
| `https://analytics-ru.svc.rockbitegames.com/api/external` | Analytics (RU proxy) | ✅ Bearer Token | ✅ Yes | ❌ No |

### B. Auth Header Construction (from `GameAuth.java`, `NewGameAuth.java`)

```java
// Authorization header
"authorization", "Bearer " + accessToken

// Required headers
"game-auth-userid", userId
"game-auth-sessionid", sessionId
"game-auth-application", "clxylhegq000gg0zzl9tajk06"
"country-code", geoCode
"platform", platformName
"x-log-id", ...
"x-firebase-appcheck", appCheckToken  // if App Check enabled
```

### C. App Check Bypass (from `AppCheckImpl.java`)

```java
public void getAppCheckToken(AppCheckTokenListener listener) {
    if (!EngineGlobal.isAppCheckEnabled()) {
        // DEBUG MODE - returns hardcoded debug token
        listener.onAppCheckTokenReceived(EngineGlobal.getAppCheckDebugToken());
        return;
    }
    
    RemoteConfigApiClient remoteConfig = ...;
    if (remoteConfig != null && !remoteConfig.checkAppCheckEnabledRemotely()) {
        // Remote config can DISABLE App Check!
        listener.onAppCheckTokenReceived("");  // Empty string!
    } else {
        getFirebaseTokenImpl(listener, false);  // Real Firebase App Check
    }
}
```

**Key Finding**: App Check can be **disabled remotely** via Remote Config key `c3po` (from `EngineFeatures.java`):
```java
// EngineFeatures.java RemoteConfig class
private static final String appCheckEnabledKey = "c3po";
```

### D. Known Public Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health/liveness` | GET | Server health check - **No auth, no App Check** |

---

## Section 2: Reward Methods (Frida Hook Candidates)

### A. Core Reward Grant Flow (Client-Side Only!)

**CRITICAL FINDING**: AFK rewards and offline earnings are granted **entirely client-side** via `TransactionManager.silentGrantRewards()`. No server validation for these reward types.

#### Flow 1: AFK Rewards Dialog (`AFKRewardsDialog.java`)

```
AFKRewardsDialog.regularClaimButton.onClick()
  → LFAfkManager.claim()
    → LFAfkManager.grantPayload(RewardPayload)
      → TransactionManager.grantReward(RewardPayload, ...)
        → TransactionManager.silentGrantRewards()  // DIRECT LOCAL MODIFICATION
          → ARewardPayload.silentGrant()
            → PlayerData modification (coins, items, etc.)
```

**Key Method**: `LFAfkManager.claim(float additionalSeconds)`
- **File**: `zombieoutpost/logic/livefight/afk/LFAfkManager.java`
- **Difficulty**: 🟢 Easy - just hook and call with accumulated seconds

#### Flow 2: Offline Earnings Dialog (`JuicyOfflineEarningsDialog.java`)

```
JuicyOfflineEarningsDialog.freeButton.onClick()
  → TradeAfkManager.claimReward(RewardPayload, callback)
    → TransactionManager.grantReward(RewardPayload, ...)
      → TransactionManager.silentGrantRewards()  // DIRECT LOCAL MODIFICATION
```

**Key Method**: `TradeAfkManager.claimReward(RewardPayload, Runnable)`
- **File**: `zombieoutpost/logic/TradeAfkManager.java`
- **Difficulty**: 🟢 Easy

### B. Reward Methods Summary

| Java FQCN.method() | Trigger Dialog | Args | Hook Difficulty |
|---------------------|---------------|------|------------------|
| `LFAfkManager.claim()` | AFKRewardsDialog.regularClaimButton | none | 🟢 Easy |
| `LFAfkManager.claim(float extraSeconds)` | AFKRewardsDialog.rvClaimButton (with ad cost) | float | 🟢 Easy |
| `TradeAfkManager.claimReward(RewardPayload, Runnable)` | JuicyOfflineEarningsDialog.freeButton | RewardPayload, callback | 🟢 Easy |
| `TransactionManager.grantReward(RewardPayload, Runnable, boolean, boolean)` | All reward flows | RewardPayload, Runnable, showVisual, fromInApp | 🟡 Medium |
| `TransactionManager.silentGrantRewards(RewardPayload)` | Offline/AFK rewards | RewardPayload | 🟡 Medium |
| `ARewardPayload.silentGrant()` | Base reward | none | 🟢 Easy |

### C. Claim Parameter Structure

```java
// RewardPayload structure (com.rockbite.engine.data.shop.RewardPayload)
RewardPayload {
    Array<ARewardPayload> rewards;  // List of reward items
    String origin;        // e.g., "lf_afk", "offline"
    String originType;    // e.g., "afk_reward", "iap"
    Actor sourceActor;    // UI element for visual feedback
}

// ARewardPayload types:
// - CurrencyPayload (SC, HC, BRAVE_COIN, SEED, SHOVEL)
// - BookPayload
// - PetPayload
// - TacticalPayload
// - SCPayload (Soft Currency specific)
// - SmartPayload
```

### D. Timestamp Manipulation Targets

```java
// For modifying offline earnings duration:
// File: zombieoutpost/data/PlayerLevelData.java
public long lastLevelActivity;

// File: zombieoutpost/logic/livefight/LiveFightSaveData.java
private ProtectedLong lastCollectedTime;  // "lct" in JSON

// Get current offline seconds formula:
int secondsPassed = (currentTimeMillis - lastLevelActivity) / 1000;
int clampedSeconds = clamp(secondsPassed, 0, maxOfflineSeconds);
```

---

## Section 3: Local State Files

### A. SharedPreferences Locations

| Path | Purpose | Encrypted |
|------|---------|-----------|
| `com.badlogic.gdx.Gdx.app.getPreferences("newGameAuth")` | Auth session tokens | ❌ No |
| `com.badlogic.gdx.Gdx.app.getPreferences("com.rockbite.zombieoutpost")` | Main game prefs | ❌ No |

### B. Game Data Storage

**Main Save File**: JSON serialized `PlayerData` object

| Component | Key in PlayerData | Description |
|-----------|-------------------|-------------|
| Soft Currency (SC) | `mainGameLevelData.sc` | BigNumber |
| Hard Currency (HC) | `hc` | ProtectedLong |
| Offline Buffer | `offlineEarningsBuffer` | BigNumber |
| Brave Coins | `fundsSaveData.braveCoins` | int |
| Last Activity | `mainGameLevelData.lastLevelActivity` | long (timestamp ms) |
| Last Collected | `liveFightSaveData.lastCollectedTime` | ProtectedLong |
| Inventory | `consumableItems` | Array<ItemSaveData> |
| Quest Progress | `missionsData` | MissionsSaveData |

### C. Save File Location (Android)

```
/data/data/com.rockbite.zombieoutpost/shared_prefs/com.rockbite.zombieoutpost.xml
/data/data/com.rockbite.zombieoutpost/shared_prefs/newGameAuth.xml
/data/data/com.rockbite.zombieoutpost/files/saveData.json  (or similar)
/data/user/0/com.rockbite.zombieoutpost/files/
```

### D. Encryption Status

**❌ NO CIPHER/ENCRYPTION FOUND** for game save data.

The `ProtectedLong` class provides some obfuscation for HC (hard currency), but:
- Save files are plain JSON
- No encryption on SharedPreferences
- Direct file modification is viable

---

## Section 4: WebSocket / SSE Connections

### A. Chat WebSocket

| Property | Value |
|----------|-------|
| Host | `chatws.svc.rockbitegames.com` |
| Port | 443 |
| Protocol | WebSocket (GdxWebSockets) |
| Library | `com.github.czyzby.websocket` |
| Auth | Required (Bearer token) |

**Message Types** (from `ChatProtocol.CommandType`):
```java
AUTH, MESSAGE, UPDATE_USER_INFO, JOIN_ROOM, 
SEND_GIFT, GET_GIFT_INFO, GET_GIFT_LIST_SHORT_INFO, 
CLAIM_GIFT, REQUEST_ONLINE_LIST
```

### B. Heartbeat

```java
// From ChatClient.java
private static final byte[] heartBeat = {1};
public static final byte heartBeatResponse = 2;

// Interval: Remote config "socket_heartbeat_send_interval_seconds" (default 10s)
```

---

## Section 5: Key Files Reference

| File | Purpose |
|------|---------|
| `com/rockbite/engine/EngineFeatures.java` | All backend URLs and feature flags |
| `com/rockbite/engine/gameauth/GameAuth.java` | Auth HTTP request construction |
| `com/rockbite/engine/gameauth/NewGameAuth.java` | Session/token management |
| `com/rockbite/engine/platform/AppCheckImpl.java` | App Check implementation + bypass vector |
| `com/rockbite/zombieoutpost/logic/livefight/afk/LFAfkManager.java` | AFK reward claim logic |
| `com/rockbite/zombieoutpost/logic/TradeAfkManager.java` | Offline earnings claim |
| `com/rockbite/zombieoutpost/game/gamelogic/TransactionManager.java` | Reward grant (client-side) |
| `com/rockbite/zombieoutpost/data/PlayerLevelData.java` | lastLevelActivity field |
| `com/rockbite/zombieoutpost/logic/livefight/LiveFightSaveData.java` | lastCollectedTime field |
| `com/rockbite/engine/inbox/InboxClient.java` | Inbox message claiming |
| `com/rockbite/engine/chat/ChatClient.java` | WebSocket chat |
| `com/rockbite/engine/chat/SocketWrapper.java` | WebSocket connection |
| `com/rockbite/engine/logic/data/ASaveData.java` | Base save data class |

---

## Recommended Automation Path

### 🥇 BEST OPTION: Client-Side Reward Manipulation (No Server Bypass Needed)

**Approach**: Frida hook on `TransactionManager.silentGrantRewards()` or `LFAfkManager.claim()`

**Why This Works**:
1. AFK rewards and offline earnings are granted **entirely client-side**
2. No server validation for these reward types
3. App Check is not checked for local reward operations
4. Just need valid `sessionId`/`userId` for save to work

**Implementation Steps**:
```javascript
// Frida script pseudocode
Java.perform(function() {
    var TransactionManager = Java.use('com.rockbite.zombieoutpost.game.gamelogic.TransactionManager');
    TransactionManager.silentGrantRewards.implementation = function(rewardPayload) {
        console.log('[HOOK] silentGrantRewards called');
        console.log('[HOOK] Origin: ' + rewardPayload.origin);
        // Modify rewardPayload before granting
        // OR just call original with inflated values
        return this.silentGrantRewards(rewardPayload);
    };
});
```

**Risk**: Low detection (client-only modification, no network calls)

---

## TOP 5 Core Discoveries

1. **`https://gameauth.svc.rockbitegames.com/api/health/liveness`** - Public endpoint, no auth, no App Check. Use for server availability checking.

2. **`LFAfkManager.claim()` / `TradeAfkManager.claimReward()`** - Entire AFK/offline reward system is client-side with NO server validation. Just modify local `PlayerData`.

3. **`lastLevelActivity` timestamp** (`PlayerLevelData.java`) - Controls offline earnings duration. Manipulate this to claim maximum offline rewards.

4. **`AppCheckImpl.getAppCheckToken()`** - App Check can be disabled remotely via Remote Config key `c3po`. If server disables it, all API calls work without App Check token.

5. **`com.badlogic.gdx.Gdx.app.getPreferences("newGameAuth")`** - Session storage. Contains `sessionId` needed for authenticated API calls.
