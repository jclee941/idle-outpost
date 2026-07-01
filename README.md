# Idle Outpost Codes

> **프로모 코드 모니터링 · 일일 보상 클레임 · 안드로이드 자동화 봇**
> **Promo code monitor · daily-reward claim CLI · Android automation bot**

An integration kit for the mobile game *Idle Outpost*. The repository ships a
Python pipeline that scrapes public sources for new promotional codes, redeems
them through the game's official HTTP API, and claims daily rewards on a
schedule. An optional Android UI bot (Appium + PaddleOCR) drives the game on a
real device or emulator, and a Cloudflare Worker can trigger scheduled work
from the edge.

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
Android UI bot, and an optional Cloudflare Worker. Every stage shares a single
persistence layer (`store.py`) and a single outbound notifier (`notifier.py`),
so each run is idempotent and restart-safe.

이 저장소는 세 개의 파이썬 파이프라인, 안드로이드 UI 봇, 그리고 Cloudflare
Worker로 구성됩니다. 모든 단계는 `store.py`의 영속 레이어와 `notifier.py`의
알림 모듈을 공유하므로 멱등(idempotent)하며 재시작에 안전합니다.

| Component / 구성요소 | Entry point / 진입점            | Runtime / 런타임 | Purpose / 용도                                        |
| -------------------- | ------------------------------- | ---------------- | ----------------------------------------------------- |
| Scraper / 수집기     | `python scraper.py`             | Python 3.11+     | Collects new promo codes from public sources / 코드 수집 |
| Redeemer / 등록기    | `python redeemer.py`            | Python 3.11+    | Redeems collected codes via game HTTP API / API 등록  |
| Claim API / 클레임   | `python claim_api.py`           | Python 3.11+    | Claims daily rewards via game HTTP API / 일일 보상    |
| Orchestrator / 통합  | `python main.py`                | Python 3.11+    | Runs all three pipelines with shared state / 통합 실행 |
| Android Bot / 봇    | `python -m idle_outpost_bot`    | Python 3.11+    | Vision-driven UI automation on device / UI 자동화    |
| Worker / 워커        | `worker/src/index.ts`           | Node / Workers  | Edge cron trigger / 엣지 스케줄 트리거                |

---

## Features / 주요 기능

- **Promo code scraper / 프로모 코드 수집** — Pulls new codes from public
  sources (sites, blogs, social posts) with BeautifulSoup parsing and de-dupe
  against the local store. / 공개 소스에서 새 코드를 수집하고 로컬 저장소와
  중복 비교.
- **HTTP API redeemer / API 코드 등록** — Authenticates against the game's
  HTTP API via `auth.py` and submits codes from the queue. / `auth.py`로 인증
  후 큐의 코드를 등록.
- **Daily claim CLI / 일일 클레임 CLI** — Triggers the in-game daily reward
  endpoint with retry and cooldown handling. / 재시도/쿨다운을 적용해 일일
  보상 엔드포인트 호출.
- **Shared persistence / 공유 영속 레이어** — `store.py` keeps a
  crash-safe JSON/DB state of seen codes, last claim timestamp, and queue. /
  코드·클레임 시각·큐 상태를 안전하게 보존.
- **Notifier integration / 알림 연동** — `notifier.py` posts to the
  configured webhook on success/failure. / 성공/실패 시 설정된 웹훅으로
  발송.
- **Android UI bot / 안드로이드 UI 봇** — Appium driver + PaddleOCR +
  OpenCV templates drives idle loop: calendar, cards, quests, ads. /
  Appium + PaddleOCR + 템플릿 매칭으로 캘린더/카드/퀘스트/광고 자동화.
- **Edge scheduling / 엣지 스케줄링** — Cloudflare Worker can POST to the
  same endpoints the CLI exposes on a cron. / Cloudflare Worker가 동일
  엔드포인트를 cron으로 호출 가능.

---

## Architecture / 아키텍처

