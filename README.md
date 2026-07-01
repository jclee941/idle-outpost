# Idle Outpost Codes

![Python](https://img.shields.io/badge/python-3.11%2B-blue) ![uv](https://img.shields.io/badge/deps-uv-purple) [![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE) ![Bot](https://img.shields.io/badge/optional-android%20bot-orange) ![Worker](https://img.shields.io/badge/optional-cloudflare%20worker-orange) ![Status](https://img.shields.io/badge/status-experimental-yellow)

> **프로모 코드 모니터링 · 일일 보상 클레임 · 안드로이드 자동화 봇**
> *Promo code monitor · daily-reward claim CLI · Android automation bot*

## 요약 (Summary, 한국어)

`idle-outpost-codes`는 모바일 게임 *Idle Outpost*를 위한 통합 자동화 키트입니다. 핵심 파이프라인은 공개 웹에서 새 프로모션 코드를 주기적으로 수집하고, 게임의 공식 HTTP API로 코드를 등록(Redeem)하며, 일일 보상을 자동으로 클레임합니다. 모든 단계는 단일 영속 레이어(`store.py`)와 단일 발신 알림 모듈(`notifier.py`)을 공유하므로 멱등(idempotent)이고 재시작에 안전합니다.

옵션으로 두 개의 확장 컴포넌트를 함께 운용할 수 있습니다. 안드로이드 디바이스/에뮬레이터에서 비전 기반 UI 봇을 구동하거나(`idle_outpost_bot/`, Appium + PaddleOCR), Cloudflare Worker로 엣지 스케줄링/트리거를 연동하거나(`worker/`, TypeScript)할 수 있습니다. 운영자는 단일 진입점 `python main.py`만 기억하면 됩니다. 봇과 워커는 옵션이므로 가벼운 컨테이너나 로컬 크론만으로도 핵심 파이프라인을 운용할 수 있습니다.

## Overview (English, secondary)

`idle-outpost-codes` is an automation kit for the mobile game *Idle Outpost*. It scrapes public sources for new promotional codes, redeems them through the official HTTP API, and claims daily rewards on a schedule. A single persistence layer and a single outbound notifier are shared by every stage, so runs are idempotent and restart-safe. An optional Android UI bot (Appium + PaddleOCR) and a Cloudflare Worker can be added on top for on-device automation and edge scheduling.

## 상태 / Status

| 항목 / Item | 값 / Value | 비고 / Notes |
|---|---|---|
| 패키지명 / Package name | `idle-outpost-codes` | `pyproject.toml` |
| 버전 / Version | `0.1.0` | 사전 배포 / pre-release |
| Python | `>= 3.11` | `requires-python` |
| 의존성 관리 / Dependency manager | `uv` 권장 | `uv.lock` 동봉 |
| 라이선스 / License | MIT | [`LICENSE`](LICENSE) |
| 운영 준비도 / Production readiness | 실험적 (Experimental) | 핵심 파이프라인 가동 가능, 봇은 캘리브레이션 필요 |
| 봇 백엔드 / Bot backend | Appium + PaddleOCR | `extras: bot` |
| 워커 런타임 / Worker runtime | Cloudflare Workers (TS) | `worker/` |

## 패키지 구성 / Package Contents

| 경로 / Path | 역할 / Role | 비고 / Notes |
|---|---|---|
| `main.py` | 단일 진입점, 단계 조립 | `python main.py` |
| `scraper.py` | 공개 소스에서 코드 수집 | BeautifulSoup4 |
| `auth.py` | 게임 인증 토큰 발급/갱신 | httpx |
| `redeemer.py` | 코드 Redeem 호출 | 멱등 처리 |
| `claim_api.py` | 일일 보상 클레임 | 멱등 처리 |
| `store.py` | 영속 레이어 (SQLite/JSON) | 재시작 안전성 보장 |
| `notifier.py` | 외부 알림 발송 | 단일 채널 |
| `idle_outpost_bot/` | 안드로이드 UI 자동화 (선택) | `extras: bot` |
| `worker/` | Cloudflare Worker 트리거 (선택) | `wrangler` |
| `video1.png` | 데모/문서용 스크린샷 | README 첨부 |

## 먼저 읽을 파일 / First Files to Read

| 순서 / Order | 파일 / File | 이유 / Why |
|---|---|---|
| 1 | `pyproject.toml` | 의존성과 extras 확인 |
| 2 | `main.py` | 전체 파이프라인의 진입점 |
| 3 | `store.py`, `notifier.py` | 멱등성과 알림 동작의 단일 진실 공급원 |
| 4 | `scraper.py`, `redeemer.py`, `claim_api.py` | 각 단계의 비즈니스 로직 |
| 5 | `idle_outpost_bot/README.md` | 봇 운용 시 캘리브레이션 절차 |
| 6 | `worker/README.md` | Cloudflare Worker 배포 절차 |

## API / 엔트리 포인트 / Entry Points

| 엔트리 / Entry | 시그니처 / Signature | 설명 / Description |
|---|---|---|
| CLI | `python main.py` | 수집 → Redeem → 일일 클레임 일괄 실행 |
| 모듈 | `from redeemer import redeem` | 코드 단일 Redeem 호출 |
| 모듈 | `from claim_api import claim_daily` | 일일 보상 클레임 호출 |
| 모듈 | `from scraper import fetch_codes` | 신규 코드 후보 수집 |
| 봇 | `python -m idle_outpost_bot` | 안드로이드 UI 루프 실행 |
| 워커 | `worker/src/index.ts`의 `scheduled` 핸들러 | cron 트리거 핸들러 |

## 아키텍처 / Architecture

핵심 파이프라인은 순방향 단계와 공유 백엔드로 구성됩니다.

| 컴포넌트 / Component | 책임 / Responsibility | 비고 / Notes |
|---|---|---|
| `scraper.py` | 공개 페이지 파싱 → 코드 후보 | BeautifulSoup4 |
| `store.py` | 코드/클레임 상태 영속화 | SQLite 권장 |
| `auth.py` | 게임 토큰 발급/갱신 | httpx |
| `redeemer.py` | 코드 Redeem API 호출 | 멱등: 이미 처리된 코드 스킵 |
| `claim_api.py` | 일일 보상 클레임 | 멱등: 일일 1회 가드 |
| `notifier.py` | 결과/오류 외부 통지 | 단일 모듈 |
| `idle_outpost_bot/` | 디바이스 측 UI 자동화 | 옵션 |
| `worker/` | 엣지 스케줄링 | 옵션 |

### 흐름 / Flow

1. `scraper`가 공개 소스에서 코드 후보를 수집합니다.
2. `store`에 저장된 미처리 코드만 `auth`로 토큰을 받아 `redeemer`에 전달합니다.
3. `redeemer` 결과(성공/실패/만료)를 `store`에 기록하고 `notifier`로 통지합니다.
4. `claim_api`가 일일 보상을 클레임하고 `store`에 일일 가드를 남깁니다.
5. 봇은 위 단계를 보조하며, 워커는 트리거 역할을 담당합니다.

## 빠른 시작 / Quickstart

### 1. 저장소 준비 / Setup

```bash
git clone <repository-url> idle-outpost-codes
cd idle-outpost-codes
uv venv
source .venv/bin/activate
uv pip install -e .
```

### 2. 환경 변수 / Environment

루트에 `.env`를 작성합니다. (예시 키 이름은 실제 사용 값에 맞춰 조정)

```dotenv
# 게임 인증
GAME_USER_ID=...
GAME_AUTH_TOKEN=...

# 알림 (선택)
NOTIFY_WEBHOOK_URL=...

# 스토리지
STORE_PATH=./data/store.sqlite
```

### 3. 파이프라인 실행 / Run pipeline

```bash
python main.py
```

### 4. (선택) 안드로이드 봇 / Optional Android bot

```bash
uv pip install -e ".[bot]"
python -m idle_outpost_bot
```

자세한 캘리브레이션 절차는 [`idle_outpost_bot/README.md`](idle_outpost_bot/README.md) 및 [`idle_outpost_bot/CALIBRATION_FULL.md`](idle_outpost_bot/CALIBRATION_FULL.md)를 참조하세요.

### 5. (선택) Cloudflare Worker / Optional Worker

```bash
cd worker
npm ci
npx wrangler deploy
```

상세 절차는 [`worker/README.md`](worker/README.md)를 참조하세요.

## 설정 / Configuration

| 키 / Key | 필수 / Required | 기본값 / Default | 설명 / Description |
|---|---|---|---|
| `GAME_USER_ID` | 예 / Yes | — | 게임 계정 식별자 |
| `GAME_AUTH_TOKEN` | 예 / Yes | — | 인증 토큰 |
| `STORE_PATH` | 아니오 / No | `./data/store.sqlite` | 영속 파일 경로 |
| `NOTIFY_WEBHOOK_URL` | 아니오 / No | — | 알림 웹훅 |
| `SCRAPER_SOURCES` | 아니오 / No | 내장 기본값 | 추가 수집 소스 (선택) |
| `BOT_DEVICE_UDID` | 봇 전용 | — | Appium 타깃 디바이스 |

`python-dotenv`로 `.env`가 자동 로드됩니다. 키 이름은 운영 환경에 맞춰 `auth.py` / `notifier.py` 정의를 우선하세요.

## 명령어 참고 / Commands Reference

| 명령 / Command | 용도 / Purpose |
|---|---|
| `python main.py` | 전체 파이프라인 1회 실행 |
| `python -m scraper` | 코드 수집만 단독 실행 (지원 시) |
| `python -m redeemer` | 저장된 코드 Redeem만 실행 (지원 시) |
| `python -m claim_api` | 일일 클레임만 실행 (지원 시) |
| `python -m idle_outpost_bot` | 안드로이드 UI 자동화 루프 |
| `python -m idle_outpost_bot.auto_calibrate` | OCR/탭 좌표 캘리브레이션 |
| `cd worker && npx wrangler dev` | 워커 로컬 실행 |
| `cd worker && npx wrangler deploy` | 워커 배포 |
| `uv run ruff check .` | 린트 |
| `uv run basedpyright` | 타입 검사 (선택) |

## 로컬 개발 / Local Development

| 작업 / Task | 절차 / Steps |
|---|---|
| 가상환경 | `uv venv && source .venv/bin/activate` |
| 코어 설치 | `uv pip install -e .` |
| 봇 의존성 포함 | `uv pip install -e ".[bot]"` |
| 테스트 | `uv run pytest` (추가 시) |
| 린트 | `uv run ruff check .` |
| 타입 검사 | `uv run basedpyright` |
| 워커 개발 | `cd worker && npm ci && npx wrangler dev` |

데이터 디렉터리는 일반적으로 `./data/`이며, 영속 파일은 코드 실행 시 자동 생성됩니다. 캐시된 캘리브레이션 자산은 `idle_outpost_bot/calibration/`에 위치합니다.

## 테스트 / Testing

| 영역 / Area | 도구 / Tool | 위치 / Location |
|---|---|---|
| 단위 테스트 | `pytest` (추가 권장) | `tests/` |
| 봇 캘리브레이션 | `auto_calibrate.py` | `idle_outpost_bot/` |
| 워커 로컬 검증 | `wrangler dev` | `worker/` |
| 스크레이퍼 회귀 | 소스별 스냅샷 비교 | `scraper.py` |

캘리브레이션 결과물(이미지·OCR YAML)은 `idle_outpost_bot/calibration/`에 커밋되며, 화면 변경 시 동일 경로로 갱신합니다.

## 기여 / Contribution

기여 절차는 [`CONTRIBUTING.md`](CONTRIBUTING.md)를 참조하세요. 일반적으로 다음을 권장합니다.

1. 이슈로 변경 사항을 먼저 논의합니다.
2. 포크 후 기능 브랜치를 생성합니다.
3. `ruff check`와 `basedpyright`를 통과시킵니다.
4. 캘리브레이션 자산을 변경한 경우 관련 `*.png` / `*.ocr.yaml`을 함께 갱신합니다.
5. PR을 열고 변경 요약과 테스트 결과를 첨부합니다.

## 운영자 / 책임자 / Maintainers & Points of Contact

| 항목 / Item | 값 / Value |
|---|---|
| 유지 조직 / Owning org | 저장소 소유자 (Owners) |
| 이슈 트래커 | 저장소 Issues |
| 보안 연락 / Security contact | 저장소 Owners (비공개 권장) |
| 라이선스 / License | MIT ([`LICENSE`](LICENSE)) |

## 더 자세한 문서 / Further Documentation

| 문서 / Doc | 경로 / Path | 주제 / Topic |
|---|---|---|
| 광고 보상 정리 | [`idle_outpost_bot/AD_REWARDS.md`](idle_outpost_bot/AD_REWARDS.md) | 광고 보상 흐름 |
| API 리서치 | [`idle_outpost_bot/API_RESEARCH.md`](idle_outpost_bot/API_RESEARCH.md) | 게임 API 노트 |
| 자동화 대상 | [`idle_outpost_bot/AUTOMATION_TARGETS.md`](idle_outpost_bot/AUTOMATION_TARGETS.md) | 봇 대상 화면 목록 |
| 전체 캘리브레이션 | [`idle_outpost_bot/CALIBRATION_FULL.md`](idle_outpost_bot/CALIBRATION_FULL.md) | 캘리브레이션 절차 |
| JADX 인벤토리 | [`idle_outpost_bot/JADX_FULL_INVENTORY.md`](idle_outpost_bot/JADX_FULL_INVENTORY.md) | 디컴파일 인벤토리 |
| 봇 README | [`idle_outpost_bot/README.md`](idle_outpost_bot/README.md) | 봇 운영 가이드 |
| 워커 README | [`worker/README.md`](worker/README.md) | 워커 배포 가이드 |

## 도움말 / Getting Help

1. 먼저 본 README의 *상태 / Status* 및 *먼저 읽을 파일*을 확인합니다.
2. 관련 모듈의 README를 읽습니다 (`idle_outpost_bot/`, `worker/`).
3. 저장소 Issues에 재현 절차와 로그를 첨부해 질문을 남깁니다.
4. 보안 이슈는 공개 이슈 대신 Owners에게 비공개로 연락합니다.

---

© 본 프로젝트는 MIT 라이선스로 배포됩니다. 자세한 내용은 [`LICENSE`](LICENSE)를 참조하세요.