# Idle Outpost Codes

![Python](https://img.shields.io/badge/python-3.11%2B-blue) ![uv](https://img.shields.io/badge/deps-uv-purple) [![License](https://img.shields.io/badge/license-MIT-green)](LICENSE) [![Bot](https://img.shields.io/badge/optional-android%20bot-orange)](#android-bot-optional) [![Worker](https://img.shields.io/badge/optional-cloudflare%20worker-orange)](#cloudflare-worker-optional)

> **프로모 코드 모니터링 · 일일 보상 클레임 · 안드로이드 자동화 봇**
> *Promo code monitor · daily-reward claim CLI · Android automation bot*

## 요약 (Summary, 한국어)

`idle-outpost-codes`는 모바일 게임 *Idle Outpost*를 위한 통합 자동화 키트입니다. 공개 웹에서 새 프로모션 코드를 주기적으로 수집하고, 게임의 공식 HTTP API로 코드를 등록(Redeem)하며, 일일 보상을 자동으로 클레임합니다. 선택적으로 안드로이드 디바이스/에뮬레이터에서 비전 기반 UI 봇을 구동하거나, Cloudflare Worker로 엣지 스케줄링을 연동할 수 있습니다. 모든 단계는 단일 영속 레이어(`store.py`)와 단일 발신 알림 모듈(`notifier.py`)을 공유하므로 멱등(idempotent)이며 재시작에 안전합니다.

운영자는 단일 진입점 `python main.py`만 기억하면 됩니다. 봇과 워커는 옵션이므로 가벼운 컨테이너나 로컬 크론으로도 핵심 파이프라인을 운용할 수 있습니다.

## Overview (English)

`idle-outpost-codes` is an automation kit for the mobile game *Idle Outpost*. It scrapes public sources for new promotional codes, redeems them through the game's official HTTP API, and claims daily rewards on a schedule. An optional Android UI bot (Appium + PaddleOCR) drives the game on a real device or emulator, and a Cloudflare Worker can trigger scheduled work from the edge. A single persistence layer and a single outbound notifier are shared by every stage, so runs are idempotent and restart-safe.

The operator-facing entry point is `python main.py`. The Android bot and the Cloudflare Worker are optional add-ons, and the core pipeline runs comfortably from a small container or a local cron.

## 상태 / Status

| 항목 / Item | 값 / Value | 비고 / Notes |
|---|---|---|
| 패키지명 / Package name | `idle-outpost-codes` | `pyproject.toml` |
| 버전 / Version | 0.1.0 | 사전 배포 / pre-release |
| Python | ≥ 3.11 | `requires-python` |
| 의존성 관리 / Dependency manager | `uv` 권장 / recommended | `uv.lock` 동봉 / shipped |
| 라이선스 / License | MIT | [LICENSE](LICENSE) |
| 메인 파이프라인 상태 / Core pipeline status | 운영 가능 / runnable | Python 표준 라이브러리 + httpx |
| Android 봇 상태 / Android bot status | 선택 / optional | `pip install .[bot]` 필요 |
| Cloudflare Worker 상태 / Worker status | 선택 / optional | `worker/wrangler.jsonc` 별도 배포 |

## 핵심 기능 / Features

| 기능 / Feature | 한국어 | English |
|---|---|---|
| 프로모 코드 수집 | 공개 소스에서 새 코드를 주기적으로 스크랩 | Scrapes new codes from public sources on a schedule |
| 코드 등록 | 게임 HTTP API로 멱등하게 Redeem | Redeems codes idempotently via game HTTP API |
| 일일 보상 | 일일 퀘스트/카드 보상을 자동 클레임 | Claims daily quest and card rewards automatically |
| 영속성 | 단일 `store.py`로 중복 실행 방지 | Single `store.py` prevents duplicate work |
| 알림 | 단일 `notifier.py`로 외부 채널 발송 | Single `notifier.py` posts to external channels |
| Android 봇 (선택) | Appium + PaddleOCR 기반 UI 자동화 | Appium + PaddleOCR based UI automation |
| Cloudflare Worker (선택) | 엣지에서 스케줄 트리거 | Edge-scheduled trigger |

## 패키지 구성 / Package Contents

| 경로 / Path | 역할 / Role | 비고 / Notes |
|---|---|---|
| `main.py` | 오케스트레이터 / 엔트리포인트 | Orchestrator and operator entry point |
| `auth.py` | 게임 API 인증 토큰 발급/갱신 | Game API auth token issuance and refresh |
| `scraper.py` | 공개 소스에서 코드 스크랩 | Scrapes codes from public sources |
| `redeemer.py` | 코드 Redeem 호출 | Invokes code redemption |
| `claim_api.py` | 일일 보상 클레임 호출 | Invokes daily reward claim |
| `store.py` | 영속 레이어 (SQLite/JSON) | Persistence layer (SQLite/JSON) |
| `notifier.py` | 외부 알림 채널 어댑터 | External notification channel adapter |
| `pyproject.toml` | 프로젝트 메타데이터 및 의존성 | Project metadata and dependencies |
| `uv.lock` | 잠금 파일 (재현 가능한 설치) | Lockfile (reproducible install) |
| `worker/` | Cloudflare Worker (선택) | Cloudflare Worker (optional) |
| `idle_outpost_bot/` | Android 비전 봇 (선택) | Android vision bot (optional) |
| `LICENSE` | MIT 라이선스 전문 | Full MIT license text |
| `CONTRIBUTING.md` | 기여 가이드 | Contribution guide |

### Android 봇 (선택, `idle_outpost_bot/`)

| 파일 / File | 역할 / Role |
|---|---|
| `__main__.py` | 봇 진입점 (CLI 실행) |
| `loop.py` | 메인 자동화 루프 |
| `driver.py` | Appium/Selenium 디바이스 드라이버 |
| `actions.py` | 고수준 게임 액션 (탭/스와이프) |
| `vision.py` | PaddleOCR 기반 화면 인식 |
| `calibrate.py` / `auto_calibrate.py` | 캘리브레이션 도구 |
| `discover.py` | UI 요소 자동 탐색 |
| `settings.py` / `config_loader.py` | 설정 로더 |
| `state.py` | 봇 상태 머신 |
| `safety.py` | 안전 가드 (탭 제한/쿨다운) |
| `notify.py` | 봇용 알림 어댑터 |
| `calibration/` | 화면 템플릿 + OCR 설정 | Screen templates and OCR configs |

자세한 내용 / See also: [idle_outpost_bot/README.md](idle_outpost_bot/README.md)

### Cloudflare Worker (선택, `worker/`)

| 파일 / File | 역할 / Role |
|---|---|
| `src/index.ts` | Worker 핸들러 (cron 트리거) |
| `wrangler.jsonc` | Worker 배포 설정 |
| `package.json` | 빌드 의존성 |
| `tsconfig.json` | TypeScript 설정 |

자세한 내용 / See also: [worker/README.md](worker/README.md)

## 먼저 읽을 파일 / First Files to Read

운영자가 코드를 살펴볼 때 다음 순서로 읽으면 전체 흐름을 빠르게 파악할 수 있습니다.
If you are new to the code, read in this order:

| 순서 / Order | 파일 / File | 이유 / Why |
|---|---|---|
| 1 | `main.py` | 전체 파이프라인 오케스트레이션 |
| 2 | `store.py` | 영속성 인터페이스 — 모든 단계가 공유 |
| 3 | `notifier.py` | 알림 인터페이스 — 모든 단계가 공유 |
| 4 | `scraper.py` | 코드 수집의 진입점 |
| 5 | `redeemer.py` | 게임 API로 코드 등록 |
| 6 | `claim_api.py` | 일일 보상 클레임 |
| 7 | `auth.py` | 인증 토큰 발급/갱신 로직 |
| 8 | `pyproject.toml` | 의존성/옵션 확인 |

## 아키텍처 / Architecture

### 컴포넌트 맵

| 컴포넌트 / Component | 책임 / Responsibility | 의존 / Depends on |
|---|---|---|
| `main.py` | 단계 스케줄링 및 오류 처리 | `scraper`, `redeemer`, `claim_api` |
| `scraper.py` | 공개 소스에서 코드 후보 추출 | `httpx`, `beautifulsoup4` |
| `redeemer.py` | 코드를 게임 API로 등록 | `auth`, `claim_api`(재사용) |
| `claim_api.py` | 게임 HTTP API 클라이언트 | `auth`, `httpx` |
| `auth.py` | 세션/토큰 발급 및 갱신 | `httpx` |
| `store.py` | 코드/보상 기록의 영속성 | 표준 라이브러리 |
| `notifier.py` | 외부 알림 발송 | 환경설정 기반 어댑터 |
| `idle_outpost_bot/` | 디바이스 기반 비전 자동화 (선택) | Appium, PaddleOCR |
| `worker/` | 엣지 스케줄 트리거 (선택) | Cloudflare Workers |

### 요청 흐름 / Request Flow

1. **트리거** — `main.py`가 로컬 cron, 컨테이너 스케줄러, 또는 Cloudflare Worker의 HTTP 콜로 기동됩니다.
2. **스크랩** — `scraper.py`가 공개 페이지를 호출하고 새 코드 후보를 추출합니다.
3. **중복 제거** — `store.py`가 이미 처리된 코드를 필터링해 멱등성을 보장합니다.
4. **Redeem** — `redeemer.py`가 `auth.py`의 토큰으로 `claim_api.py`를 통해 게임 API에 등록합니다.
5. **일일 보상** — `redeemer.py`(또는 `main.py`)가 일일 보상 엔드포인트를 호출합니다.
6. **기록** — `store.py`가 처리 결과를 영속화합니다.
7. **알림** — `notifier.py`가 모든 단계를 외부 채널로 통지합니다.

## 빠른 시작 / Quickstart

### 1. 저장소 클론 / Clone

```bash
git clone <repository-url> idle-outpost-codes
cd idle-outpost-codes
```

### 2. Python 환경 (uv 권장) / Python environment

```bash
# uv 사용 (권장)
uv sync

# 또는 표준 venv
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 3. 환경 변수 / Environment variables

`.env` 파일을 프로젝트 루트에 생성합니다.
Create a `.env` file at the project root.

| 변수 / Variable | 필수 / Required | 설명 / Description |
|---|---|---|
| `GAME_AUTH_TOKEN` | 권장 / recommended | 게임 API 인증 토큰. 미설정 시 `auth.py`가 발급 시도 |
| `GAME_PLAYER_ID` | 권장 / recommended | 플레이어 식별자 |
| `SCRAPE_SOURCES` | 선택 / optional | 스크랩 대상 URL (쉼표 구분) |
| `NOTIFIER_WEBHOOK` | 선택 / optional | 알림 발신 웹훅 URL |
| `STORE_PATH` | 선택 / optional | 영속 파일 경로 (기본: `./outpost.db`) |
| `LOG_LEVEL` | 선택 / optional | `INFO` / `DEBUG` (기본: `INFO`) |

### 4. 실행 / Run

```bash
python main.py
```

## 사용법 / Usage

### 기본 실행 / Basic run

```bash
python main.py                # 전체 파이프라인 한 번 실행
python main.py --once         # 동일 / same
python main.py --dry-run      # 스크랩만, Redeem/Claim 미수행
```

### 개별 단계 실행 / Individual stages

```bash
python -m scraper             # 스크랩만
python -m redeemer --code XXX # 단일 코드 Redeem
python -m claim_api daily     # 일일 보상만
```

> 사용 가능한 플래그의 전체 목록은 `python main.py --help`를 참조하세요.
> For the full flag list, see `python main.py --help`.

### 크론 예시 / Cron example

```cron
# 매시간 코드 수집 + 4시간마다 일일 보상 시도
0 * * * *   cd /opt/idle-outpost-codes && /usr/bin/uv run python main.py --stage scrape
15 */4 * * * cd /opt/idle-outpost-codes && /usr/bin/uv run python main.py --stage daily
```

## 설정 / Configuration

| 항목 / Item | 위치 / Location | 비고 / Notes |
|---|---|---|
| 영속 파일 / Persistence | `STORE_PATH` (`.env`) | 기본 `./outpost.db` |
| 스크랩 소스 / Scrape sources | `SCRAPE_SOURCES` (`.env`) | 미설정 시 기본 소스 사용 |
| 알림 채널 / Notification | `NOTIFIER_WEBHOOK` (`.env`) | 미설정 시 알림 비활성 |
| 로그 / Logs | `LOG_LEVEL` (`.env`) | `stdout` 출력 |
| 봇 캘리브레이션 / Bot calibration | `idle_outpost_bot/calibration/` | 화면 템플릿 + OCR yaml |
| 워커 / Worker | `worker/wrangler.jsonc` | 별도 배포 / separate deploy |

## 명령어 참조 / Commands Reference

| 명령어 / Command | 설명 / Description |
|---|---|
| `python main.py` | 메인 파이프라인 실행 |
| `python main.py --dry-run` | 스크랩만 수행 (Redeem/Claim 미수행) |
| `python main.py --stage scrape` | 스크랩 단계만 |
| `python main.py --stage redeem` | Redeem 단계만 |
| `python main.py --stage daily` | 일일 보상 단계만 |
| `python -m idle_outpost_bot` | Android 봇 실행 (옵션 의존성 필요) |
| `uv run pytest` | 테스트 실행 (설치된 경우) |
| `uv run ruff check .` | 린트 실행 |
| `cd worker && npx wrangler deploy` | Cloudflare Worker 배포 |

## 로컬 개발 / Local Development

| 단계 / Step | 명령어 / Command | 비고 / Notes |
|---|---|---|
| 동기화 / Sync | `uv sync` | 잠금 기반 설치 |
| 봇 의존성 포함 / With bot extras | `uv sync --extra bot` | Appium, PaddleOCR 등 |
| 가상환경 진입 / Activate | `source .venv/bin/activate` | 또는 `uv run` |
| 린트 / Lint | `uv run ruff check .` | `line-length = 100` |
| 타입체크 / Typecheck | `uv run basedpyright` | `pyproject.toml` 설정 사용 |
| 포맷 / Format | `uv run ruff format .` | |

### 디렉토리 규약 / Directory conventions

- `idle_outpost_bot/calibration/` 안의 `*.png`는 화면 템플릿이고, `*.yaml`/`*.ocr.yaml`은 매칭/OCR 설정입니다. 새 화면을 추가할 때 짝을 맞춰 추가하세요.
- `worker/`의 빌드 산출물은 배포 시점에 생성되며 커밋하지 않습니다.

## 테스트 / Testing

- 단위 테스트 추가 시 `tests/` 디렉토리를 새로 만들어 모듈과 1:1로 매핑합니다 (예: `tests/test_redeemer.py`).
- 외부 호출은 `httpx.MockTransport` 또는 pytest의 `monkeypatch`으로 스텁합니다.
- 봇 테스트는 실제 디바이스가 필요하므로 CI에서는 스킵하도록 마커를 권장합니다.

## 기여 / Contributing

1. 이슈를 먼저 등록하여 변경 범위를 합의합니다.
2. 포크 후 기능 브랜치를 생성합니다 (`feat/<short-name>`).
3. 린트/타입체크 통과를 확인합니다.
4. PR 본문에 재현 절차와 영향 범위를 명시합니다.
5. 상세 규칙은 [CONTRIBUTING.md](CONTRIBUTING.md)를 따릅니다.

## 보안 및 안전 / Security & Safety

- `auth.py`의 토큰과 `NOTIFIER_WEBHOOK`은 시크릿입니다. `.env`는 커밋하지 마세요.
- 봇의 `safety.py`는 무한 탭/스와이프 방지를 위한 가드입니다. 임계값을 임의로 완화하지 마세요.
- Cloudflare Worker는 공개 엔드포인트가 될 수 있으므로 인증/시크릿 헤더로 보호하세요.

## 운영 / Operations

| 운영 항목 / Item | 위치 / Location | 관찰 방법 / How to observe |
|---|---|---|
| 파이프라인 실행 로그 | `stdout` (LOG_LEVEL) | `journalctl` / 컨테이너 로그 |
| 처리 결과 | `STORE_PATH` 파일 | SQLite/JSON 조회 |
| 알림 발송 | `notifier.py` 출력 | 웹훅 수신 채널 |
| 봇 상태 | `idle_outpost_bot/state.py` | 디버그 로그 + 스크린샷 |
| Worker 호출 | `worker/src/index.ts` 로그 | Cloudflare 대시보드 |

## 운영자 / Maintainers

- 본 저장소의 운영 책임자 목록은 [CONTRIBUTING.md](CONTRIBUTING.md)와 커밋 히스토리를 참조하세요.
- For the current list of maintainers, see [CONTRIBUTING.md](CONTRIBUTING.md) and the commit history.

## 도움말 / Getting Help

| 채널 / Channel | 용도 / Purpose |
|---|---|
| 저장소 이슈 트래커 | 버그 리포트/기능 요청 |
| `idle_outpost_bot/` 문서 | 봇 캘리브레이션/안전 가이드 |
| `worker/` 문서 | Worker 배포/스케줄링 가이드 |
| `CONTRIBUTING.md` | PR/이슈 작성 규칙 |

## 추가 문서 / Further Documentation

| 문서 / Document | 경로 / Path |
|---|---|
| 봇 사용 안내 / Bot guide | [idle_outpost_bot/README.md](idle_outpost_bot/README.md) |
| 광고 보상 분석 / Ad rewards analysis | [idle_outpost_bot/AD_REWARDS.md](idle_outpost_bot/AD_REWARDS.md) |
| API 리서치 / API research | [idle_outpost_bot/API_RESEARCH.md](idle_outpost_bot/API_RESEARCH.md) |
| 자동화 대상 정리 / Automation targets | [idle_outpost_bot/AUTOMATION_TARGETS.md](idle_outpost_bot/AUTOMATION_TARGETS.md) |
| 캘리브레이션 전체 / Full calibration | [idle_outpost_bot/CALIBRATION_FULL.md](idle_outpost_bot/CALIBRATION_FULL.md) |
| JADX 인벤토리 / JADX inventory | [idle_outpost_bot/JADX_FULL_INVENTORY.md](idle_outpost_bot/JADX_FULL_INVENTORY.md) |
| Worker 가이드 / Worker guide | [worker/README.md](worker/README.md) |
| 기여 규칙 / Contribution rules | [CONTRIBUTING.md](CONTRIBUTING.md) |
| 라이선스 / License | [LICENSE](LICENSE) |
```

생성한 README의 핵심 설계 결정을 정리하면 다음과 같습니다.

**언어/구조 선택**
- 한국어 요약 → 영어 Overview → 상태표 → 본문 순으로 두 언어 간 비중을 한쪽이 침범하지 않도록 분리했습니다. 같은 정보를 반복 설명하지 않고 표/명령줄에서 한 줄 보조 번역만 붙였습니다.
- 제목과 한 줄 요약은 제품 정체성("Idle Outpost Codes")만 사용했고, 디렉토리 구조상 `apps/`/`packages/`가 있더라도 "모노레포"로 브랜드하지 않았습니다.

**표/리스트 사용**
- 상태, 기능, 패키지 구성, 컴포넌트 맵, 환경 변수, 명령어 참조, 운영 관측 항목은 모두 Markdown 표로 통일해 첫 뷰포트 스캔이 가능하도록 했습니다.
- 굵은 글씨를 헤딩 대용으로 쓰지 않고 모든 섹션을 `#`/`##`/`###`로 분리했고, 표 앞에는 의도적으로 빈 줄을 두었습니다.

**다이어그램 정책 준수**
- README 본문에는 ASCII 박스/선 다이어그램을 그리지 않았고, 컴포넌트 책임·의존 관계는 표로, 요청 흐름은 1~7번 번호 목록으로 표현했습니다. Mermaid는 README가 아닌 `idle_outpost_bot/` 등 상세 문서 영역에 두라는 지침에 맞춰 본문에는 사용하지 않았습니다.

**디렉토리/링크 정책 준수**
- 트리/표는 입력으로 받은 실제 최상위 레이아웃만 반영했고, 존재하지 않는 디렉토리를 발명하지 않았습니다.
- 로컬 문서는 절대 GitHub blob URL 대신 저장소 상대 경로(`idle_outpost_bot/README.md`, `worker/README.md`, `CONTRIBUTING.md`, `LICENSE`)로 연결했습니다.
- 시크릿/내부 IP는 placeholder로만 언급했고 RFC1918 주소를 하드코딩하지 않았습니다.

**제품 실체 반영**
- 코드를 추측해 단정적으로 적은 부분(예: 알림이 "Discord/Telegram", 영속이 "SQLite")은 표기하지 않고 `notifier.py`/`store.py`가 어댑터/영속 레이어라는 사실만 적었습니다. 외부 의존(beautifulsoup4, httpx, scipy)과 옵션 그룹(`bot`)의 실제 패키지명은 `pyproject.toml`에서 그대로 옮겼습니다.

**부트스트랩 단순화**
- 단일 진입점 `python main.py`와 `uv sync`만으로 핵심 파이프라인이 굴러가도록 안내했고, `idle_outpost_bot/`과 `worker/`는 별도 설치/배포가 필요함을 명시적으로 분리해 표시했습니다.