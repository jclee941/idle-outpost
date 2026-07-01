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
| 운영 준비도 / Production readiness | 실험적 (Experimental) | 핵심 파이프라인 가동, 봇/워커는 옵션 |
| 안드로이드 봇 | 옵션 | `pip install '.[bot]'` / `idle_outpost_bot/` |
| Cloudflare Worker | 옵션 | `worker/` (Wrangler) |

## 컴팩트 흐름 / Compact flow

| 단계 / Stage | 모듈 / Module | 역할 / Role |
|---|---|---|
| 1. Scrape | `scraper.py` | 공개 출처에서 새 코드 수집 |
| 2. Authenticate | `auth.py` | 게임 API 인증 토큰 발급/갱신 |
| 3. Redeem | `redeemer.py` | 코드를 API로 등록 |
| 4. Claim | `claim_api.py` | 일일 보상 자동 클레임 |
| 5. Persist | `store.py` | 코드/상태 영속화 (멱등) |
| 6. Notify | `notifier.py` | 단일 알림 채널 |
| 7. Orchestrate | `main.py` | 위 단계를 한 CLI로 묶음 |
| 8. (옵션) Bot | `idle_outpost_bot/` | 비전 기반 UI 자동화 |
| 9. (옵션) Worker | `worker/src/index.ts` | 엣지 트리거/스케줄 |

요청 흐름 (Request flow, numbered):

1. 운영자가 `python main.py`를 호출한다.
2. `scraper`가 새 코드를 가져와 `store`에 기록한다.
3. `auth`가 토큰을 확보/갱신한다.
4. `redeemer`가 `store`에 없는 코드만 API에 등록한다(멱등).
5. `claim_api`가 일일 보상을 회수한다.
6. 모든 이벤트는 `notifier`로 단일 채널(텔레그램/웹훅 등)에 보고된다.
7. (옵션) 봇은 `worker`의 트리거나 로컬 스케줄러로 시작된다.

## 패키지 구성 / Package Contents

### 루트 (Core pipeline)

| 경로 / Path | 종류 / Kind | 설명 / Description |
|---|---|---|
| `main.py` | 진입점 / Entry | CLI 오케스트레이터 |
| `auth.py` | 모듈 | 게임 API 인증 |
| `scraper.py` | 모듈 | 코드 스크래퍼 |
| `redeemer.py` | 모듈 | 코드 등록 |
| `claim_api.py` | 모듈 | 일일 보상 클레임 |
| `store.py` | 모듈 | 영속 레이어 |
| `notifier.py` | 모듈 | 발신 알림 |
| `pyproject.toml` | 메타 | 프로젝트/의존성 정의 |
| `uv.lock` | 메타 | 잠긴 의존성 그래프 |
| `LICENSE` | 메타 | MIT 라이선스 |
| `CONTRIBUTING.md` | 문서 | 기여 가이드 |
| `video1.png` | 자산 | 데모/스크린샷 |

### 옵션 컴포넌트 (Optional components)

| 경로 / Path | 종류 / Kind | 설명 / Description |
|---|---|---|
| `idle_outpost_bot/` | Python 패키지 | 안드로이드 비전 봇 (Appium + PaddleOCR) |
| `worker/` | TypeScript 패키지 | Cloudflare Worker (`wrangler.jsonc`) |

### `idle_outpost_bot/` 하위

| 경로 / Path | 설명 / Description |
|---|---|
| `__main__.py` | 봇 실행 진입점 (`python -m idle_outpost_bot`) |
| `actions.py`, `loop.py`, `discover.py` | UI 액션 / 루프 / 화면 디스커버리 |
| `driver.py`, `vision.py`, `safety.py` | 디바이스 드라이버, 비전 처리, 안전 가드 |
| `calibrate.py`, `auto_calibrate.py` | 캘리브레이션 도구 |
| `settings.py`, `state.py`, `config_loader.py`, `notify.py` | 설정/상태/로더/알림 |
| `i18n_ko.properties` | 한국어 리소스 |
| `calibration/` | 캘리브레이션 데이터 (`.png`, `.ocr.yaml`) |
| `AD_REWARDS.md` | 광고 보상 자동화 메모 |
| `API_RESEARCH.md` | 게임 API 리서치 결과 |
| `AUTOMATION_TARGETS.md` | 자동화 대상 매트릭스 |
| `CALIBRATION_FULL.md` | 풀 캘리브레이션 가이드 |
| `JADX_FULL_INVENTORY.md` | 디컴파일 인벤토리 |
| `README.md` | 봇 전용 문서 |