The system is intentionally split into small CLI scripts so that each stage
can run on its own cron or be triggered by the Worker. They communicate only
through `store.py` (state) and `notifier.py` (side-effects).

시스템은 각 단계를 독립 cron 또는 Worker에서 호출할 수 있도록 작은 CLI로
분리되어 있으며, `store.py`(상태)와 `notifier.py`(부수 효과)만 공유합니다.

| Layer / 계층           | Module / 모듈                              | Responsibility / 책임                                    |
| ---------------------- | ------------------------------------------ | -------------------------------------------------------- |
| Auth / 인증            | `auth.py`                                  | Login, refresh, token cache / 로그인·토큰 갱신           |
| Scrape / 수집          | `scraper.py`                               | HTML fetch + parse, code normalization / HTML 파싱       |
| Redeem / 등록          | `redeemer.py`                              | POST codes through game API / 코드 등록 요청             |
| Claim / 클레임         | `claim_api.py`                             | Daily-reward HTTP flow / 일일 보상 HTTP 호출             |
| State / 상태           | `store.py`                                 | Codes seen, last claim, retry counters / 영속 상태       |
| Notify / 알림          | `notifier.py`                              | Webhook fan-out / 웹훅 발송                              |
| Orchestrate / 통합     | `main.py`                                  | Pipeline sequencing, exit codes / 파이프라인 조합        |
| UI Bot / UI 봇         | `idle_outpost_bot/loop.py`, `driver.py`    | Appium session, OCR-driven state machine / OCR 상태기계  |
| Edge / 엣지            | `worker/src/index.ts`                      | Scheduled trigger to a reachable host / 호스트 호출      |

Request flow / 요청 흐름:

1. `main.py` (or Worker cron) calls `scraper.run()`.
2. New codes are appended to `store.py` only if not already present.
3. `redeemer.run()` picks queued codes and POSTs via `auth.client`.
4. Successful codes move to a `claimed` set; failures stay queued with a retry count.
5. `claim_api.run()` triggers the daily reward endpoint on its own schedule.
6. `notifier.send()` reports each result to the configured webhook.

---

## Repository Layout / 저장소 구조

```
.
├── main.py                   # Pipeline orchestrator
├── scraper.py                # Promo code scraper
├── redeemer.py               # Code redeemer via game API
├── claim_api.py              # Daily reward claimer
├── auth.py                   # Auth/session helper
├── store.py                  # Persistence layer
├── notifier.py               # Webhook notifier
├── pyproject.toml            # Python project metadata
├── uv.lock                   # Locked dependency graph (uv)
├── LICENSE
├── CONTRIBUTING.md
├── worker/                   # Cloudflare Worker (TypeScript)
│   ├── src/index.ts
│   ├── package.json
│   ├── wrangler.jsonc
│   └── tsconfig.json
└── idle_outpost_bot/         # Android UI automation
    ├── __main__.py
    ├── loop.py
    ├── driver.py
    ├── actions.py
    ├── vision.py
    ├── calibrate.py
    ├── auto_calibrate.py
    ├── discover.py
    ├── settings.py
    ├── state.py
    ├── safety.py
    ├── notify.py
    ├── config_loader.py
    ├── i18n_ko.properties
    └── calibration/          # OCR templates + probe screenshots
```

---

## Quick Start / 빠른 시작

### Prerequisites / 사전 준비물

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or `pip`
- Optional: Android emulator/device with ADB and Appium server for the bot
- Optional: Node 20+ and `wrangler` for the Worker

### 1. Install Python dependencies / 파이썬 의존성 설치

```bash
# Core pipeline only
uv sync

# Include Android bot extras
uv sync --extra bot
```

### 2. Configure environment / 환경 설정

