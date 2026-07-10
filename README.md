# Idle Outpost Codes

[![Python](https://img.shields.io/badge/python-3.11%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()
[![Status](https://img.shields.io/badge/status-experimental-orange)]()

## 한 줄 요약 / One-line Summary

> **KR**: Idle Outpost의 프로모션 코드를 모니터링하고 일일 보상을 자동 수령하며, Android 클라이언트를 OCR 기반으로 자동화하는 도구 모음입니다.
>
> **EN**: A toolkit that monitors Idle Outpost promo codes, automates daily reward claims, and drives the Android client with OCR-based UI automation.

## 빠른 상태 / Status at a Glance

| 항목 | 값 |
| --- | --- |
| Production readiness | Experimental / Personal use |
| Python | 3.11+ |
| Optional extras | `pip install -e .[bot]` (Appium, Selenium, PaddleOCR) |
| Worker runtime | Cloudflare Workers (TypeScript) |
| Localization | `i18n_ko.properties` (Korean) |
| Primary entry | `python main.py`, `python -m idle_outpost_bot` |
| Storage backend | `store.py` (JSON / lightweight DB) |
| Bot OCR | PaddleOCR + template matching |

## 동작 흐름 / High-Level Flow

1. `scraper.py`가 공개된 코드 게시판 / 커뮤니티 피드를 주기적으로 확인합니다.
2. 새 코드가 발견되면 `store.py`의 로컬 저장소에 기록됩니다.
3. `claim_api.py`가 일일 보상 / 광고 보상 엔드포인트를 호출해 토큰을 회수합니다.
4. `redeemer.py`가 저장된 코드를 게임 계정에 등록합니다.
5. `notifier.py`가 텔레그램 등 외부 채널로 알림을 발송합니다.
6. (선택) `idle_outpost_bot/` 패키지가 에뮬레이터 화면을 캡처하고 OCR로 상태를 판별해 위 루프를 자동 수행합니다.
7. (선택) `worker/`의 Cloudflare Worker가 외부에서 조회 가능한 JSON 엔드포인트를 제공합니다.

## 목차 / Table of Contents

- [패키지 구성 / Package Contents](#패키지-구성--package-contents)
- [상태 / Status](#상태--status)
- [먼저 읽을 파일 / First Files to Read](#먼저-읽을-파일--first-files-to-read)
- [진입점 / API or Entry Points](#진입점--api-or-entry-points)
- [빠른 시작 / Quickstart](#빠른-시작--quickstart)
- [명령어 / Commands Reference](#명령어--commands-reference)
- [로컬 개발 / Local Development](#로컬-개발--local-development)
- [테스트 / Testing](#테스트--testing)
- [유지보수 / Maintainers](#유지보수--maintainers)
- [추가 문서 / Further Documentation](#추가-문서--further-documentation)
- [기여 / Contributing](#기여--contributing)
- [라이선스 / License](#라이선스--license)

## 패키지 구성 / Package Contents

### 최상위 모듈 / Top-Level Modules

| 경로 | 역할 |
| --- | --- |
| `main.py` | CLI 진입점. 서브커맨드로 스크레이퍼 / 리디머 / 봇을 묶습니다. |
| `scraper.py` | 공개 코드 소스를 HTTP로 가져와 파싱합니다. |
| `store.py` | 코드와 회수 이력의 로컬 저장소. |
| `claim_api.py` | 일일 보상 / 광고 보상 엔드포인트를 호출합니다. |
| `redeemer.py` | 저장된 코드를 게임 계정에 등록합니다. |
| `notifier.py` | 텔레그램 / 디스코드 등 외부 채널로 푸시합니다. |
| `auth.py` | 세션 토큰 발급 및 갱신. |
| `pyproject.toml` | 의존성과 메타데이터. |
| `uv.lock` | `uv` 패키지 매니저용 잠금 파일. |

### Android 자동화 봇 / `idle_outpost_bot/`

| 경로 | 역할 |
| --- | --- |
| `__main__.py` | `python -m idle_outpost_bot` 진입점. |
| `driver.py` | Appium / uiautomator2 세션 관리. |
| `vision.py` | PaddleOCR과 템플릿 매칭으로 화면 상태를 인식합니다. |
| `loop.py` | 메인 루프: 캡처 → 인식 → 액션 → 안전 검사. |
| `actions.py` | 탭 / 스와이프 / 입력 등 저수준 동작. |
| `safety.py` | 가드레일: 인위적 딜레이, 실패 임계치, 종료 조건. |
| `auto_calibrate.py`, `calibrate.py` | 캘리브레이션 이미지와 OCR yaml을 갱신합니다. |
| `state.py` | FSM(유한 상태 머신) 정의. |
| `discover.py` | UI 요소를 동적으로 탐색합니다. |
| `settings.py` | 사용자 / 디바이스 설정. |
| `config_loader.py` | YAML / JSON 설정 로더. |
| `i18n_ko.properties` | 한국어 UI 문자열. |
| `calibration/` | 화면 상태별 기준 이미지와 OCR 결과 yaml. |

### Cloudflare Worker / `worker/`

| 경로 | 역할 |
| --- | --- |
| `src/index.ts` | 최신 코드 / 공지를 JSON으로 노출하는 Worker 핸들러. |
| `wrangler.jsonc` | Cloudflare Workers 배포 설정. |
| `package.json` | TypeScript 의존성. |

## 상태 / Status

- 본 저장소는 **개인 실험용 / Experimental**입니다.
- 게임 클라이언트 변경 시 `idle_outpost_bot/calibration/`의 기준 이미지가 손상될 수 있습니다.
- 코드 API 엔드포인트는 비공식이며 언제든 변경될 수 있습니다.
- 프로덕션 트래픽을 가정하지 않으며, 안정성 SLA를 제공하지 않습니다.

## 먼저 읽을 파일 / First Files to Read

운영자가 가장 먼저 봐야 할 파일은 다음 순서를 권장합니다.

1. `pyproject.toml` — 의존성과 옵션(`bot`) 확인.
2. `main.py` — CLI 구조와 서브커맨드 이해.
3. `idle_outpost_bot/README.md` — 봇 캘리브레이션 절차.
4. `worker/README.md` — Worker 배포 절차.
5. `idle_outpost_bot/AD_REWARDS.md`, `AUTOMATION_TARGETS.md` — 자동화 대상 화면 분석.

## 진입점 / API or Entry Points

### Python CLI (최상위 진입점)

| 명령 | 진입 모듈 | 용도 |
| --- | --- | --- |
| `python main.py` | `main.py` | CLI 디스패처 |
| `python -m idle_outpost_bot` | `idle_outpost_bot/__main__.py` | Android 자동화 봇 |

각 모듈은 단독 실행이 가능하도록 구성되어 있습니다. 자세한 인자 목록은 각 파일 상단 또는 `python <module>.py --help` 출력을 확인하세요.

### Cloudflare Worker

| 엔드포인트 | 메서드 | 응답 |
| --- | --- | --- |
| `/` | `GET` | 최신 코드 JSON |
| `/healthz` | `GET` | 워커 헬스 체크 |

환경 변수와 시크릿은 `worker/wrangler.jsonc`를 참조하세요.

## 빠른 시작 / Quickstart

### 1. 저장소 클론 / Clone

```bash
git clone <repository-url>
cd idle-outpost-codes
```

### 2. Python 환경 / Python Environment

`uv`를 권장합니다. 다른 도구를 써도 무방합니다.

```bash
# 핵심 기능만 설치
uv sync

# 봇까지 사용
uv sync --extra bot
```

### 3. 환경 변수 / Environment Variables

`.env`를 만들어 다음 키를 채워주세요. 값은 모두 플레이스홀더입니다.

```ini
IDLE_OUTPOST_AUTH_TOKEN=<your-session-token>
IDLE_OUTPOST_DEVICE_ID=<your-device-uuid>
TELEGRAM_BOT_TOKEN=<optional-telegram-token>
TELEGRAM_CHAT_ID=<optional-chat-id>
```

### 4. 첫 실행 / First Run

```bash
# 코드 수집
python main.py scrape

# 캐시된 목록 확인
python main.py list

# 일일 보상 회수
python main.py claim
```

### 5. 봇 실행 / Run the Bot (선택)

봇 가이드의 사전 준비(에뮬레이터, Appium 서버)를 마친 뒤:

```bash
python -m idle_outpost_bot
```

## 명령어 / Commands Reference

| 진입점 | 주요 역할 | 참고 모듈 |
| --- | --- | --- |
| `main.py` | CLI 디스패처. 스크레이프 / 리디엠 / 클레임 / 노티파이 호출. | `scraper.py`, `redeemer.py`, `claim_api.py`, `notifier.py` |
| `claim_api.py` | 일일 보상 엔드포인트 호출. | `auth.py` |
| `redeemer.py` | 저장된 코드를 계정에 등록. | `store.py`, `auth.py` |
| `scraper.py` | 외부 코드 게시판에서 신규 코드 수집. | `store.py` |
| `notifier.py` | 외부 채널 알림 발송. | `store.py` |
| `idle_outpost_bot/__main__.py` | Android 자동화 메인 루프. | `driver.py`, `vision.py`, `loop.py` |
| `worker/src/index.ts` | Cloudflare Worker 핸들러. | `wrangler.jsonc` |

## 로컬 개발 / Local Development

- Python 3.11+ 및 `uv` 권장.
- 코드 스타일: Ruff(`line-length = 100`). `ruff check .`, `ruff format .`.
- 타입 검사: basedpyright(`venv = .venv`).
- 봇 작업 시 Android 에뮬레이터와 Appium 서버를 사전에 띄워야 합니다.
- Worker 개발은 `cd worker && npm install && npm run dev`로 로컬에서 시뮬레이션합니다.

## 테스트 / Testing

본 저장소에는 자동화 테스트 프레임워크가 아직 포함되어 있지 않습니다. PR 전 다음을 수동으로 확인하세요.

1. `python main.py scrape --dry-run`이 오류 없이 종료되는지.
2. `python main.py list`가 최근 항목을 보여주는지.
3. 봇의 경우 `idle_outpost_bot/calibration/` 기준 이미지와 현재 에뮬레이터 화면이 일치하는지.

## 유지보수 / Maintainers

- **Repository owner**: 저장소 소유자(GitHub 계정).
- **Issues**: 버그 제보 및 기능 제안은 저장소 Issues 탭을 이용하세요.
- **Security**: 토큰 / 자격 증명은 절대 커밋하지 마세요. 비밀 값은 환경 변수 또는 `.env`로만 주입합니다.

## 추가 문서 / Further Documentation

| 문서 | 위치 | 설명 |
| --- | --- | --- |
| 보상 회수 절차 | `idle_outpost_bot/AD_REWARDS.md` | 광고 보상 자동화 상세. |
| API 리서치 | `idle_outpost_bot/API_RESEARCH.md` | 비공식 API 분석. |
| 자동화 대상 | `idle_outpost_bot/AUTOMATION_TARGETS.md` | 대상 화면 목록. |
| 캘리브레이션 절차 | `idle_outpost_bot/CALIBRATION_FULL.md` | 기준 이미지 갱신 절차. |
| JADX 인벤토리 | `idle_outpost_bot/JADX_FULL_INVENTORY.md` | APK 디컴파일 결과 요약. |
| 봇 패키지 안내 | `idle_outpost_bot/README.md` | 봇 실행 및 캘리브레이션. |
| Worker 가이드 | `worker/README.md` | Cloudflare Worker 배포. |

## 기여 / Contributing

기여 절차는 [`CONTRIBUTING.md`](./CONTRIBUTING.md)를 참조하세요. PR 전 다음을 권장합니다.

- 변경 범위에 해당하는 `idle_outpost_bot/` 캘리브레이션 이미지를 함께 갱신.
- 비밀 값은 `.env.example` 형식으로만 추가하고 실제 값은 커밋 금지.
- `ruff check .` 및 `ruff format .` 통과 확인.

## 라이선스 / License

이 프로젝트는 [`LICENSE`](./LICENSE)에 명시된 조건에 따라 배포됩니다.