### `worker/` 하위

| 경로 / Path | 설명 / Description |
|---|---|
| `src/index.ts` | Worker 핸들러 |
| `wrangler.jsonc` | Cloudflare Wrangler 설정 |
| `tsconfig.json`, `package.json`, `package-lock.json` | TypeScript/Node 메타 |
| `README.md` | Worker 전용 문서 |

## 먼저 읽을 파일 / First Files to Read

| 순서 / Order | 파일 / File | 이유 / Why |
|---|---|---|
| 1 | [`pyproject.toml`](pyproject.toml) | 의존성/옵션/툴 설정 |
| 2 | [`main.py`](main.py) | 오케스트레이터 진입점 |
| 3 | [`store.py`](store.py), [`notifier.py`](notifier.py) | 공유 영속/알림 |
| 4 | [`scraper.py`](scraper.py), [`redeemer.py`](redeemer.py), [`claim_api.py`](claim_api.py) | 핵심 파이프라인 단계 |
| 5 | [`idle_outpost_bot/README.md`](idle_outpost_bot/README.md) | 봇 운영/캘리브레이션 |
| 6 | [`worker/README.md`](worker/README.md) | 엣지 배포 |
| 7 | [`CONTRIBUTING.md`](CONTRIBUTING.md) | 기여 절차 |

## API / 엔트리 포인트 / Entry Points

### Python CLI

- 메인 진입점: `python main.py` (오케스트레이터)
- 봇 진입점(옵션): `python -m idle_outpost_bot`
- 캘리브레이션(옵션): `python -m idle_outpost_bot.calibrate`, `python -m idle_outpost_bot.auto_calibrate`

### 모듈 책임

| 모듈 / Module | 노출 표면 / Surface | 비고 / Notes |
|---|---|---|
| `main` | CLI 진입점 | `argparse`/서브커맨드 |
| `auth` | 토큰 발급/갱신 | 내부 호출 |
| `scraper` | 코드 수집 | `store`에 기록 |
| `redeemer` | 코드 등록 | `store` 기준 멱등 |
| `claim_api` | 일일 보상 클레임 | 멱등 |
| `store` | 영속 인터페이스 | 파일 경로/포맷은 환경 변수로 주입 |
| `notifier` | 단일 발신 함수 | 텔레그램/웹훅 등 채널은 환경 변수 기반 |

### Cloudflare Worker

- 핸들러: [`worker/src/index.ts`](worker/src/index.ts)
- 배포 설정: [`worker/wrangler.jsonc`](worker/wrangler.jsonc)
- 트리거: HTTP 요청 또는 Cron Trigger (Wrangler 설정에 따름)

## 빠른 시작 / Quickstart

