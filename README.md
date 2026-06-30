# Idle Outpost Codes

> **프로모 코드 모니터링 · 일일 보상 클레임 · 안드로이드 자동화 봇**
> **Promo code monitor · daily-reward claim CLI · Android automation bot**

A monorepo of automation tools for the mobile game *Idle Outpost*. The project contains a Python pipeline that scrapes the public web for new promotional codes, redeems them against the official game HTTP API, and claims daily rewards on a schedule. Optionally, an Android UI bot (Appium + PaddleOCR) drives the game on a real device or emulator, and a Cloudflare Worker can trigger scheduled work from the edge.

*Idle Outpost* 모바일 게임을 위한 통합 자동화 키트입니다. 공개 웹에서 새 프로모션 코드를 수집하고, 게임의 공식 HTTP API로 코드를 등록(Redeem)하며, 일일 보상을 자동 수령하고, 선택적으로 안드로이드 디바이스에서 비전 기반 봇을 구동합니다. Cloudflare Worker를 통한 엣지 스케줄링도 지원합니다.

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

The repository is composed of three loosely coupled Python pipelines, an Android UI bot, and an optional Cloudflare Worker. They share a single persistence layer (`store.py`) and a single outbound notifier (`notifier.py`), so every stage is idempotent and restart-safe.

이 저장소는 세 개의 파이썬 파이프라인, 안드로이드 UI 봇, 그리고 Cloudflare Worker로 구성됩니다. 모든 단계는 `store.py`의 영속 레이어와 `notifier.py`의 알림 모듈을 공유하므로 멱등(idempotent)하며 재시작에 안전합니다.

| Component / 구성요소 | Entry point / 진입점 | Responsibility / 역할 |
| --- | --- | --- |
| Promo monitor / 프로모 모니터 | `scraper.py` | Discovers new codes from configured web sources via `httpx` + BeautifulSoup / 설정된 웹 소스에서 새 코드 수집 |
| Code redeemer / 코드 리디머 | `redeemer.py` | Posts each fresh code to the official game HTTP API / 공식 게임 API로 코드 등록 |
| Daily claim CLI / 일일 클레임 | `claim_api.py` | Claims daily rewards on a schedule / 일일 보상 자동 수령 |
| Auth helper / 인증 헬퍼 | `auth.py` | Manages session tokens and credentials / 세션 토큰 및 자격 증명 관리 |
| Persistence / 영속화 | `store.py` | Dedupes codes and tracks per-account claim history / 코드 중복 제거 및 계정별 클레임 이력 |
| Notifier / 알림 | `notifier.py` | Sends outbound notifications on events / 이벤트 알림 발송 |
| Pipeline orchestrator / 오케스트레이터 | `main.py` | Runs the monitor + redeem + claim loop end-to-end / 모니터·리딤·클레임 루프 통합 실행 |
| Android UI bot / 안드로이드 봇 | `idle_outpost_bot/__main__.py` | Vision-driven automation on a device / 디바이스에서 비전 기반 자동화 |
| Edge scheduler / 엣지 스케줄러 | `worker/src/index.ts` | Cloudflare Worker that triggers the pipeline on a cron / 크론으로 파이프라인 트리거 |

---

## Features / 주요 기능

| EN | KO |
| --- | --- |
| Web scraper for new promo codes from configured sources | 설정된 소스에서 새 프로모 코드 자동 수집 |
| HTTP redemption against the official game API | 공식 게임 API에 코드 자동 등록 |
| Daily-reward claim CLI with per-account history | 계정별 이력이 있는 일일 보상 클레임 CLI |
| Idempotent local store: safe to re-run | 멱등 로컬 저장소: 재실행 안전 |
| Pluggable notifier (webhook/email/etc.) | 플러그 가능한 알림 모듈 (웹훅/이메일 등) |
| Optional Android bot: Appium + PaddleOCR + Selenium | 옵션 안드로이드 봇: Appium + PaddleOCR + Selenium |
| Vision calibration assets and OCR templates | 비전 캘리브레이션 자산 및 OCR 템플릿 |
| Korean localization (`i18n_ko.properties`) | 한국어 로컬라이제이션 (`i18n_ko.properties`) |
| Cloudflare Worker for edge-triggered scheduling | 엣지 트리거용 Cloudflare Worker |
| `uv` lockfile for reproducible Python installs | 재현 가능한 파이썬 설치를 위한 `uv` 락파일 |

