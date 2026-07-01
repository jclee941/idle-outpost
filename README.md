# Idle Outpost Codes

> **프로모 코드 모니터링 · 일일 보상 클레임 · 안드로이드 자동화 봇**
> **Promo code monitor · daily-reward claim CLI · Android automation bot**

An integration kit for the mobile game *Idle Outpost*. The repo ships a Python
pipeline that scrapes public sources for new promotional codes, redeems them
through the game's official HTTP API, and claims daily rewards on a schedule.
An optional Android UI bot (Appium + PaddleOCR) drives the game on a real
device or emulator, and a Cloudflare Worker can trigger scheduled work from the
edge.

*Idle Outpost* 모바일 게임을 위한 통합 자동화 키트입니다. 공개 웹에서 새
프로모션 코드를 수집하고, 게임의 공식 HTTP API로 코드를 등록(Redeem)하며,
일일 보상을 자동 수령합니다. 추가로 안드로이드 디바이스/에뮬레이터에서
비전 기반 봇을 구동할 수 있고, Cloudflare Worker로 엣지 스케줄링을
연동할 수 있습니다.

---

## Table of Contents / 목차

- [Overview / 개요](#overview--개요)
- [Features / 주요 기능](#features--주요-기능)
- [Architecture / 아키텍처](#architecture--아키텍처)
- [Repository Layout / 저장소 구조](#repository-layout--저장소-구조)
- [Quick Start / 빠른 시작](#quick-start--빠른-시작)
- [Configuration / 설정](#configuration--설정)
- [Commands Reference / 명령어 레퍼런스](#commands-reference--명령어-레퍼런스)
- [Python Pipeline / 파이썬 파이프라인](#python-pipeline--파이썬-파이프라인)
- [Android Bot / 안드로이드 봇](#android-bot--안드로이드-봇)
- [Cloudflare Worker](#cloudflare-worker)
- [Local Development / 로컬 개발](#local-development--로컬-개발)
- [Testing / 테스트](#testing--테스트)
- [Troubleshooting / 문제 해결](#troubleshooting--문제-해결)
- [Contributing / 기여](#contributing--기여)
- [Disclaimer / 면책](#disclaimer--면책)
- [License / 라이선스](#license--라이선스)

---

## Overview / 개요

The repository is composed of three loosely-coupled Python pipelines, an
Android UI bot, and an optional Cloudflare Worker. They share a single
persistence layer (`store.py`) and a single outbound notifier
(`notifier.py`), so every stage is idempotent and restart-safe.

이 저장소는 세 개의 파이썬 파이프라인, 안드로이드 UI 봇, 그리고 Cloudflare
Worker로 구성됩니다. 모든 단계는 `store.py`의 영속 레이어와 `notifier.py`의
알림 모듈을 공유하므로 멱등(idempotent)하며 재시작에 안전합니다.

| Component / 구성요소 | Entry point / 진입점         | Runtime / 런타임 | Purpose / 목적                                                              |
|---------------------|------------------------------|------------------|-----------------------------------------------------------------------------|
| Promo monitor       | `python main.py scrape`      | Python 3.11+     | Crawl public sources, extract codes, persist them. 공개 소스 크롤링·코드 추출·저장 |
| Code redeemer       | `python main.py redeem`      | Python 3.11+     | Submit stored codes to the game API. 저장된 코드를 게임 API에 등록         |
| Daily claimer       | `python main.py claim`       | Python 3.11+     | Trigger daily reward sign-in. 일일 보상 사인인 트리거                      |
| Android bot         | `python -m idle_outpost_bot` | Appium + PaddleOCR | Drive the game UI on a real device. 디바이스에서 게임 UI 자동 조작         |
| Edge scheduler      | `worker/src/index.ts`        | Cloudflare Worker | Trigger `claim`/`redeem` from a cron handler. 엣지에서 `claim`/`redeem` 호출 |

---

## Features / 주요 기능

- **Code scraping** — `scraper.py` uses `httpx` + `beautifulsoup4` to pull
  promo code listings from configured URLs and parses candidate codes.
- **Safe redemption** — `redeemer.py` signs requests, de-duplicates against
  `store.py`, and only submits codes that have never been tried.
- **Daily reward claim** — `claim_api.py` hits the in-game `daily` endpoint
  on a cadence and records per-account timestamps.
- **Idempotent storage** — `store.py` persists codes, attempts, and last-claim
  timestamps (SQLite by default) so retries are safe across restarts.
- **Notifications** — `notifier.py` fans out results to a generic webhook so
  the same channel works for Discord, Slack, ntfy, etc.
- **Android vision bot** — `idle_outpost_bot/` captures screenshots via
  Appium, runs OCR/templates with PaddleOCR + OpenCV-style matching, and
  performs calibrated swipes and taps to advance the player loop.
- **Edge scheduling** — `worker/` exposes a cron handler that POSTs into the
  pipeline so you don't need a long-running host.
- **Bilingual UX** — UI text is wired through `idle_outpost_bot/i18n_ko.properties`
  for Korean locale matching.

---

## Architecture / 아키텍처

### High-level flow / 상위 흐름

1. `scraper.py` fetches promo pages and writes candidate codes into
   `store.py`.
2. `redeemer.py` reads *unattempted* codes, signs them, submits to the game
   API, and writes the outcome back into `store.py`.
3. `claim_api.py` checks the last claim timestamp per player in `store.py`
   and, if the cooldown has elapsed, hits the in-game daily endpoint.
4. `notifier.py` reports per-step results to the configured webhook.
5. The Android bot operates orthogonally: it does not require the HTTP
   pipeline and uses `state.py` + `vision.py` instead, but shares
   `notifier.py`.

### Data contracts / 데이터 계약

| Store entity / 엔티티 | Fields / 필드                                                                                   | Owner / 책임 모듈       |
|-----------------------|------------------------------------------------------------------------------------------------|-------------------------|
| `code`                | `value`, `source`, `first_seen`, `tried`, `result`                                             | `scraper.py`, `redeemer.py` |
| `claim_log`           | `player_id`, `claimed_at`, `reward`, `response_code`                                          | `claim_api.py`          |
| `bot_state`           | `screen`, `last_action`, `coins`, `gems`, `energy`, `quests_done`, `last_daily_claim`          | `idle_outpost_bot/state.py` |
| `calibration`         | image templates + `*.ocr.yaml` region descriptors keyed by screen name                          | `idle_outpost_bot/calibrate.py` |

### Module responsibilities / 모듈 책임

| Module / 모듈            | Role / 역할                                                                            |
|--------------------------|----------------------------------------------------------------------------------------|
| `auth.py`                | Build signed request headers for the in-game API. 서명된 요청 헤더 생성                |
| `claim_api.py`           | Hit the daily-claim endpoint with cooldown enforcement. 데일리 클레임 호출            |
| `main.py`                | CLI dispatch (`scrape`, `redeem`, `claim`, `serve`). CLI 디스패치                       |
| `notifier.py`            | Single outbound webhook adapter. 단일 웹훅 아웃바운드 어댑터                           |
| `redeemer.py`            | Submit stored codes against the official API. 코드 등록                                |
| `scraper.py`             | Crawl configured sources and extract candidate codes. 후보 코드 추출                    |
| `store.py`               | SQLite-backed persistence shared by all three pipelines. 공유 SQLite 영속 레이어       |
| `worker/src/index.ts`   | Cloudflare Worker cron → POSTs into the pipeline. 엣지 크론 호출                       |
| `idle_outpost_bot/*`     | Android UI bot — driver, vision, calibration, loop, safety, actions, notify, state, settings |

---

## Repository Layout / 저장소 구조

```
.
├── auth.py                  # API request signer
├── claim_api.py             # Daily reward claimer
├── main.py                  # CLI entry point
├── notifier.py              # Outbound webhook adapter
├── pyproject.toml           # Project metadata + dependencies
├── redeemer.py              # Promo code redemption
├── scraper.py               # Promo code scraper
├── store.py                 # SQLite-backed persistence
├── uv.lock                  # uv lockfile
├── video1.png               # Reference screenshot
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── idle_outpost_bot/        # Android UI bot package
│   ├── __init__.py
│   ├── __main__.py
│   ├── actions.py
│   ├── auto_calibrate.py
│   ├── calibrate.py
│   ├── config_loader.py
│   ├── discover.py
│   ├── driver.py
│   ├── i18n_ko.properties
│   ├── loop.py
│   ├── notify.py
│   ├── safety.py
│   ├── settings.py
│   ├── state.py
│   ├── vision.py
│   ├── AD_REWARDS.md
│   ├── API_RESEARCH.md
│   ├── AUTOMATION_TARGETS.md
│   ├── CALIBRATION_FULL.md
│   ├── JADX_FULL_INVENTORY.md
│   ├── README.md
│   └── calibration/         # OCR templates + reference images
│       ├── after_cards.png + .ocr.yaml
│       ├── after_quest.png + .ocr.yaml
│       ├── after_tasks.png + .ocr.yaml
│       ├── back_close.png + .ocr.yaml
│       ├── back_from_cards.png + .ocr.yaml
│       ├── calendar.png + .ocr.yaml / .yaml
│       ├── cards.png + .ocr.yaml
│       ├── check_screen.png + .ocr.yaml
│       ├── clean_main.png + .ocr.yaml
│       ├── closed2.png + .ocr.yaml
│       ├── closed_check.png + .ocr.yaml
│       ├── fresh_main.png + .ocr.yaml
│       ├── game_ready.png + .ocr.yaml
│       ├── inbox.png + .ocr.yaml
│       ├── main.png + main_screen.png + main_screen.yaml
│       ├── main_screen.ocr.yaml
│       ├── mainscreen_check.png + .ocr.yaml
│       ├── quest_board.png + .ocr.yaml
│       ├── restart_check.png + .ocr.yaml
│       ├── swipe_test.png + .ocr.yaml
│       ├── p2_*.png            # Phase-2 probes
│       └── probe_*.png         # Live-screen probes
└── worker/                # Cloudflare Worker
    ├── package.json
    ├── package-lock.json
    ├── tsconfig.json
    ├── wrangler.jsonc
    ├── README.md
    └── src/
        └── index.ts
```

> **Note / 참고** — The `idle_outpost_bot/calibration/` directory doubles as a
> versioned reference set: each `*.png` is a captured screen, and each
> matching `*.ocr.yaml` (or `*.yaml`) describes the regions, expected
> strings, and tolerances that `vision.py` uses to recognize that screen.
> Adding new flows means dropping new PNGs + descriptors here and extending
> `calibrate.py` / `auto_calibrate.py`.

---

## Quick Start / 빠른 시작

### 1. Clone and install / 클론 및 설치

```bash
git clone <repository-url> idle-outpost-codes
cd idle-outpost-codes

# Choose one of the package managers
uv sync                    # uses uv.lock
# or
python -m venv .venv
source .venv/bin/activate
pip install -e .           # HTTP pipeline only
pip install -e ".[bot]"    # HTTP pipeline + Android bot extras
```

### 2. Configure / 설정

```bash
cp .env.example .env  # if present; otherwise create manually
```

Minimum variables for the HTTP pipeline:

```
PLAYER_ID=...
AUTH_TOKEN=...
GAME_API_BASE=https://api.idleoutpost.example
NOTIFY_WEBHOOK=https://your.webhook/endpoint
DB_PATH=./data/store.sqlite
```

### 3. Run a single scrape + redeem + claim / 1회 실행

```bash
python main.py scrape
python main.py redeem
python main.py claim
```

### 4. Run the Android bot / 안드로이드 봇 실행

```bash
# Pre-requisites
# - Appium server running locally
# - ADB device connected (real phone or emulator)
# - The Idle Outpost APK installed on the device
pip install -e ".[bot]"
python -m idle_outpost_bot
```

### 5. Deploy the Worker (optional) / Worker 배포

```bash
cd worker
npm install
npx wrangler deploy
```

---

## Configuration / 설정

### Environment variables / 환경 변수

| Variable / 변수      | Required / 필수 | Default / 기본값         | Description / 설명                                              |
|----------------------|-----------------|--------------------------|------------------------------------------------------------------|
| `PLAYER_ID`          | yes             | —                        | Player identifier sent to the daily-claim API. 플레이어 식별자   |
| `AUTH_TOKEN`         | yes             | —                        | Bearer token used by `auth.py`. 인증 토큰                        |
| `GAME_API_BASE`      | recommended     | (built-in default)       | Base URL of the in-game HTTP API. 게임 API 베이스 URL            |
| `DB_PATH`            | no              | `./data/store.sqlite`    | SQLite file used by `store.py`. SQLite 경로                      |
| `NOTIFY_WEBHOOK`     | no              | empty                    | Webhook URL passed to `notifier.py`. 알림 웹훅                   |
| `SCRAPER_URLS`       | no              | built-in list            | Newline-separated source URLs for `scraper.py`. 크롤링 대상 URL    |
| `BOT_DEVICE_UDID`    | for bot only    | empty                    | ADB device identifier for Appium. Appium용 디바이스 UDID         |
| `BOT_APP_PACKAGE`    | for bot only    | `com.idleoutpost.game`   | App package name on Android. 안드로이드 패키지명                 |
| `BOT_LOCALE`         | no              | `ko-KR`                  | Locale for OCR region matching. OCR 로케일                       |
| `WORKER_TARGET_URL`  | worker only     | —                        | Pipeline endpoint the Worker POSTs into. Worker 호출 대상 URL    |

### Bot settings / 봇 설정

`idle_outpost_bot/settings.py` exposes tuning parameters for the UI bot:
screen dwell timeout, OCR confidence floor, swipe duration, daily-claim
cooldown, and so on. Override them either through environment variables
(prefixed `BOT_`) or by mounting a custom `settings.yaml` next to
`config_loader.py`.

---

## Commands Reference / 명령어 레퍼런스

### Python CLI (`main.py`)

| Command                | Description / 설명                                                              |
|------------------------|---------------------------------------------------------------------------------|
| `python main.py scrape`| Pull current promo codes from configured sources and persist them. 코드 수집  |
| `python main.py redeem`| Submit all untried codes to the in-game API. 코드 등록                          |
| `python main.py claim` | Run a daily-claim if the cooldown elapsed. 일일 보상 클레임                      |
| `python main.py serve` | (Optional) Long-running scheduler that triggers the above on cron. 통합 데몬   |

Typical cron schedule:

```cron
*/30 * * * *  cd /srv/idle-outpost && .venv/bin/python main.py scrape
*/10 * * * *  cd /srv/idle-outpost && .venv/bin/python main.py redeem
0   8 * * *  cd /srv/idle-outpost && .venv/bin/python main.py claim
```

### Bot CLI (`idle_outpost_bot`)

| Command                              | Description / 설명                                                       |
|--------------------------------------|--------------------------------------------------------------------------|
| `python -m idle_outpost_bot`         | Run the main `loop.py` against the connected device. 메인 루프 실행     |
| `python -m idle_outpost_bot discover`| One-shot screen discovery: dumps probes into `calibration/probe_*.png`. 화면 디스커버리 |
| `python -m idle_outpost_bot calibrate`| Re-anchor OCR regions from captured screenshots. OCR 재캘리브레이션     |
| `python -m idle_outpost_bot auto-calibrate` | Run end-to-end calibration driven by `calibrate.py`. 전체 자동 캘리브레이션 |

### Worker (`wrangler`)

| Command                       | Description / 설명                                        |
|-------------------------------|------------------------------------------------------------|
| `npx wrangler dev`            | Local Worker sandbox. 로컬 Worker 실행                   |
| `npx wrangler deploy`         | Deploy cron trigger to Cloudflare. Cloudflare에 배포     |
| `npx wrangler tail`           | Live log streaming. 실시간 로그 스트리밍                  |

---

## Python Pipeline / 파이썬 파이프라인

### `scraper.py`

- Reads `SCRAPER_URLS` and the built-in defaults.
- Uses `httpx` with sane timeouts and `beautifulsoup4` for HTML parsing.
- Returns a list of `{code, source, first_seen}` records; `store.py`
  ignores duplicates by `(source, code)`.

### `redeemer.py`

- Pulls untried codes from `store.py`.
- Delegates signing to `auth.py` and submission to the redeem endpoint.
- Records each attempt with status (`ok`, `expired`, `already_used`,
  `error`) so subsequent runs skip finished work.

### `claim_api.py`

- Reads `claim_log.last_claimed_at` per `player_id`.
- Honors a cooldown (default 24h, configurable) to avoid hitting
  the endpoint more than once per game day.

### `store.py`

- Light SQLite wrapper with three tables: `code`, `claim_log`, `bot_state`.
- Thread-safe through a single connection guarded by a lock.
- Schema migrations live inside `store.py`; bump the module-level
  schema version when adding columns.

### `notifier.py`

- One function: `notify(event: str, payload: dict) -> None`.
- Single webhook target, configurable payload shape (`text`,
  `discord`, `slack`).
- Failures are logged, not raised — a webhook outage should not
  block the pipeline.

### `auth.py`

- Builds `Authorization` and per-request `X-Sign` headers from
  `AUTH_TOKEN` and a deterministic signature over request body.
- Detail conventions are documented in `idle_outpost_bot/API_RESEARCH.md`.

---

## Android Bot / 안드로이드 봇

### Runtime requirements / 런타임 요구사항

| Requirement / 요구사항 | Notes / 비고                                                                          |
|------------------------|---------------------------------------------------------------------------------------|
| Android device         | USB debugging enabled, or an emulator (e.g., Android Studio AVD). USB 디버깅 활성화  |
| ADB on host            | `adb devices` shows your target.                                                      |
| Appium server          | v2.x recommended; `appium` and `appium-uiautomator2-driver`. Appium 서버               |
| Idle Outpost APK       | Installed on the device. APK 설치                                                      |
| Python extras          | `pip install -e ".[bot]"` installs Appium-Python-Client, PaddleOCR, PaddlePaddle, Pillow. |

### Modules / 모듈

| Module / 모듈        | Role / 역할                                                                              |
|----------------------|------------------------------------------------------------------------------------------|
| `driver.py`          | Boots Appium session, exposes `screenshot()`, `tap()`, `swipe()`. Appium 세션 래퍼       |
| `vision.py`          | PaddleOCR + template matching over screenshots. OCR + 템플릿 매칭                         |
| `discover.py`        | Captures the current screen and writes `probe_*.png` for offline analysis. 화면 디스커버리 |
| `calibrate.py`       | Interactive/manual re-anchoring of OCR regions against captured screens. 수동 캘리브레이션 |
| `auto_calibrate.py`  | Heuristic full pass that re-anchors many regions at once. 자동 캘리브레이션              |
| `actions.py`         | High-level intents: `open_calendar`, `claim_daily`, `watch_ad`, etc. 고수준 액션         |
| `loop.py`            | The main player loop combining `state`, `vision`, `actions`, `safety`. 메인 루프          |
| `safety.py`          | Guards: human-present detection, playtime caps, anti-stuck heuristics. 안전 가드          |
| `state.py`           | Persistent screen-state, currency/energy counters, last-claim timestamp. 상태 영속        |
| `notify.py`          | Reuses the same webhook target with bot-specific event names. 봇용 알림                   |
| `settings.py`        | Tunables: dwell time, OCR confidence floor, swipes per second. 튜닝 파라미터               |
| `config_loader.py`   | Loads YAML/JSON config files. YAML/JSON 설정 로더                                         |
| `i18n_ko.properties` | Korean locale strings used by `vision.py` for region matching. 한국어 로케일 문자열      |

### Calibration assets / 캘리브레이션 자산

`idle_outpost_bot/calibration/` pairs reference PNGs with `.ocr.yaml` (or
`.yaml`) descriptors. Heads-up:

- `main_screen.png` + `main_screen.yaml` is the canonical "we are on the
  home screen" anchor. Most other screens reference it.
- `after_*` and `*_check` assets are post-action verification screens —
  the bot uses them to confirm a tap registered before continuing.
- `probe_*` images are live-screen dumps produced by `discover.py`; treat
  them as inputs to a future calibration, not as long-lived references.
- `p2_*` images correspond to phase-2 features (ads, trades, events) and
  are documented in `AUTOMATION_TARGETS.md`.

### Bot safety / 봇 안전장치

`safety.py` enforces:

- A maximum continuous runtime and a mandatory pause between sessions.
- Detection of unexpected dialogs (system permission prompts,
  "are you still there?") with auto-dismiss heuristics that refuse to
  click anything resembling a payment button.
- Logging of every captured screenshot so regressions can be
  diagnosed offline.

---

## Cloudflare Worker

`worker/` is a minimal cron handler that POSTs into your deployed
pipeline. It is decoupled from the Python code; you point it at any
HTTPS endpoint that runs `main.py claim` or `main.py redeem`.

```text
┌──────────────────────┐    cron    ┌────────────────────┐    HTTPS     ┌─────────────────────┐
│ Cloudflare Workers  │ ─────────▶ │ worker/src/index.ts│ ───────────▶ │ Your pipeline host  │
└──────────────────────┘            └────────────────────┘              │  /claim, /redeem    │
                                                                        └─────────────────────┘
```

`wrangler.jsonc` configures the cron trigger(s) and the
`WORKER_TARGET_URL` KV binding. See `worker/README.md` for the latest
contract details.

---

## Local Development / 로컬 개발

| Tool / 도구         | Purpose / 목적                                                                       |
|---------------------|--------------------------------------------------------------------------------------|
| `uv`                | Fast Python package/dependency manager; reads `uv.lock`. 빠른 의존성 관리           |
| `ruff`              | Linting (`ruff check`). 린트                                                        |
| `basedpyright`      | Static type checking (configured in `pyproject.toml`). 정적 타입 검사                 |
| `pytest`            | Test runner (add your own tests under `tests/`). 테스트 러너                         |
| `npm` / `wrangler`  | Worker build, dev, deploy. Worker 빌드·배포                                         |

Suggested developer loop:

```bash
# Python side
uv sync --all-extras          # include bot deps
ruff check .
basedpyright .
pytest                        # once tests exist

# Worker side
cd worker
npm install
npx wrangler dev
```

---

## Testing / 테스트

The repo currently ships without a test suite — every stage is idempotent
and the SQLite store makes it easy to add fixtures. Suggested starting
points when adding tests:

| Area / 영역            | Suggested test / 권장 테스트                                                       |
|------------------------|-----------------------------------------------------------------------------------|
| `scraper.py`           | Frozen HTML fixture → expected code list. HTML 픽스처 기반 파서 테스트            |
| `redeemer.py`          | Stub the HTTP client → confirm dedup via `store.py`. HTTP 스텁 + 중복 제거 테스트 |
| `claim_api.py`         | Inject `now()` → assert cooldown enforcement. 쿨다운 검증                          |
| `store.py`             | Round-trip insert/read for each table. 영속 라운드트립                              |
| `notifier.py`          | Mock `httpx` → assert payload shape. 페이로드 형식 검증                            |
| `idle_outpost_bot/vision.py` | Replay captured screenshots → assert screen labels. 스크린샷 리플레이            |

> **Pull requests that change behavior should include a regression
> test.** 동작 변경 PR은 회귀 테스트를 포함해주세요.

---

## Troubleshooting / 문제 해결

| Symptom / 증상                                              | Likely cause / 원인                                              | Fix / 해결                                                                       |
|-------------------------------------------------------------|------------------------------------------------------------------|----------------------------------------------------------------------------------|
| `python main.py redeem` reports `already_used` for every code | `AUTH_TOKEN` rotated or expired. 인증 토큰 만료/재발급           | Refresh credentials; `auth.py` honors the env variable on every call.            |
| Bot stuck on `main_screen` check                            | UI text changed between game versions. 게임 버전 변경            | Run `python -m idle_outpost_bot auto-calibrate`, then verify `main_screen.yaml`. |
| `notifier.py` logs `webhook 4xx`                           | Webhook URL wrong or requires auth. 웹훅 인증 누락               | Update `NOTIFY_WEBHOOK`; payload format is documented in `notifier.py`.         |
| PaddleOCR slow first run                                   | Model download on first import. 첫 실행 시 모델 다운로드          | Pre-warm by running `python -c "from paddleocr import PaddleOCR; PaddleOCR(use_angle_cls=False)"`. |
| Cloudflare Worker 500s on cron                             | `WORKER_TARGET_URL` unreachable from the edge. 엣지에서 도달 불가 | Confirm DNS + the target accepts POST. Worker logs are visible via `wrangler tail`. |
| `store.py` locked errors                                   | Two processes opened the same SQLite path. 동일 DB 동시 접근      | Single-writer pattern; use `python main.py serve` if you want a coordinator.      |

---

## Contributing / 기여

1. Fork and create a feature branch.
2. Run `ruff check .` and `basedpyright` before pushing.
3. Add or update a calibration asset whenever you change
   `idle_outpost_bot/vision.py` matching logic.
4. Update the relevant deep-dive (`API_RESEARCH.md`,
   `AUTOMATION_TARGETS.md`, `JADX_FULL_INVENTORY.md`,
   `CALIBRATION_FULL.md`, `AD_REWARDS.md`) if your change touches the
   area they cover.
5. Open a pull request describing the behavior change and the
   observable effect (screenshots encouraged for bot changes).

See `CONTRIBUTING.md` for the full guidelines.

---

## Disclaimer / 면책

This repository is an unofficial integration kit for the mobile game
*Idle Outpost*. It interacts with publicly visible web sources and with
the in-game HTTP API, but it does **not** modify the game client or any
binary distributed by the game's publisher. Running automated clients
against third-party services may violate their terms of service — use
this code at your own risk and prefer the official channels for
support and account recovery.

이 저장소는 모바일 게임 *Idle Outpost*의 비공식 통합 키트입니다. 공개 웹
소스와 게임 내 HTTP API를 사용하지만 게임 클라이언트/바이너리를 수정하지
않습니다. 자동화된 클라이언트를 제3자 서비스에 대해 실행하는 것이 해당
이용약관을 위반할 수 있으며, 모든 책임은 사용자에게 있습니다.

---

## License / 라이선스

Released under the terms in `LICENSE`. By contributing, you agree your
contributions are licensed under the same terms.

이 저장소는 `LICENSE` 파일의 조건에 따라 배포됩니다. 기여 시 동일한
조건으로 라이선스됨에 동의한 것으로 간주됩니다.