전제 조건 / Prerequisites: Python 3.11+, [`uv`](https://docs.astral.sh/uv/), (옵션) Node.js 20+ / Wrangler, (옵션) 안드로이드 디바이스 또는 에뮬레이터.

### 1. 클론 및 설치

```bash
git clone <repository-url> idle-outpost-codes
cd idle-outpost-codes
uv sync
```

핵심 파이프라인만 사용한다면 이 단계로 충분합니다.

### 2. 환경 변수

저장소 루트에 `.env`를 작성합니다 (예시):

```dotenv
# 게임 계정
GAME_USER_ID=replace-me
GAME_AUTH_TOKEN=replace-me

# 알림 채널 (선택, 둘 중 하나 이상 권장)
NOTIFY_TELEGRAM_BOT_TOKEN=replace-me
NOTIFY_TELEGRAM_CHAT_ID=replace-me
NOTIFY_WEBHOOK_URL=

# 영속 레이어 경로 (선택)
STORE_PATH=./data/store.json
```

`python-dotenv`가 자동으로 로드합니다. 실제 키 이름은 `store.py`/`notifier.py`/`auth.py`의 환경 변수 참조를 확인하세요.

### 3. 핵심 파이프라인 실행

```bash
uv run python main.py
```

서브커맨드와 플래그 목록은 다음으로 확인합니다.

```bash
uv run python main.py --help
```

### 4. 안드로이드 봇 (옵션)

```bash
uv sync --extra bot
uv run python -m idle_outpost_bot
```

자세한 캘리브레이션 절차는 [`idle_outpost_bot/README.md`](idle_outpost_bot/README.md) 및 [`idle_outpost_bot/CALIBRATION_FULL.md`](idle_outpost_bot/CALIBRATION_FULL.md)를 참조하세요.

### 5. Cloudflare Worker (옵션)

```bash
cd worker
npm install
npx wrangler dev        # 로컬 개발
npx wrangler deploy     # 배포
```

자세한 사용법은 [`worker/README.md`](worker/README.md)를 참조하세요.

## 설정 / Configuration

| 위치 / Source | 종류 / Kind | 비고 / Notes |
|---|---|---|
| `pyproject.toml` | 프로젝트 메타 | 의존성/툴 설정 |
| `.env` | 비밀/런타임 | `python-dotenv`로 로드 |
| `idle_outpost_bot/calibration/*.yaml` | 캘리브레이션 데이터 | 봇 OCR/매칭 임계값 |
| `worker/wrangler.jsonc` | Worker 설정 | 크론 트리거, 바인딩, 시크릿 |
| `idle_outpost_bot/i18n_ko.properties` | 로컬라이제이션 | 한국어 리소스 |

`[project.optional-dependencies]`의 `bot` 그룹은 무거운 의존성(Appium, Selenium, PaddleOCR, PaddlePaddle 등)을 포함하므로, 코어 파이프라인만 사용할 때는 `uv sync`만으로 충분합니다.

## 명령어 참조 / Commands Reference

| 명령 / Command | 용도 / Purpose |
|---|---|
| `uv run python main.py` | 핵심 파이프라인 1회 실행 |
| `uv run python main.py --help` | CLI 도움말/서브커맨드 확인 |
| `uv run python -m idle_outpost_bot` | 안드로이드 봇 실행 |
| `uv run python -m idle_outpost_bot.calibrate` | 캘리브레이션 도구 |
| `uv run python -m idle_outpost_bot.auto_calibrate` | 자동 캘리브레이션 |
| `uv run ruff check .` | 린트 ([`pyproject.toml`](pyproject.toml) `[tool.ruff]`) |
| `uv run ruff format .` | 포맷터 |
| `uv run basedpyright` | 타입체크 (`[tool.basedpyright]`) |
| `cd worker && npx wrangler dev` | Worker 로컬 개발 |
| `cd worker && npx wrangler deploy` | Worker 배포 |
| `cd worker && npx wrangler tail` | Worker 로그 스트리밍 |

## 로컬 개발 / Local Development

- 의존성 설치: `uv sync` (코어) 또는 `uv sync --extra bot` (봇 포함)
- 코드 스타일: 라인 길이 100, Python 3.11 타깃 (`[tool.ruff]`)
- 사전 커밋 체크: `uv run ruff check .` / `uv run ruff format .` / `uv run basedpyright`
- 새 의존성 추가: `uv add <package>` 또는 옵션 그룹에는 `uv add --optional bot <package>`
- 모듈 단위 실행: `uv run python -m <module>` (예: `idle_outpost_bot`)

## 테스트 / Testing

저장소에는 별도 `tests/` 디렉터리가 포함되어 있지 않습니다. 변경 후 다음을 권장합니다.

| 항목 / Item | 방법 / Method |
|---|---|
| 스모크 | `uv run python main.py --help` |
| 스크래퍼 | 샘플 입력으로 단위 호출 |
| 등록/클레임 | 테스트 계정으로 1회 실행 |
| 봇 | 캘리브레이션 화면(`idle_outpost_bot/calibration/`)을 수동으로 확인 |
| Worker | `wrangler dev`에서 핸들러 호출 검증 |

PR 전 `uv run ruff check .`와 `uv run basedpyright` 통과를 권장합니다.

## 기여 / Contributing

기여 절차는 [`CONTRIBUTING.md`](CONTRIBUTING.md)를 참조하세요. 버그 리포트와 기능 제안은 저장소 이슈 트래커를 이용합니다.

## 운영자 책임 / Operator Notes

| 영역 / Area | 책임 / Responsibility |
|---|---|
| 계정 | 본인의 게임 계정/토큰만 사용 |
| 이용약관 | 게임 이용약관과 해당 지역法令 준수 |
| 알림 | 텔레그램/웹훅 시크릿은 `.env`로 안전하게 관리, 커밋 금지 |
| 봇 | 디바이스 조작은 본인 단말에서만 수행 |
| 데이터 | `STORE_PATH` 백업 정책 수립 |
| 스케줄 | 운영 환경(컨테이너/Cron/Cloudflare)에 맞게 트리거 구성 |

## 운영자/연락처 / Maintainers / Points of Contact

- 저장소 소유자: 저장소 메타데이터([`pyproject.toml`](pyproject.toml), [`LICENSE`](LICENSE)) 참조
- 이슈 트래커: 저장소 이슈 탭
- 내부 문서: `idle_outpost_bot/*.md`, [`worker/README.md`](worker/README.md), [`CONTRIBUTING.md`](CONTRIBUTING.md)

## 더 자세한 문서 / Further Documentation

| 문서 / Document | 경로 / Path | 주제 / Topic |
|---|---|---|
| 핵심 파이프라인 | [`main.py`](main.py), [`store.py`](store.py), [`notifier.py`](notifier.py) | 오케스트레이션/영속/알림 |
| 캘리브레이션 | [`idle_outpost_bot/CALIBRATION_FULL.md`](idle_outpost_bot/CALIBRATION_FULL.md) | 비전 봇 캘리브레이션 |
| API 조사 | [`idle_outpost_bot/API_RESEARCH.md`](idle_outpost_bot/API_RESEARCH.md) | 게임 API 리버스 |
| 광고 보상 | [`idle_outpost_bot/AD_REWARDS.md`](idle_outpost_bot/AD_REWARDS.md) | 광고 리워드 자동화 |
| 자동화 대상 | [`idle_outpost_bot/AUTOMATION_TARGETS.md`](idle_outpost_bot/AUTOMATION_TARGETS.md) | 액션 매트릭스 |
| JADX 인벤토리 | [`idle_outpost_bot/JADX_FULL_INVENTORY.md`](idle_outpost_bot/JADX_FULL_INVENTORY.md) | 디컴파일 결과 |
| 봇 사용법 | [`idle_outpost_bot/README.md`](idle_outpost_bot/README.md) | 봇 운영 |
| Worker | [`worker/README.md`](worker/README.md) | Cloudflare 엣지 |
| 기여 | [`CONTRIBUTING.md`](CONTRIBUTING.md) | 기여 절차 |
| 라이선스 | [`LICENSE`](LICENSE) | MIT 전문 |
| 데모 | `video1.png` | 스크린샷/동영상 |
```

> **Note**: `LICENSE` 파일은 MIT 라이선스임을 뱃지로 표시하고 있습니다. 실제 전문은 [`LICENSE`](LICENSE)에서 확인하세요. `uv.lock`은 재현 가능한 빌드를 위해 커밋되어 있습니다.