---

## Architecture / 아키텍처

### High-level data flow / 데이터 흐름

1. **Discover / 수집** — `scraper.py` fetches candidate code pages with `httpx`, parses with BeautifulSoup, extracts code tokens, and forwards them to `store.py`.
2. **Dedup / 중복 제거** — `store.py` records each code as `seen`, `redeemed`, `expired`, or `failed` keyed by source URL and code string.
3. **Redeem / 등록** — `redeemer.py` authenticates via `auth.py`, then calls the game's official HTTP API through `claim_api.py`-style HTTP helpers for every unseen code.
4. **Claim / 클레임** — On a separate schedule, the same `claim_api.py` posts the daily-reward endpoint for each configured account.
5. **Notify / 알림** — On every state transition (`seen → redeemed`, `failed`, `expired`), `notifier.py` emits a structured event.
6. **Bot (optional) / 봇(옵션)** — `idle_outpost_bot` runs on top of the same `store.py` mirror so the bot and the HTTP pipeline never double-claim.

| Stage / 단계 | Module / 모듈 | Output state / 출력 상태 | Restart-safe? / 재시작 안전 |
| --- | --- | --- | --- |
| Scrape | `scraper.py` | `seen` | Yes / 예 |
| Redeem | `redeemer.py` + `auth.py` | `redeemed` / `failed` | Yes / 예 |
| Daily claim | `claim_api.py` | `claimed` per day | Yes / 예 |
| Notify | `notifier.py` | outbound event | Yes / 예 |
| Bot claim | `idle_outpost_bot/loop.py` | `claimed` per day | Yes / 예 |

### Process map / 프로세스 맵

| Process / 프로세스 | Runtime / 런타임 | Trigger / 트리거 | Notes / 비고 |
| --- | --- | --- | --- |
| `main.py` | Python 3.11+ | CLI / cron | End-to-end monitor + redeem + claim / 모니터·리딤·클레임 통합 |
| `worker/src/index.ts` | Cloudflare Workers (V8) | Cron trigger / HTTP | Calls a webhook to start `main.py` on a host / 호스트의 `main.py` 호출 |
| `idle_outpost_bot/__main__.py` | Python 3.11+ | Manual / scheduled | Requires an Android device or emulator and Appium server / 안드로이드 디바이스/에뮬레이터 및 Appium 서버 필요 |

---

## Repository Layout / 저장소 구조

```text
.
├── auth.py                    # Session/auth helpers for the game HTTP API
├── claim_api.py               # Daily-reward claim + HTTP helpers
├── main.py                    # Pipeline orchestrator (monitor → redeem → claim)
├── notifier.py                # Outbound notification dispatcher
├── pyproject.toml             # Python project metadata + optional bot deps
├── redeemer.py                # Code redemption against the official API
├── scraper.py                 # Web scraper for new promo codes
├── store.py                   # Idempotent local store / dedupe layer
├── uv.lock                    # uv-managed lockfile
├── video1.png                 # Demo / preview asset
├── worker/                    # Cloudflare Worker (edge scheduler)
│   ├── README.md
│   ├── package.json
│   ├── package-lock.json
│   ├── tsconfig.json
│   ├── wrangler.jsonc
│   └── src/
│       └── index.ts
└── idle_outpost_bot/          # Android UI automation bot
    ├── README.md
    ├── __init__.py
    ├── __main__.py            # Bot entry point
    ├── actions.py             # High-level UI actions
    ├── auto_calibrate.py      # Auto calibration flow
    ├── calibrate.py           # Manual calibration
    ├── config_loader.py       # YAML config loader
    ├── discover.py            # UI element discovery
    ├── driver.py              # Appium driver wrapper
    ├── i18n_ko.properties     # Korean strings
    ├── loop.py                # Main bot loop
    ├── notify.py              # Bot-side notifier
    ├── safety.py              # Safety guards / cooldowns
    ├── settings.py            # Bot settings
    ├── state.py               # Bot state
    ├── vision.py              # PaddleOCR + image matching
    ├── AD_REWARDS.md
    ├── API_RESEARCH.md
    ├── AUTOMATION_TARGETS.md
    ├── CALIBRATION_FULL.md
    ├── JADX_FULL_INVENTORY.md
    └── calibration/           # OCR templates and probe screenshots
        ├── *.png
        └── *.ocr.yaml / *.yaml
```

