# Idle Outpost Codes

![Python](https://img.shields.io/badge/python-3.11%2B-blue) ![uv](https://img.shields.io/badge/deps-uv-purple) [![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE) ![Bot](https://img.shields.io/badge/optional-android%20bot-orange) ![Worker](https://img.shields.io/badge/optional-cloudflare%20worker-orange) ![Status](https://img.shields.io/badge/status-experimental-yellow)

> **프로모 코드 모니터링 · 일일 보상 클레임 · 안드로이드 자동화 (옵션)**
> *Promo code monitor · daily-reward claim CLI · optional Android automation bot*

## 요약 (Summary, 한국어)

`idle-outpost-codes`는 모바일 게임 *Idle Outpost*의 신규 프로모션 코드 모니터링과 일일 보상 자동 클레임을 위한 단일 Python 패키지입니다. 공개 웹에서 코드를 수집하고 게임의 공식 HTTP API로 등록하며, 모든 결과를 단일 영속 레이어(`store.py`)와 단일 알림 어댑터(`notifier.py`)로 흘려보냅니다. 단계가 같은 저장소와 알림 채널을 공유하기 때문에 멱등(idempotent)이고 재시작에 안전합니다.

옵션으로 두 컴포넌트를 추가 운용할 수 있습니다. 안드로이드 디바이스에서 비전 기반 UI 자동화(`idle_outpost_bot/`, Appium + PaddleOCR) 또는 Cloudflare Worker를 통한 엣지 스케줄링(`worker/`, TypeScript)이 가능합니다. 운영자는 단일 진입점 `python main.py`만 기억하면 핵심 파이프라인을 가동할 수 있습니다.

## Overview (English, secondary)

`idle-outpost-codes` is a single Python kit that monitors new promotional codes for the mobile game *Idle Outpost* and claims daily rewards on a schedule. It scrapes public sources, redeems codes through the game's HTTP API, and routes every result through a shared persistence layer (`store.py`) and a shared notifier (`notifier.py`), so each run is idempotent and safe to restart. An optional Android vision bot (Appium + PaddleOCR) and a Cloudflare Worker can be layered on top for on-device UI automation and edge scheduling.

## 상태 / Status

| 항목 / Item | 값 / Value | 비고 / Notes |
|---|---|---|
| 패키지 / Package | `idle-outpost-codes` | [`pyproject.toml`](pyproject.toml) |
| 버전 / Version | `0.1.0` | 사전 배포 / pre-release |
| Python | `>= 3.11` | `requires-python` |
| 의존성 관리 / Dependency manager | `uv` 권장 | [`uv.lock`](uv.lock) 동봉 |
| 라이선스 / License | MIT | [`LICENSE`](LICENSE) |
| 운영 준비도 / Production readiness | 실험적 (Experimental) | 핵심 파이프라인 가동 가능 |
| 코어 CLI 진입점 / Core CLI entry | `python main.py` | 파이프라인 오케스트레이션 |
| 영속 레이어 / Persistence | `store.py` | 단일 모듈, 모든 단계 공유 |
| 알림 어댑터 / Notifier | `notifier.py` | 단일 모듈, 모든 단계 공유 |
| 옵션 / Optional | Android 봇 · Cloudflare Worker | 설치/미설치 모두 운용 가능 |

## 실행 흐름 / Execution Flow

1. `scraper` — 공개 소스에서 신규 프로모션 코드 후보를 수집합니다.
2. `store` — 신규 코드를 영속 저장하여 중복 등록을 차단합니다.
3. `redeemer` — 게임 공식 HTTP API로 코드를 등록(Redeem)합니다.
4. `claim_api` — 일일 보상 엔드포인트를 자동 클레임합니다.
5. `notifier` — 결과를 단일 채널로 발신합니다(신규/성공/실패).
6. *(옵션)* `idle_outpost_bot` — 안드로이드 디바이스에서 비전 기반 UI 자동화.
7. *(옵션)* `worker` — Cloudflare 엣지에서 스케줄링 또는 트리거.

## 목차 / Contents

- [기능 / Features](#기능--features)
- [패키지 구성 / Package Contents](#패키지-구성--package-contents)
- [아키텍처 / Architecture](#아키텍처--architecture)
- [먼저 읽을 파일 / First Files to Read](#먼저-읽을-파일--first-files-to-read)
- [진입점 / Entry Points](#진입점--entry-points)
- [빠른 시작 / Quickstart](#빠른-시작--quickstart)
- [설정 / Configuration](#설정--configuration)
- [명령어 / Commands](#명령어--commands)
- [로컬 개발 / Local Development](#로컬-개발--local-development)
- [테스트 / Testing](#테스트--testing)
- [옵션: 안드로이드 봇 / Optional Android Bot](#옵션-안드로이드-봇--optional-android-bot)
- [옵션: Cloudflare Worker / Optional Cloudflare Worker](#옵션-cloudflare-worker--optional-cloudflare-worker)
- [유지보수 책임자 / Maintainers](#유지보수-책임자--maintainers)
- [추가 문서 / Further Documentation](#추가-문서--further-documentation)
- [기여 / Contributing](#기여--contributing)
- [라이선스 / License](#라이선스--license)

## 기능 / Features

- 공개 웹 소스에서 *Idle Outpost* 프로모션 코드를 주기적으로 수집
- 수집된 코드를 게임의 공식 HTTP API로 자동 등록(Redeem)
- 일일 보상 엔드포인트를 스케줄 기반으로 자동 클레임
- 모든 단계를 단일 영속 레이어와 단일 알림 채널로 라우팅 → 멱등·재시작 안전
- *(옵션)* 안드로이드 디바이스/에뮬레이터에서 비전 기반 UI 자동화 (Appium + PaddleOCR)
- *(옵션)* Cloudflare Worker를 통한 엣지 스케줄링/트리거

## 패키지 구성 / Package Contents

| 경로 / Path | 역할 / Role |
|---|---|
| `main.py` | CLI 진입점, 파이프라인 오케스트레이션 |
| `scraper.py` | 공개 소스에서 프로모션 코드 스크레이핑 |
| `redeemer.py` | 게임 HTTP API로 코드 등록 |
| `claim_api.py` | 일일 보상 클레임 API 호출 |
| `auth.py` | 인증 토큰/세션 처리 |
| `store.py` | 단일 영속 레이어 (코드·상태·히스토리) |
| `notifier.py` | 단일 발신 알림 어댑터 |
| `idle_outpost_bot/` | 옵션 - 안드로이드 비전 봇 (Appium + PaddleOCR) |
| `worker/` | 옵션 - Cloudflare Worker (TypeScript, Wrangler) |
| `pyproject.toml` · `uv.lock` | 패키지 메타데이터 및 의존성 잠금 |
| `LICENSE` · `CONTRIBUTING.md` | 라이선스 및 기여 가이드 |

## 아키텍처 / Architecture

| 단계 / Stage | 모듈 / Module | 산출물 / Output | 멱등성 / Idempotency |
|---|---|---|---|
| 수집 / Scrape | `scraper.py` | 후보 코드 목록 | `store` 키로 중복 차단 |
| 등록 / Redeem | `redeemer.py` | 게임 API 등록 결과 | 코드 단위 1회 |
| 일일 클레임 / Daily claim | `claim_api.py` | 일일 보상 응답 | 날짜+계정 단위 1회 |
| 영속 / Persistence | `store.py` | 코드·상태·히스토리 | 단일 진실 공급원 |
| 알림 / Notifier | `notifier.py` | 외부 채널 발신 | 단일 어댑터 |
| 옵션 봇 / Optional bot | `idle_outpost_bot/` | UI 자동화 동작 | 캘리브레이션 YAML 기준 |
| 옵션 워커 / Optional worker | `worker/` | 엣지 트리거 | Wrangler 스케줄/요청 기준 |

## 먼저 읽을 파일 / First Files to Read

운영자가 코드를 처음 열었다면 다음 순서로 살펴보세요.

1. [`pyproject.toml`](pyproject.toml) — 패키지 메타데이터, 의존성, 툴 설정(ruff, basedpyright).
2. [`main.py`](main.py) — 파이프라인 진입점과 단계 구성 방식.
3. [`store.py`](store.py) — 영속 모델과 중복 방지 키.
4. [`notifier.py`](notifier.py) — 단일 알림 채널 어댑터.
5. [`scraper.py`](scraper.py) · [`redeemer.py`](redeemer.py) · [`claim_api.py`](claim_api.py) — 각 단계의 핵심 로직.
6. [`auth.py`](auth.py) — 인증 토큰 처리.
7. *(옵션)* [`idle_outpost_bot/README.md`](idle_outpost_bot/README.md), [`worker/README.md`](worker/README.md).

## 진입점 / Entry Points

| 표면 / Surface | 진입점 / Entry point | 비고 / Notes |
|---|---|---|
| CLI 파이프라인 / CLI pipeline | `python main.py` | 코어 오케스트레이터 |
| 안드로이드 봇 / Android bot | `python -m idle_outpost_bot` | Appium 서버 필요 |
| 엣지 트리거 / Edge trigger | [`worker/src/index.ts`](worker/src/index.ts) | Wrangler로 배포 |
| 영속 / Persistence | `store.py` 내부 API | 단일 모듈 |
| 알림 / Notifier | `notifier.py` 내부 API | 단일 어댑터 |

## 빠른 시작 / Quickstart

로컬 환경에서 핵심 파이프라인을 가동하는 최소 절차입니다.

1. **의존성 설치 / Install dependencies**
   ```bash
   # uv 설치 (https://github.com/astral-sh/uv) 후:
   uv sync
   ```
2. **환경 변수 파일 준비 / Prepare environment file**
   ```bash
   # auth.py와 notifier.py에서 필요한 키 이름을 확인한 뒤 .env 파일을 작성하세요.
   # Check auth.py and notifier.py for the required key names, then create .env.
   ```
3. **파이프라인 실행 / Run the pipeline**
   ```bash
   python main.py
   ```

## 설정 / Configuration

설정은 `python-dotenv`로 로드되는 환경 변수와 `pyproject.toml`의 의존성 그룹으로 분리합니다.

| 그룹 / Group | 위치 / Location | 용도 / Purpose |
|---|---|---|
| 코어 런타임 / Core runtime | `.env` (`auth.py`, `notifier.py`) | 인증 토큰, 알림 채널(Webhook 등) |
| 스크레이퍼 소스 / Scraper sources | `scraper.py` 또는 설정 모듈 | 코드 수집 대상 URL/셀렉터 |
| 옵션 - 봇 / Optional bot | `idle_outpost_bot/settings.py` | Appium 엔드포인트, OCR 파라미터 |
| 옵션 - 워커 / Optional worker | `worker/wrangler.jsonc` | Cloudflare Workers 환경 변수 |

> 정확한 키 이름은 `auth.py`와 `notifier.py`의 상수 정의, [`idle_outpost_bot/settings.py`](idle_outpost_bot/settings.py), [`worker/wrangler.jsonc`](worker/wrangler.jsonc)를 확인하세요.

## 명령어 / Commands

| 명령어 / Command | 용도 / Purpose |
|---|---|
| `uv sync` | 코어 의존성 설치 |
| `uv sync --extra bot` | 안드로이드 봇 의존성 추가 설치 |
| `python main.py` | 전체 파이프라인 실행 (scrape → redeem → claim) |
| `python main.py --stage scrape` | 스크레이핑 단계만 실행 |
| `python main.py --stage redeem` | 코드 등록 단계만 실행 |
| `python main.py --stage claim` | 일일 보상 단계만 실행 |
| `python -m idle_outpost_bot` | 안드로이드 비전 봇 실행 |
| `uv run ruff check .` | 린트 실행 |
| `uv run basedpyright` | 타입 체크 |
| `cd worker && npm install` | Worker 의존성 설치 |
| `npx wrangler dev --config worker/wrangler.jsonc` | Worker 로컬 개발 서버 |

## 로컬 개발 / Local Development

- **Python 패키지 매니저** — `uv` 사용을 권장합니다(`uv.lock` 동봉).
- **린트** — `ruff`, 라인 길이 100, 타깃 Python 3.11 ([`pyproject.toml`](pyproject.toml)).
- **타입 체크** — `basedpyright`, 가상환경은 `.venv`.
- **봇 개발** — [`idle_outpost_bot/calibration/`](idle_outpost_bot/calibration)의 OCR YAML과 스크린샷을 함께 수정합니다. 자세한 절차는 [`idle_outpost_bot/CALIBRATION_FULL.md`](idle_outpost_bot/CALIBRATION_FULL.md) 참조.
- **워커 개발** — `worker/`는 `npm install` 후 `wrangler dev`로 로컬 검증합니다.

## 테스트 / Testing

현재 저장소에는 자동화된 테스트 프레임워크가 명시적으로 포함되어 있지 않습니다. 변경 전에는 다음을 권장합니다.

- `uv run ruff check .` 통과
- `uv run basedpyright` 통과
- 드라이런이 가능한 경우 `python main.py --stage scrape` 1회 실행해 신규 코드 후보만 수집하고 정상 종료 확인

## 옵션: 안드로이드 봇 / Optional Android Bot

`idle_outpost_bot/`은 *Idle Outpost* 클라이언트 UI를 디바이스/에뮬레이터에서 자동으로 조작하는 비전 기반 봇입니다. Appium으로 디바이스에 연결하고 PaddleOCR로 화면을 인식한 뒤, YAML 캘리브레이션(`calibration/*.ocr.yaml`)과 매칭하여 동작합니다.

- 진입점: `python -m idle_outpost_bot`
- 의존성 그룹: `uv sync --extra bot` (Appium, Selenium, PaddleOCR, Pillow, NumPy, PyYAML)
- 캘리브레이션 자산: [`idle_outpost_bot/calibration/`](idle_outpost_bot/calibration)
- 운영 가이드: [`idle_outpost_bot/README.md`](idle_outpost_bot/README.md)
- 리서치 노트: [`idle_outpost_bot/API_RESEARCH.md`](idle_outpost_bot/API_RESEARCH.md), [`idle_outpost_bot/AUTOMATION_TARGETS.md`](idle_outpost_bot/AUTOMATION_TARGETS.md), [`idle_outpost_bot/JADX_FULL_INVENTORY.md`](idle_outpost_bot/JADX_FULL_INVENTORY.md), [`idle_outpost_bot/AD_REWARDS.md`](idle_outpost_bot/AD_REWARDS.md)

## 옵션: Cloudflare Worker / Optional Cloudflare Worker

`worker/`는 Cloudflare Workers에서 동작하는 TypeScript 핸들러입니다. 엣지에서 스케줄 트리거 또는 외부 호출을 받아 코어 파이프라인을 깨우는 용도로 사용할 수 있습니다.

- 소스: [`worker/src/index.ts`](worker/src/index.ts)
- 설정: [`worker/wrangler.jsonc`](worker/wrangler.jsonc)
- 가이드: [`worker/README.md`](worker/README.md)
- 로컬 실행: `cd worker && npm install` 후 `npx wrangler dev --config wrangler.jsonc`

## 유지보수 책임자 / Maintainers

이 저장소의 유지보수 책임자는 저장소 소유자(Repository owner)입니다. 운영 중 일반 이슈는 저장소 이슈 트래커를 이용하고, 보안 관련 사항은 공개 이슈 대신 비공개 채널로 연락하세요. 실제 담당자/연락처 정보는 운영 환경에 맞추어 저장소 관리자가 갱신합니다.

## 추가 문서 / Further Documentation

- 코어 패키지 — 이 README가 1차 문서입니다.
- 안드로이드 봇 — [`idle_outpost_bot/README.md`](idle_outpost_bot/README.md) 및 동 폴더의 리서치/캘리브레이션 문서.
- Cloudflare Worker — [`worker/README.md`](worker/README.md).
- 기여 절차 — [`CONTRIBUTING.md`](CONTRIBUTING.md).

## 기여 / Contributing

기여 절차와 PR 규약은 [`CONTRIBUTING.md`](CONTRIBUTING.md)를 따릅니다. 봇 캘리브레이션이나 스크레이퍼 소스를 변경할 때는 관련 문서([`idle_outpost_bot/CALIBRATION_FULL.md`](idle_outpost_bot/CALIBRATION_FULL.md), [`idle_outpost_bot/AUTOMATION_TARGETS.md`](idle_outpost_bot/AUTOMATION_TARGETS.md))도 함께 갱신해 주세요.

## 라이선스 / License

이 프로젝트는 [MIT License](LICENSE) 하에 배포됩니다.