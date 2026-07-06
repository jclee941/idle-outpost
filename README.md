# Idle Outpost Codes

![Python](https://img.shields.io/badge/python-3.11%2B-blue) ![uv](https://img.shields.io/badge/deps-uv-purple) [![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE) ![Bot](https://img.shields.io/badge/optional-android%20bot-orange) ![Worker](https://img.shields.io/badge/optional-cloudflare%20worker-orange) ![Status](https://img.shields.io/badge/status-experimental-yellow)

> **프로모 코드 모니터링 · 일일 보상 클레임 · 안드로이드 자동화 (옵션)**
> *Promo code monitor · daily-reward claim CLI · optional Android automation bot*

## 요약 (Summary, 한국어)

`idle-outpost-codes`는 모바일 게임 *Idle Outpost*의 신규 프로모션 코드 모니터링과 일일 보상 자동 클레임을 위한 단일 Python 패키지입니다. 공개 웹에서 코드를 수집하고 게임의 HTTP API로 등록하며, 모든 결과를 단일 영속 레이어(`store.py`)와 단일 알림 어댑터(`notifier.py`)로 흘려보냅니다. 단계가 같은 저장소와 알림 채널을 공유하기 때문에 멱등(idempotent)이고 재시작에 안전합니다.

옵션으로 두 컴포넌트를 추가 운용할 수 있습니다. 안드로이드 디바이스에서 비전 기반 UI 자동화(`idle_outpost_bot/`, Appium + PaddleOCR) 또는 Cloudflare Worker를 통한 엣지 스케줄링(`worker/`, TypeScript)이 가능합니다. 운영자는 단일 진입점 `python main.py`만 기억하면 핵심 파이프라인을 가동할 수 있습니다.

## Overview (English, secondary)

`idle-outpost-codes` is a single Python kit that monitors new promotional codes for the mobile game *Idle Outpost* and claims daily rewards on a schedule. It scrapes public sources, redeems codes through the game's HTTP API, and routes every result through a shared persistence layer (`store.py`) and a shared notifier (`notifier.py`), so each run is idempotent and safe to restart. An optional Android vision bot (Appium + PaddleOCR) and a Cloudflare Worker can be layered on top for on-device UI automation and edge scheduling.

## 상태 / Status

| 항목 / Item | 값 / Value | 비고 / Notes |
|---|---|---|
| 패키지 / Package | `idle-outpost-codes` | [`pyproject.toml`](pyproject.toml) |
| 버전 / Version | `0.1.0` | 사전 배포 / pre-release |
| Python | `>= 3.11` | `requires-python` |
| 의존성 관리 / Dependency manager | `uv` 권장 / recommended | [`uv.lock`](uv.lock) 동봉 |
| 라이선스 / License | MIT | [`LICENSE`](LICENSE) |
| 운영 준비도 / Production readiness | 실험적 / experimental | v0.1.x, API 변경 가능 / API may change |
| 핵심 진입점 / Core entry point | `python main.py` | 단일 명령 / single command |
| 알림 어댑터 / Notifier | `notifier.py` | 단일 채널 / single channel |
| 영속 레이어 / Persistence | `store.py` | 멱등 / idempotent |
| 코드 수집 / Code scraping | `scraper.py` | 공개 소스 / public sources only |
| 코드 등록 / Code redemption | `redeemer.py` | 게임 HTTP API |
| 일일 보상 / Daily claim | `claim_api.py` | 게임 HTTP API |
| 인증 / Auth | `auth.py` | 세션 토큰 / session tokens |
| 옵션 컴포넌트 / Optional | 안드로이드 봇, Worker | [`idle_outpost_bot/`](idle_outpost_bot/README.md), [`worker/`](worker/README.md) |

## 동작 흐름 / Run flow

| 단계 / Step | 모듈 / Module | 책임 / Responsibility |
|---|---|---|
| 1. 수집 / Scrape | `scraper.py` | 공개 소스에서 코드 후보 추출 / Extract code candidates |
| 2. 인증 / Auth | `auth.py` | 세션 토큰 발급·갱신 / Issue/refresh session tokens |
| 3. 일일 보상 / Daily claim | `claim_api.py` | 일일 보상 클레임 / Claim daily reward |
| 4. 코드 등록 / Redeem | `redeemer.py` | 신규 코드를 게임 API로 등록 / Redeem via game API |
| 5. 저장 / Persist | `store.py` | 멱등 영속화 (이미 처리된 항목 스킵) / Idempotent persistence |
| 6. 통지 / Notify | `notifier.py` | 단일 알림 어댑터 / Single notifier |
| 7. (옵션) 봇 / Bot (optional) | `idle_outpost_bot/loop.py` | 안드로이드 UI 자동화 / Android UI automation |
| 8. (옵션) 워커 / Worker (optional) | `worker/src/index.ts` | 엣지 스케줄링 / Edge scheduling |

## 운영자 빠른 행동 / Operator's quick action

| 작업 / Task | 명령 / Command |
|---|---|
| 의존성 설치 / Install deps | `uv sync` |
| 핵심 파이프라인 1회 실행 / Run core pipeline once | `python main.py` |
| 안드로이드 봇 추가 의존성 / Install Android bot extras | `uv sync --extra bot` |
| 안드로이드 봇 실행 / Run Android bot | `python -m idle_outpost_bot` |
| Worker 로컬 개발 / Worker local dev | `cd worker && npm install && npx wrangler dev` |
| Worker 배포 / Deploy Worker | `cd worker && npx wrangler deploy` |

## 디렉터리 구조 / Directory layout

```
.
├── auth.py             # Game auth (session token)
├── claim_api.py        # Daily reward HTTP endpoint
├── CONTRIBUTING.md     # Contribution guide
├── idle_outpost_bot/   # Optional Android vision bot (Appium + PaddleOCR)
├── LICENSE             # MIT
├── main.py             # Core pipeline entry point
├── notifier.py         # Single notifier adapter
├── pyproject.toml      # Package metadata & deps
├── README.md
├── redeemer.py         # Promo code redemption
├── scraper.py          # Public-source code scraper
├── store.py            # Idempotent persistence layer
├── uv.lock             # Locked dependency graph
├── video1.png          # Demo screenshot
└──