---

## Quick Start / 빠른 시작

### Prerequisites / 사전 요구사항

| Tool / 도구 | Version / 버전 | Purpose / 용도 |
| --- | --- | --- |
| Python | 3.11+ | Run the pipeline and the bot / 파이프라인 및 봇 실행 |
| uv (recommended) | latest | Reproducible installs / 재현 가능한 설치 |
| Node.js | 18+ | Build the Worker / Worker 빌드 (선택) |
| Appium server | 2.x | Required only for the Android bot / 안드로이드 봇에서만 필요 |
| Android device / emulator | Android 9+ | Required only for the Android bot / 안드로이드 봇에서만 필요 |

### Install / 설치

```bash
# Clone
git clone <REPO_URL> idle-outpost-codes
cd idle-outpost-codes

# Python dependencies (pipeline only)
uv sync

# Optional: install the Android bot dependencies
uv sync --extra bot
```

### Configure / 설정

Create a `.env` file at the repository root. See [Configuration](#configuration--설정) for the full list of variables.

```dotenv
# Example / 예시
GAME_API_BASE_URL=https://api.example-game.com
GAME_ACCOUNT_ID=your_account_id
GAME_AUTH_TOKEN=your_auth_token
NOTIFIER_WEBHOOK_URL=https://your-webhook.example/notify
STORE_PATH=./var/store.json
```

### Run / 실행

```bash
# Run the full pipeline once / 파이프라인 1회 실행
uv run python main.py

# Run only the scraper / 스크레이퍼만 실행
uv run python scraper.py

# Run only the redeemer / 리디머만 실행
uv run python redeemer.py

# Run only the daily claim / 일일 클레임만 실행
uv run python claim_api.py

# Run the Android bot (requires Appium server + device) / 안드로이드 봇 실행
uv run python -m idle_outpost_bot
```

---

## Configuration / 설정

The pipeline reads configuration from environment variables (loaded via `python-dotenv` from a local `.env`) and from YAML files inside `idle_outpost_bot/`. The exact keys consumed by each module are documented in the module itself; the variables below are the conventional names.

| Variable / 변수 | Used by / 사용처 | Description / 설명 |
| --- | --- | --- |
| `GAME_API_BASE_URL` | `auth.py`, `redeemer.py`, `claim_api.py` | Base URL of the official game HTTP API / 공식 게임 API의 베이스 URL |
| `GAME_ACCOUNT_ID` | `auth.py`, `claim_api.py` | Account identifier / 계정 식별자 |
| `GAME_AUTH_TOKEN` | `auth.py` | Session token or refresh token / 세션/리프레시 토큰 |
| `STORE_PATH` | `store.py` | Local JSON store path / 로컬 JSON 저장 경로 |
| `NOTIFIER_WEBHOOK_URL` | `notifier.py` | Webhook destination for events / 이벤트 웹훅 |
| `NOTIFIER_KIND` | `notifier.py` | `webhook`, `email`, or `noop` / 알림 종류 |
| `SCRAPE_SOURCES` | `scraper.py` | Comma-separated list of source URLs / 소스 URL 목록 (콤마 구분) |
| `REDEEM_DRY_RUN` | `redeemer.py` | `1` to skip actual API calls / 실제 호출 건너뛰기 |
| `BOT_DEVICE_UDID` | `idle_outpost_bot/driver.py` | Target Android device UDID / 대상 안드로이드 디바이스 UDID |
| `BOT_APPIUM_URL` | `idle_outpost_bot/driver.py` | Appium server URL (default `http://127.0.0.1:4723`) |
| `BOT_CALIBRATION_DIR` | `idle_outpost_bot/vision.py` | Path to `idle_outpost_bot/calibration/` |

> Do not commit `.env` to version control. Treat `GAME_AUTH_TOKEN` and any webhook secrets as sensitive.
>
> `.env` 파일은 버전 관리에 커밋하지 마세요. `GAME_AUTH_TOKEN` 및 웹훅 시크릿은 민감 정보입니다.

---

## Commands Reference / 명령어 레퍼런스

### Python pipeline / 파이썬 파이프라인

| Command / 명령어 | Description / 설명 |
| --- | --- |
| `uv run python main.py` | Run monitor → redeem → claim end-to-end / 모니터→리딤→클레임 통합 실행 |
| `uv run python scraper.py` | Scrape configured sources, persist new codes / 소스 스크레이핑 후 새 코드 저장 |
| `uv run python redeemer.py` | Redeem all `seen` codes against the API / `seen` 코드 모두 등록 |
| `uv run python claim_api.py` | Trigger daily-reward claim / 일일 보상 클레임 트리거 |
| `uv run python auth.py` | Verify/refresh credentials / 자격 증명 확인/갱신 |
| `uv run python notifier.py` | Send a test notification / 테스트 알림 발송 |

### Android bot / 안드로이드 봇

| Command / 명령어 | Description / 설명 |
| --- | --- |
| `uv run python -m idle_outpost_bot` | Start the bot loop / 봇 루프 시작 |
| `uv run python -m idle_outpost_bot --calibrate` | Run manual calibration / 수동 캘리브레이션 |
| `uv run python -m idle_outpost_bot --auto-calibrate` | Run auto calibration / 자동 캘리브레이션 |
| `uv run python -m idle_outpost_bot --discover` | Dump discovered UI elements / UI 요소 덤프 |

### Cloudflare Worker

| Command / 명령어 | Description / 설명 |
| --- | --- |
| `npm install` (in `worker/`) | Install Worker dependencies / Worker 의존성 설치 |
| `npx wrangler dev` | Local Worker dev server / 로컬 Worker 개발 서버 |
| `npx wrangler deploy` | Deploy to Cloudflare / Cloudflare에 배포 |

---

## Python Pipeline / 파이썬 파이프라인

### `scraper.py`

Fetches each URL in `SCRAPE_SOURCES` using `httpx`, parses HTML with BeautifulSoup, extracts promo code tokens (typically uppercase alphanumerics), and writes them to `store.py` with state `seen`. Each successful parse updates a per-source `last_checked` timestamp so unchanged pages can be skipped.

`SCRAPE_SOURCES`의 각 URL을 `httpx`로 가져온 뒤 BeautifulSoup으로 파싱하여 프로모 코드 토큰을 추출하고 `store.py`에 `seen` 상태로 기록합니다.

### `redeemer.py`

Reads `seen` codes from `store.py`, authenticates with `auth.py`, and POSTs each code to the official game HTTP endpoint. Success transitions the code to `redeemed`; permanent failures (already used, expired) transition to `failed` or `expired`. Idempotency is enforced by `store.py` so a network drop never causes a double-redeem.

`store.py`에서 `seen` 코드를 읽어 `auth.py`로 인증한 뒤 공식 API에 POST 합니다. 성공 시 `redeemed`, 영구 실패 시 `failed`/`expired`로 전이합니다. 네트워크 단절로 인한 중복 등록은 `store.py`의 멱등성으로 방지됩니다.

### `claim_api.py`

Triggers the daily-reward endpoint for each configured account and records the claim date. Re-running within the same day is a no-op.

각 계정의 일일 보상 엔드포인트를 호출하고 클레임 일자를 기록합니다. 같은 날 재실행하면 no-op입니다.

### `auth.py`

Abstracts the game account session: loads credentials from env, refreshes expired tokens, and exposes a single `get_session()` helper used by `redeemer.py` and `claim_api.py`.

게임 계정 세션을 추상화합니다. 환경 변수에서 자격 증명을 로드하고 만료된 토큰을 갱신한 뒤 `get_session()` 헬퍼를 제공합니다.

### `store.py`

A small JSON-backed key-value store with the following logical schema:

| Key / 키 | Value / 값 |
| --- | --- |
| `codes[code].state` | `seen` \| `redeemed` \| `failed` \| `expired` |
| `codes[code].source` | Source URL / 출처 URL |
| `codes[code].first_seen` | ISO-8601 timestamp / 최초 발견 시각 |
| `accounts[id].last_daily_claim` | ISO-8601 date / 마지막 일일 클레임 날짜 |
| `sources[url].last_checked` | ISO-8601 timestamp / 마지막 확인 시각 |

### `notifier.py`

Dispatches a structured payload on every state transition. The exact channel (`webhook`, `email`, `noop`) is selected by `NOTIFIER_KIND`.

모든 상태 전이에 대해 구조화된 페이로드를 발송합니다. 채널은 `NOTIFIER_KIND`로 선택합니다.

### `main.py`

The orchestrator. A typical run:

1. `scraper.run()` — discover new codes
2. `redeemer.run()` — redeem `seen` codes
3. `claim_api.run()` — daily-reward claim for each account
4. `notifier.flush()` — emit any pending events

각 단계는 독립적이며 순서대로 실행됩니다. 한 단계의 실패가 다음 단계의 실행을 막지 않습니다.

---

## Android Bot / 안드로이드 봇

The bot lives in `idle_outpost_bot/` and is intentionally split from the HTTP pipeline: it can be enabled independently and writes to the same `store.py` schema so the two never double-claim.

봇은 `idle_outpost_bot/`에 있으며 HTTP 파이프라인과 분리되어 있습니다. 동일한 `store.py` 스키마를 공유하므로 두 경로 사이의 중복 클레임을 방지합니다.

| Module / 모듈 | Role / 역할 |
| --- | --- |
| `__main__.py` | CLI entry point / CLI 진입점 |
| `loop.py` | Main tick loop / 메인 루프 |
| `driver.py` | Appium session lifecycle / Appium 세션 관리 |
| `vision.py` | PaddleOCR + template matching / OCR + 템플릿 매칭 |
| `actions.py` | High-level game actions / 상위 게임 액션 |
| `discover.py` | UI element discovery / UI 요소 탐색 |
| `state.py` | Per-account bot state / 계정별 봇 상태 |
| `safety.py` | Cooldowns, anti-ban heuristics, screen-state guards / 쿨다운·안티밴·화면 가드 |
| `settings.py` | Bot configuration / 봇 설정 |
| `config_loader.py` | YAML config loader / YAML 설정 로더 |
| `notify.py` | Bot-side notifications / 봇 알림 |
| `calibrate.py` / `auto_calibrate.py` | Calibration flow / 캘리브레이션 |
| `i18n_ko.properties` | Korean strings / 한국어 문자열 |
| `calibration/*.png` + `*.yaml` | OCR templates + probe screenshots / OCR 템플릿 및 프로브 스크린샷 |

### Calibration / 캘리브레이션

The `calibration/` directory contains per-screen reference screenshots (e.g. `main_screen.png`, `cards.png`, `calendar.png`, `inbox.png`, `quest_board.png`) and corresponding `*.ocr.yaml` / `*.yaml` files describing expected text regions and matching thresholds. Run `--auto-calibrate` on first setup; use `--calibrate` to fix a single screen.

`calibration/`에는 화면별 참조 스크린샷과 OCR 영역/임계값이 정의된 YAML이 함께 들어 있습니다. 최초 설정 시 `--auto-calibrate`를 실행하고, 단일 화면 수정은 `--calibrate`를 사용하세요.

### Bot safety / 봇 안전장치

`safety.py` enforces cooldowns between actions, validates that the current screen matches an expected template before tapping, and pauses the loop if the game shows a dialog, reward popup, or unexpected state. This is intentionally conservative — the bot is a tool, not an autoclicker.

`safety.py`는 액션 간 쿨다운을 강제하고, 탭 전에 현재 화면이 기대된 템플릿과 일치하는지 검증하며, 다이얼로그/보상 팝업/예상치 못한 상태가 감지되면 루프를 일시 정지합니다. 의도적으로 보수적으로 동작합니다.

---

## Cloudflare Worker

The Worker in `worker/` is a thin cron-friendly trigger: on a schedule it calls a webhook (or queue) that runs `main.py` on a host with credentials. It is designed to be cheap and stateless.

`worker/`의 Worker는 가벼운 크론 트리거입니다. 스케줄에 따라 호스트의 `main.py`를 호출하는 웹훅을 발화합니다.

| File / 파일 | Purpose / 용도 |
| --- | --- |
| `worker/wrangler.jsonc` | Wrangler bindings, cron triggers, environment / Wrangler 설정 |
| `worker/src/index.ts` | `scheduled` handler and HTTP entry point / 스케줄·HTTP 핸들러 |
| `worker/tsconfig.json` | TypeScript config / TypeScript 설정 |
| `worker/package.json` | Dependencies and scripts / 의존성 및 스크립트 |

> Configure the webhook URL and any secrets via `wrangler secret put` before deploying.
>
> 배포 전에 `wrangler secret put`으로 웹훅 URL과 시크릿을 설정하세요.

---

## Local Development / 로컬 개발

### Recommended workflow / 권장 워크플로

1. Create a virtual environment with `uv venv` and install dependencies with `uv sync --extra bot`.
2. Copy `.env.example` to `.env` (if present) and fill in real values, or create `.env` manually using the table above.
3. Run `uv run python main.py` once with `REDEEM_DRY_RUN=1` to verify scraping and storage without hitting the live API.
4. Set `REDEEM_DRY_RUN=0` and run again to perform real redemptions.
5. For the bot: start Appium (`appium`), attach a device or emulator, then `uv run python -m idle_outpost_bot`.

### Code style / 코드 스타일

| Tool / 도구 | Purpose / 용도 |
| --- | --- |
| Ruff | Linting + formatting (line length 100, target py311) / 린트 + 포맷 |
| basedpyright | Static type checking / 정적 타입 검사 |

```bash
uv run ruff check .
uv run ruff format .
uv run basedpyright
```

---

## Testing / 테스트

The repository does not ship with a dedicated test suite. The pipeline is designed to be verifiable end-to-end via dry-run:

전용 테스트 스위트는 포함되어 있지 않습니다. 파이프라인은 dry-run으로 종단 검증을 수행하도록 설계되어 있습니다.

| Check / 검증 | Command / 명령어 | Expected result / 기대 결과 |
| --- | --- | --- |
| Scrape dry-run | `REDEEM_DRY_RUN=1 uv run python scraper.py` | New codes appear in `STORE_PATH` / 새 코드가 저장소에 기록됨 |
| Redeem dry-run | `REDEEM_DRY_RUN=1 uv run python redeemer.py` | All `seen` codes transition to `redeemed` / 모든 `seen` 코드가 `redeemed`로 전이 |
| Daily claim idempotency | Run `uv run python claim_api.py` twice the same day | Second run is a no-op / 두 번째 실행은 no-op |
| Bot screen detection | `uv run python -m idle_outpost_bot --discover` | UI elements listed for the current screen / 현재 화면의 UI 요소 출력 |

When adding new logic, prefer covering it with a small standalone script under `var/` that exercises `store.py` transitions directly.

새 로직을 추가할 때는 `var/` 아래에 `store.py` 전이를 직접 검증하는 작은 스크립트를 두는 것을 권장합니다.

---

## Troubleshooting / 문제 해결

| Symptom / 증상 | Likely cause / 원인 | Fix / 해결 |
| --- | --- | --- |
| `httpx` returns 401/403 from the game API | Expired token / 만료된 토큰 | Re-export `GAME_AUTH_TOKEN` via `auth.py` / `auth.py`로 토큰 재설정 |
| Codes stuck in `seen` | Redeemer not run / 리디머 미실행 | Run `uv run python redeemer.py` / 리디머 실행 |
| Daily claim does nothing | Already claimed today / 오늘 이미 클레임 | Check `accounts[id].last_daily_claim` / 저장소에서 날짜 확인 |
| Bot stuck on a screen | Screen template mismatch / 화면 템플릿 불일치 | Re-run `--auto-calibrate` for that screen / 해당 화면 재캘리브레이션 |
| Appium connection refused | Server not running / 서버 미실행 | Start `appium` and confirm `BOT_APPIUM_URL` / Appium 서버 시작 및 URL 확인 |
| Worker deploy fails | Missing secrets / 시크릿 누락 | `wrangler secret put <NAME>` for each required secret / 필요한 시크릿 설정 |
| PaddleOCR slow / OOM | Wrong device target / 디바이스 타깃 오류 | Use CPU build or pin `paddlepaddle` version / CPU 빌드 사용 또는 버전 고정 |

---

## Contributing / 기여

1. Fork the repository and create a feature branch.
2. Keep changes scoped: prefer extending `store.py` states over ad-hoc files.
3. Run `ruff check`, `ruff format`, and `basedpyright` before opening a PR.
4. If you add a new screen to the bot, include both the reference screenshot and its `*.ocr.yaml` template under `idle_outpost_bot/calibration/`.
5. Do not commit `.env`, `STORE_PATH` contents, or any captured account tokens.

For larger changes, open an issue first to discuss the design. The contribution guide in `CONTRIBUTING.md` is the source of truth for process details.

`store.py`의 상태를 확장하는 방식을 우선하고, 가능한 한 작은 PR 단위로 분리해 주세요.

---

## Disclaimer / 면책

This project automates interactions with a third-party mobile game and its public HTTP endpoints. Using automation against a game's services may violate that game's Terms of Service and could result in account restrictions.

이 프로젝트는 제3자 모바일 게임 및 해당 공개 HTTP 엔드포인트와의 상호작용을 자동화합니다. 게임 서비스에 대한 자동화 사용은 해당 게임의 이용약관을 위반할 수 있으며 계정 제한의 원인이 될 수 있습니다.

You are solely responsible for:

- Compliance with the game's Terms of Service.
- Any consequences of running the bot, the scraper, or the redeemer against live services.
- Securing your own credentials, tokens, and webhook secrets.

The maintainers of this repository do not encourage account abuse and provide this code for educational and personal-use purposes only.

본 저장소의 유지보수자는 계정 남용을 권장하지 않으며, 본 코드는 교육 및 개인 사용 목적만으로 제공됩니다. 게임 이용약관 준수, 자동화 실행으로 발생하는 결과, 그리고 본인의 자격 증명/토큰/웹훅 시크릿 보안에 대한 책임은 전적으로 사용자에게 있습니다.

---

## License / 라이선스

Released under the terms described in [`LICENSE`](./LICENSE). By using this software you agree to those terms.

[`LICENSE`](./LICENSE) 파일에 명시된 조건에 따라 배포됩니다. 본 소프트웨어 사용 시 해당 조건에 동의하는 것으로 간주됩니다.