Create a `.env` in the repository root (see [Configuration](#configuration--설정)
for the full list of variables).

```env
GAME_BASE_URL=https://example.invalid
GAME_USERNAME=your_login
GAME_PASSWORD=your_password
NOTIFY_WEBHOOK_URL=https://hooks.example.invalid/notify
STORE_PATH=./.data/state.json
```

### 3. Run the orchestrator / 통합 실행

```bash
python main.py
```

To run stages individually:

```bash
python scraper.py
python redeemer.py
python claim_api.py
```

### 4. (Optional) Deploy the Worker / 워커 배포

```bash
cd worker
npm install
npx wrangler deploy
```

---

## Configuration / 설정

All settings are read from environment variables or a `.env` file via
`python-dotenv`.

| Variable / 변수          | Required / 필수 | Default / 기본값 | Description / 설명                                |
| ------------------------ | --------------- | ---------------- | ------------------------------------------------- |
| `GAME_BASE_URL`          | Yes             | —                | Base URL for the game HTTP API                    |
| `GAME_USERNAME`          | Yes             | —                | Login identifier                                  |
| `GAME_PASSWORD`          | Yes             | —                | Login password / token                            |
| `GAME_DEVICE_ID`         | No              | auto             | Stable device identifier for auth                 |
| `NOTIFY_WEBHOOK_URL`     | No              | —                | Outbound webhook for results                      |
| `NOTIFY_ON_SUCCESS`      | No              | `true`           | Notify on successful redeems                      |
| `NOTIFY_ON_FAILURE`      | No              | `true`           | Notify on failed attempts                         |
| `STORE_PATH`             | No              | `./.data/state.json` | Local persistence file                        |
| `SCRAPER_USER_AGENT`     | No              | library default  | Override HTTP User-Agent for scraping             |
| `SCRAPER_TIMEOUT`        | No              | `15`             | Scrape timeout in seconds                         |
| `REDEEM_MAX_RETRIES`     | No              | `5`              | Retry count per code                              |
| `CLAIM_CRON_HOUR`        | No              | `0`              | Preferred hour (UTC) for daily claim              |
| `BOT_DEVICE_UDID`        | Bot only        | —                | ADB device UDID                                   |
| `BOT_APPIUM_SERVER_URL`  | Bot only        | `http://127.0.0.1:4723` | Appium server endpoint                   |
| `BOT_LOCALE`             | Bot only        | `en`             | UI locale for OCR templates                       |
| `BOT_DRY_RUN`            | Bot only        | `false`          | Run bot loop without tapping                      |

> Note / 참고: `127.0.0.1` is a loopback placeholder; on a real deployment
> point `BOT_APPIUM_SERVER_URL` at the host running Appium. The repo does not
> include private network information.

---

## Commands Reference / 명령어 레퍼런스

### Python CLI / 파이썬 CLI

| Command / 명령어                          | Description / 설명                                  |
| ----------------------------------------- | --------------------------------------------------- |
| `python main.py`                          | Run full pipeline (scrape → redeem → claim)         |
| `python main.py --only scrape`            | Run only the scraper                                |
| `python main.py --only redeem`            | Run only the redeemer                               |
| `python main.py --only claim`             | Run only the daily claimer                          |
| `python main.py --dry-run`                | Skip HTTP writes, only print actions                |
| `python scraper.py --source <name>`       | Restrict scraping to a configured source            |
| `python redeemer.py --code ABCD-1234`     | Redeem a single code instead of the queue          |
| `python claim_api.py --force`             | Claim even if already claimed today                 |
| `python -m idle_outpost_bot`              | Start the Android bot                               |
| `python -m idle_outpost_bot calibrate`    | Open the calibration helper                         |
| `python -m idle_outpost_bot auto-calibrate` | Run automatic OCR template calibration            |

Exit codes / 종료 코드:

| Code / 코드 | Meaning / 의미                          |
| ----------- | --------------------------------------- |
| `0`         | Success / 성공                          |
| `1`         | Generic failure / 일반 오류             |
| `2`         | Auth error / 인증 오류                  |
| `3`         | Network error / 네트워크 오류           |
| `4`         | Partial success (some codes failed) / 부분 성공 |

### Worker / 워커

| Command / 명령어                | Description / 설명                  |
| ------------------------------- | ----------------------------------- |
| `npm run dev`                   | Local `wrangler dev`                |
| `npm run deploy`                | Deploy to Cloudflare                |
| `npm run tail`                  | Tail live logs                      |

---

## Python Pipeline / 파이썬 파이프라인

### `scraper.py`

- Fetches configured source pages with `httpx` and parses code candidates with
  `beautifulsoup4`.
- Normalizes codes (uppercase, strip, dash-insensitive) and writes new entries
  into `store.py`.
- Respects `SCRAPER_USER_AGENT` and `SCRAPER_TIMEOUT`.

### `redeemer.py`

- Reads the queue from `store.py`, calls the game API through `auth.client`,
  and updates each code's status (`pending`, `claimed`, `failed`).
- Honors `REDEEM_MAX_RETRIES` and exponential backoff.
- Emits results to `notifier.send()`.

### `claim_api.py`

- Calls the in-game daily reward endpoint with the cached session.
- Records `last_claim_at` in `store.py` to prevent duplicate runs.
- Supports `--force` to bypass the once-per-day guard.

### `store.py`

- JSON-backed persistence layer with atomic writes.
- Keeps three collections: `seen_codes`, `claim_history`, `retry_counters`.

### `notifier.py`

- Single outbound interface (webhook) with templated payloads.
- Honors `NOTIFY_ON_SUCCESS` / `NOTIFY_ON_FAILURE`.

### `auth.py`

- Manages login, refresh, and short-lived token caching.
- Loads credentials from environment only — never from disk.

### `main.py`

- Sequential orchestrator with `--only` and `--dry-run` flags.
- Returns non-zero on any stage failure when running end-to-end.

---

## Android Bot / 안드로이드 봇

The bot lives in `idle_outpost_bot/` and is a stateful loop driven by
PaddleOCR and template images under `calibration/`.

### Modules / 모듈

| Module / 모듈         | Purpose / 용도                                                |
| --------------------- | ------------------------------------------------------------- |
| `loop.py`             | Top-level idle loop, sleeps between checks                   |
| `driver.py`           | Appium session lifecycle and screenshot capture               |
| `actions.py`          | Tap / swipe / wait primitives with safety wrappers           |
| `vision.py`           | OCR, template matching, screen classification                 |
| `state.py`            | In-memory + persistent state for the bot                      |
| `safety.py`           | Failsafe checks (no input, stuck screen, dialog blocks)       |
| `notify.py`           | Bot-specific notifier for unusual states                      |
| `settings.py`         | Bot-specific settings loader                                  |
| `config_loader.py`    | YAML/JSON config merge                                        |
| `calibrate.py`        | Interactive calibration using saved screenshots              |
| `auto_calibrate.py`   | Headless calibration using pre-gathered probe shots           |
| `discover.py`         | Screen enumeration / element discovery                        |
| `i18n_ko.properties`  | Korean OCR tokens                                             |

### Calibration data / 캘리브레이션 데이터

The `calibration/` directory contains paired YAML OCR definitions and PNG
template images for each known screen state (e.g. `cards.png`,
`quest_board.png`, `closed_check.png`). Each `.ocr.yaml` describes the
expected text and ROI for matching.

### Running the bot / 봇 실행

```bash
# Start an Appium server (locally or remote)
appium --address 127.0.0.1 --port 4723

# Boot an emulator or attach a device via adb
adb devices

# Launch the bot
python -m idle_outpost_bot
```

### Bot operating flags / 봇 운영 플래그

| Flag / 플래그        | Effect / 효과                               |
| -------------------- | ------------------------------------------- |
| `BOT_DRY_RUN=true`   | Capture and classify, but do not tap         |
| `BOT_LOCALE=ko`      | Switch OCR templates to the Korean screens   |
| `BOT_DEVICE_UDID=…`  | Target a specific attached device            |

### Safety / 안전 장치

- `safety.py` enforces a maximum idle duration, aborts on dialog detection,
  and refuses to interact if the foreground app is not the target game.
- All tap coordinates are clamped to the screen bounds.
- `BOT_DRY_RUN` is the recommended mode for first-time calibration.

---

## Cloudflare Worker

The Worker in `worker/` is a thin scheduled trigger that POSTs to a reachable
host running the Python pipeline. It is intentionally minimal.

### `worker/wrangler.jsonc`

Defines the schedule, environment variables, and bindings. After editing,
deploy with:

```bash
cd worker
npx wrangler deploy
```

### `worker/src/index.ts`

Reads `TARGET_URL` from the environment and issues a `POST` request on the
configured cron. Useful when running the Python pipeline on a self-hosted
box behind a firewall or on a home network.

---

## Local Development / 로컬 개발

```bash
# Clone
git clone <your-fork-url>
cd idle-outpost-codes

# Set up Python environment
uv venv
uv sync --extra bot
source .venv/bin/activate

# Run scraper with a sample source
python scraper.py --source example

# Lint and type-check
ruff check .
basedpyright .
```

Pre-commit hooks are not enforced; contributors are expected to run `ruff`
and `basedpyright` locally before opening a pull request.

---

## Testing / 테스트

The repository currently ships example probes under `calibration/` (paired
`.png` + `.ocr.yaml`) that double as lightweight regression fixtures for the
bot's vision pipeline. Validate the OCR definitions with:

```bash
python -m idle_outpost_bot calibrate --check
```

For the HTTP pipeline, `main.py --dry-run` exercises the orchestration logic
without making network writes.

> Contributing a `tests/` directory with `pytest` cases is welcome; see
> [CONTRIBUTING.md](./CONTRIBUTING.md).

---

## Troubleshooting / 문제 해결

| Symptom / 증상                                  | Likely cause / 추정 원인                       | Fix / 해결                                              |
| ----------------------------------------------- | ---------------------------------------------- | ------------------------------------------------------- |
| `auth.py` raises `AuthError`                    | Wrong credentials, expired token               | Re-check `GAME_USERNAME` / `GAME_PASSWORD` and rerun    |
| Scraper returns zero codes                      | Source HTML changed / blocklist                | Update selectors in `scraper.py`                        |
| Redeemer repeatedly fails the same code         | Code already used or region-locked             | Remove from queue; check `NOTIFY_ON_FAILURE`            |
| Bot stops on `stuck_screen`                     | Dialog overlay or update popup                  | Dismiss manually or extend `safety.py`                  |
| Worker trigger returns 5xx                      | Target URL unreachable from Cloudflare edge    | Confirm `TARGET_URL` allows public POST, check WAF rules |
| `paddleocr` import fails                        | Missing `[bot]` extras                         | `uv sync --extra bot`                                   |

---

## Contributing / 기여

See [CONTRIBUTING.md](./CONTRIBUTING.md) for code style, commit message
convention, and pull request process. New calibration screens should ship
both a `.png` and `.ocr.yaml` pair under `idle_outpost_bot/calibration/`.

---

## Disclaimer / 면책

This project is an unofficial, community-driven automation toolkit for
*Idle Outpost*. It interacts only with public web pages and with the game's
official HTTP endpoints; it does not modify the game client. Use is at your
own risk and may be subject to the game's terms of service.

이 프로젝트는 *Idle Outpost* 게임의 비공식 커뮤니티 자동화 키트입니다.
공개 웹페이지와 게임의 공식 HTTP 엔드포인트만 사용하며, 게임 클라이언트를
변조하지 않습니다. 사용으로 인한 책임은 사용자 본인에게 있으며, 게임의
이용약관이 적용될 수 있습니다.

---

## License / 라이선스

Released under the terms described in [LICENSE](./LICENSE).
[EULA](./LICENSE) 파일의 조건에 따라 배포됩니다.