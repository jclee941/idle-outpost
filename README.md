# Idle Outpost Codes

![Python](https://img.shields.io/badge/python-3.11%2B-blue) ![uv](https://img.shields.io/badge/deps-uv-purple) [![License](https://img.shields.io/badge/license-MIT-green)](LICENSE) [![Bot](https://img.shields.io/badge/optional-android%20bot-orange)](#android-bot--안드로이드-봇) [![Worker](https://img.shields.io/badge/optional-cloudflare%20worker-orange)](#cloudflare-worker)

> **프로모 코드 모니터링 · 일일 보상 클레임 · 안드로이드 자동화 봇**
> *Promo code monitor · daily-reward claim CLI · Android automation bot*

## 요약 (Summary)

`idle-outpost-codes`는 모바일 게임 *Idle Outpost*를 위한 통합 자동화 키트입니다. 공개 웹에서 새 프로모션 코드를 주기적으로 수집하고, 게임의 공식 HTTP API로 코드를 등록(Redeem)하며, 일일 보상을 자동으로 클레임합니다. 선택적으로 안드로이드 디바이스/에뮬레이터에서 비전 기반 UI 봇을 구동하거나, Cloudflare Worker로 엣지 스케줄링을 연동할 수 있습니다. 모든 단계는 단일 영속 레이어와 알림 모듈을 공유하므로 멱등(idempotent)하며 재시작에 안전합니다.

## Overview (English)

`idle-outpost-codes` is an integration kit for the mobile game *Idle Outpost*. It scrapes public sources for new promotional codes, redeems them through the game's official HTTP API, and claims daily rewards on a schedule. An optional Android UI bot (Appium + PaddleOCR) drives the game on a real device or emulator, and a Cloudflare Worker can trigger scheduled work from the edge. A single persistence layer and a single outbound notifier are shared by every stage so runs are idempotent and restart-safe.

## 상태 / Status

| 항목 / Item | 값 / Value | 비고 / Notes |
|---|---|---|
| 패키지명 / Package name | `idle-outpost-codes` | `pyproject.toml` |
| 버전 / Version | 0.1.0 | 사전 배포(pre-release) |
| Python / Python | ≥ 3.11 | `requires-python` |
| 의존성 관리 / Deps | `uv` 권장 | `uv.lock` 동봉 |
| 라이선스 / License | MIT | [LICENSE](LICENSE) |
| 메인 파이프라인 / Main pipeline | Active | `python main.py` |
| Android 봇 / Android bot | Optional | `[bot]` extra |
| Cloudflare Worker | Optional | `worker/wrangler.jsonc` |
| 테스트 스위트 / Test suite | 없음 / None | 수동 검증 권장 |

## 한눈에 보는 흐름 / Flow at a Glance

운영자가 가장 자주 호출하는 진입점은 `python main.py`이며, 보조 진입점은 `python -m idle_outpost_bot`과 `worker/`의 `wrangler deploy`입니다.

| # | 단계 / Stage | 모듈 / Module | 담당 / Owner | 다음 명령 / Next command |
|---|---|---|---|---|
| 1 | 스크랩 / Scrape | `scraper.py` | 파이프라인 | 후보 코드를 `store.py`에 기록 |
| 2 | 인증 / Authenticate | `auth.py` | 파이프라인 | 세션 토큰 발급/갱신 |
| 3 | 등록 / Redeem | `redeemer.py` | 파이프라인 | 신규 코드를 게임 API로 등록 |
| 4 | 클레임 / Claim | `claim_api.py` | 파이프라인 | 일일 보상 호출 |
| 5 | 알림 / Notify | `notifier.py` | 파이프라인 | 외부 채널로 결과 통보 |
| 6 | 영속화 / Persist | `store.py` | 파이프라인 | 처리 상태 저장 (멱등 보장) |
| 7 | UI 봇 / UI bot | `idle_outpost_bot/` | 봇 패키지 | `python -m idle_outpost_bot` |
| 8 | 엣지 트리거 / Edge trigger | `worker/src/index.ts` | Worker | Cron Trigger |

## 먼저 읽을 파일 / First Files to Read

| 우선순위 / Priority | 경로 / Path | 이유 / Why |
|---|---|---|
| 1 | [main.py](main.py) | 파이프라인 오케스트레이션 진입점 |
| 2 | [pyproject.toml](pyproject.toml) | 의존성과 `[bot]` extra 정의 |
| 3 | [store.py](store.py) | 모든 단계가 공유하는 영속 레이어 |
| 4 | [notifier.py](notifier.py) | 알림 채널 통합 지점 |
| 5 | [scraper.py](scraper.py) | 데이터 소스 구조 |
| 6 | [redeemer.py](redeemer.py) | 게임 API 호출 방식 |
| 7 | [claim_api.py](claim_api.py) | 일일 보상 클레임 |
| 8 | [auth.py](auth.py) | 세션 발급/갱신 |
| 9 | [idle_outpost_bot/README.md](idle_outpost_bot/README.md) | 봇 운영 가이드 |
| 10 | [worker/README.md](worker/README.md) | Worker 배포 가이드 |
| 11 | [CONTRIBUTING.md](CONTRIBUTING.md) | 기여 절차 |

## API / 진입점 / Entry Points

| 진입점 / Entry | 호출 / Call | 용도 / Purpose |
|---|---|---|
| 파이프라인 / Pipeline | `python main.py` | 스크랩 → 등록 → 클레임 1회 실행 |
| 봇 메인 / Bot main | `python -m idle_outpost_bot` | 디바이스/에뮬레이터에서 게임 구동 |
| 캘리브레이션 / Calibration | `python -m idle_outpost_bot.calibrate` | OCR 기준점 수동 보정 |
| 자동 캘리브레이션 / Auto calibration | `python -m idle_outpost_bot.auto_calibrate` | 캘리브레이션 자동 갱신 |
| 디스커버리 / Discovery | `python -m idle_outpost_bot.discover` | UI 요소 자동 탐색 |
| Worker 배포 / Worker deploy | `cd worker && wrangler deploy` | Cloudflare Edge 배포 |
| Worker 트리거 / Worker trigger | Cron Trigger | 주기적 파이프라인 호출 |

## 빠른 시작 / Quick Start

### 1. 클론 / Clone

```bash
git clone <repo-url> idle-outpost-codes
cd idle-outpost-codes
```

### 2. 환경 변수 작성 / Environment

루트에 `.env`를 작성합니다 (값은 사용자 환경에 맞게 교체):

```ini
# 게임 계정 자격증명 (auth.py / claim_api.py에서 사용)
GAME_PLAYER_ID=<your-player-id>
GAME_AUTH_TOKEN=<your-auth-token>

# 알림 채널 (선택, notifier.py)
NOTIFY_WEBHOOK_URL=<your-webhook-url>

# 스크래퍼 동작 (선택)
SCRAPER_USER_AGENT=idle-outpost-codes/0.1
SCRAPER_TIMEOUT_SEC=30
```

### 3. 의존성 설치 / Install

`uv` 권장:

```bash
uv sync                # 파이프라인만
uv sync --extra bot    # Android 봇까지
```

표준 venv로도 설치 가능합니다:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[bot]"   # 봇 포함 시
```

### 4. 파이프라인 1회 실행 / Run Pipeline

```bash
python main.py
```

### 5. (선택) Android 봇 실행 / Optional Bot

Appium 서버, ADB 디바이스 또는 에뮬레이터를 준비한 뒤:

```bash
python -m idle_outpost_bot
```

캘리브레이션 절차와 디바이스 요구사항은 [idle_outpost_bot/README.md](idle_outpost_bot/README.md)를 참조하세요.

## 설정 / Configuration

| 파일 / File | 용도 / Purpose |
|---|---|
| `.env` | 게임 자격증명, 알림 채널, 스크래퍼 옵션 |
| [pyproject.toml](pyproject.toml) | 의존성, `ruff`, `basedpyright` 설정 |
| `idle_outpost_bot/settings.py` | 봇 동작 파라미터 |
| `idle_outpost_bot/config_loader.py` | YAML/ENV 통합 로더 |
| `idle_outpost_bot/calibration/*.yaml` | 화면별 OCR 기준 좌표 |
| `idle_outpost_bot/calibration/*.png` | 기준 화면 스크린샷 |
| `idle_outpost_bot/i18n_ko.properties` | 한국어 UI 문자열 |
| [worker/wrangler.jsonc](worker/wrangler.jsonc) | Worker 배포/트리거 설정 |
| [worker/package.json](worker/package.json) | Worker 의존성 |

## 명령어 레퍼런스 / Commands Reference

| 명령어 / Command | 설명 / Description |
|---|---|
| `python main.py` | 전체 파이프라인 1회 실행 |
| `python -m idle_outpost_bot` | 봇 메인 루프 시작 |
| `python -m idle_outpost_bot.calibrate` | 캘리브레이션 도구 |
| `python -m idle_outpost_bot.auto_calibrate` | 자동 캘리브레이션 |
| `python -m idle_outpost_bot.discover` | UI 요소 자동 디스커버리 |
| `uv sync` | 의존성 동기화 |
| `uv sync --extra bot` | 봇 의존성 포함 동기화 |
| `ruff check .` | 린트 (`pyproject.toml` 기준) |
| `basedpyright` | 타입 검사 (선택) |
| `cd worker && wrangler deploy` | Cloudflare Worker 배포 |
| `cd worker && wrangler dev` | Worker 로컬 실행 |

## 파이썬 파이프라인 / Python Pipeline

| 모듈 / Module | 역할 / Role |
|---|---|
| [main.py](main.py) | 스크랩 → 등록 → 클레임 순서로 오케스트레이션 |
| [scraper.py](scraper.py) | 공개 웹 소스에서 코드 후보 추출 (`beautifulsoup4`, `httpx`) |
| [auth.py](auth.py) | 게임 계정 세션 발급/갱신 |
| [redeemer.py](redeemer.py) | 신규 코드를 게임 API로 등록 |
| [claim_api.py](claim_api.py) | 일일 보상 클레임 호출 |
| [store.py](store.py) | 처리 상태 영속화, 멱등성 보장 |
| [notifier.py](notifier.py) | 결과를 외부 채널(웹훅 등)로 통보 |

각 단계는 `store.py`의 상태를 갱신하므로, 네트워크 또는 디바이스 오류로 실패한 단계는 다음 실행에서 재시도됩니다.

## Android 봇 / Android Bot

`idle_outpost_bot/`은 Appium-Python-Client와 PaddleOCR로 게임 UI를 인식하고 조작합니다.

| 구성요소 / Component | 파일 / File | 역할 / Role |
|---|---|---|
| 진입점 / Entry | `__main__.py` | 봇 메인 루프 시작 |
| 패키지 메타 / Package meta | `__init__.py` | 패키지 노출 표면 |
| 디바이스 드라이버 / Driver | `driver.py` | Appium 세션 관리 |
| 액션 / Actions | `actions.py` | 탭, 스와이프, 입력 등 UI 동작 |
| 비전 / Vision | `vision.py` | PaddleOCR 기반 화면 인식 |
| 루프 / Loop | `loop.py` | 메인 작업 루프 |
| 상태 / State | `state.py` | 봇 내부 상태 머신 |
| 안전 / Safety | `safety.py` | 디바이스 안전 가드 |
| 알림 / Notify | `notify.py` | 봇 이벤트 알림 |
| 설정 / Settings | `settings.py` | 동작 파라미터 |
| 설정 로더 / Config loader | `config_loader.py` | YAML/ENV 통합 |
| 디스커버리 / Discovery | `discover.py` | 화면 요소 자동 탐색 |
| 보정 / Calibration | `calibrate.py`, `auto_calibrate.py` | OCR 기준점 갱신 |
| 다국어 / Localization | `i18n_ko.properties` | 한국어 UI 문자열 |
| 캘리브레이션 데이터 / Calibration data | `calibration/*.png`, `*.yaml`, `*.ocr.yaml` | 화면/OCR 기준점 |

캘리브레이션 절차, 디바이스 요구사항, 안전 정책은 [idle_outpost_bot/README.md](idle_outpost_bot/README.md)와 다음 문서를 참조하세요:

- [idle_outpost_bot/AD_REWARDS.md](idle_outpost_bot/AD_REWARDS.md)
- [idle_outpost_bot/API_RESEARCH.md](idle_outpost_bot/API_RESEARCH.md)
- [idle_outpost_bot/AUTOMATION_TARGETS.md](idle_outpost_bot/AUTOMATION_TARGETS.md)
- [idle_outpost_bot/CALIBRATION_FULL.md](idle_outpost_bot/CALIBRATION_FULL.md)
- [idle_outpost_bot/JADX_FULL_INVENTORY.md](idle_outpost_bot/JADX_FULL_INVENTORY.md)

## Cloudflare Worker

`worker/`는 파이썬 파이프라인을 주기적으로 트리거하기 위한 Cloudflare Worker입니다.

| 항목 / Item | 경로 / Path |
|---|---|
| 엔트리 소스 / Entry source | [worker/src/index.ts](worker/src/index.ts) |
| 배포 설정 / Deploy config | [worker/wrangler.jsonc](worker/wrangler.jsonc) |
| 빌드 설정 / Build config | [worker/tsconfig.json](worker/tsconfig.json) |
| 의존성 / Dependencies | [worker/package.json](worker/package.json), [worker/package-lock.json](worker/package-lock.json) |
| 배포 명령 / Deploy command | `cd worker && wrangler deploy` |
| 로컬 실행 / Local run | `cd worker && wrangler dev` |
| 트리거 / Trigger | Cron Trigger (예: 1시간 주기) |

자세한 환경 변수와 스케줄은 [worker/README.md](worker/README.md)를 참조하세요.

## 저장소 구조 / Repository Layout

```
.
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── auth.py                  # 세션 발급/갱신
├── claim_api.py             # 일일 보상 클레임
├── main.py                  # 파이프라인 오케스트레이터
├── notifier.py              # 외부 알림 통합
├── pyproject.toml           # 의존성/도구 설정
├── redeemer.py              # 코드 등록
├── scraper.py               # 웹 스크래퍼
├── store.py                 # 영속 레이어
├── uv.lock
├── video1.png               # 데모/스크린샷
├── worker/                  # Cloudflare Worker
│   ├── README.md
│   ├── package.json
│   ├── package-lock.json
│   ├── tsconfig.json
│   ├── wrangler.jsonc
│   └── src/
│       └── index.ts
└── idle_outpost_bot/        # Android UI 봇
    ├── README.md
    ├── AD_REWARDS.md
    ├── API_RESEARCH.md
    ├── AUTOMATION_TARGETS.md
    ├── CALIBRATION_FULL.md
    ├── JADX_FULL_INVENTORY.md
    ├── __init__.py
    ├── __main__.py
    ├── actions.py
    ├── auto_calibrate.py
    ├── calibrate.py
    ├── config_loader.py
    ├── discover.py
    ├── driver.py
    ├── i18n_ko.properties
    ├── loop.py
    ├── notify.py
    ├── safety.py
    ├── settings.py
    ├── state.py
    ├── vision.py
    └── calibration/         # OCR 기준점/스크린샷
        ├── *.png
        ├── *.yaml
        └── *.ocr.yaml
```

## 로컬 개발 / Local Development

```bash
# 의존성 동기화 (봇 포함)
uv sync --extra bot

# 린트 (pyproject.toml의 ruff 설정 사용)
ruff check .

# 타입 검사 (선택, basedpyright 설정 동봉)
basedpyright

# 핫리로드 (선택, watchexec 사용 시)
watchexec -e py "python main.py"

# 워커 로컬 실행
cd worker && npm install && wrangler dev
```

## 테스트 / Testing

이 저장소에는 자동화 테스트 스위트가 포함되어 있지 않습니다. 권장 절차:

| 시나리오 / Scenario | 권장 접근 / Approach |
|---|---|
| 파이프라인 단위 | `store.py`를 임시 디렉터리로 가리키고 `httpx` 모의(Mock)로 게임 API를 시뮬레이션 |
| 스크래퍼 회귀 | 알려진 HTML 스냅샷을 고정 입력으로 사용 |
| 봇 비전 | 캘리브레이션 이미지에 대해 `vision.py` 인식 정확도를 회귀 비교 |
| Worker | `worker/`에서 `wrangler dev` 후 수동 트리거 |

## 문제 해결 / Troubleshooting

| 증상 / Symptom | 추정 원인 / Likely cause | 조치 / Action |
|---|---|---|
| `auth.py` 토큰 만료 | 세션 TTL 초과 | `.env`의 자격증명 갱신, 갱신 로직 확인 |
| 스크랩 결과 0건 | 소스 HTML 구조 변경 | `scraper.py`의 셀렉터/파서 갱신 |
| 봇이 메인 화면 미인식 | 게임 버전 변경으로 캘리브레이션 불일치 | `python -m idle_outpost_bot.calibrate` 재실행 |
| OCR 결과가 비어 있음 | 캘리브레이션 이미지 해상도 불일치 | `calibration/main.png` 등 기준 이미지 재생성 |
| Worker 배포 실패 | `wrangler.jsonc` 설정 오류 | [worker/README.md](worker/README.md)의 환경 변수 점검 |
| 의존성 충돌 | 시스템 Python 또는 PaddlePaddle 호환성 | `uv`로 3.11+ 환경 분리 설치 |

## 운영 관측 가능성 / Operator-Facing Observability

| 채널 / Channel | 모듈 / Module | 내용 / Content |
|---|---|---|
| 영속 상태 / Persisted state | `store.py` | 처리된 코드, 클레임 성공/실패 이력 |
| 외부 알림 / External notify | `notifier.py`, `idle_outpost_bot/notify.py` | 웹훅/메시지 결과 통보 |
| 안전 가드 / Safety guard | `idle_outpost_bot/safety.py` | 디바이스 충돌 방지 이벤트 |
| Worker 로그 / Worker logs | `worker/src/index.ts` | Cloudflare 대시보드/Logs |

## 기여 / Contributing

기여 절차는 [CONTRIBUTING.md](CONTRIBUTING.md)를 참조하세요. 주요 규칙:

- Python 코드 스타일은 [pyproject.toml](pyproject.toml)의 ruff 설정을 따릅니다 (`line-length = 100`, `target-version = py311`).
- 새 의존성은 `pyproject.toml`의 `dependencies` 또는 `optional-dependencies`에 추가합니다.
- 봇 관련 변경은 `idle_outpost_bot/calibration/`의 기준 데이터를 함께 갱신해야 합니다.

## 책임자 / Points of Contact

| 역할 / Role | 위치 / Location |
|---|---|
| 이슈 트래커 / Issue tracker | 저장소 Issues 탭 |
| 기여 가이드 / Contribution guide | [CONTRIBUTING.md](CONTRIBUTING.md) |
| 운영 가이드 / Ops guide | 본 README의 [Commands Reference](#명령어-레퍼런스--commands-reference) |
| 봇 운영 / Bot operations | [idle_outpost_bot/README.md](idle_outpost_bot/README.md) |
| Worker 운영 / Worker operations | [worker/README.md](worker/README.md) |

## 추가 문서 / Further Documentation

| 문서 / Document | 경로 / Path |
|---|---|
| 기여 가이드 / Contributing | [CONTRIBUTING.md](CONTRIBUTING.md) |
| 라이선스 / License | [LICENSE](LICENSE) |
| 봇 패키지 가이드 / Bot package guide | [idle_outpost_bot/README.md](idle_outpost_bot/README.md) |
| 광고 보상 참고 / Ad rewards notes | [idle_outpost_bot/AD_REWARDS.md](idle_outpost_bot/AD_REWARDS.md) |
| API 조사 / API research | [idle_outpost_bot/API_RESEARCH.md](idle_outpost_bot/API_RESEARCH.md) |
| 자동화 대상 / Automation targets | [idle_outpost_bot/AUTOMATION_TARGETS.md](idle_outpost_bot/AUTOMATION_TARGETS.md) |
| 캘리브레이션 상세 / Calibration details | [idle_outpost_bot/CALIBRATION_FULL.md](idle_outpost_bot/CALIBRATION_FULL.md) |
| JADX 인벤토리 / JADX inventory | [idle_outpost_bot/JADX_FULL_INVENTORY.md](idle_outpost_bot/JADX_FULL_INVENTORY.md) |
| Worker 가이드 / Worker guide | [worker/README.md](worker/README.md) |

## 면책 / Disclaimer

이 도구는 개인 사용/연구 목적을 위한 비공식 통합 키트이며 게임 운영자의 보증을 받지 않습니다. 게임 이용약관 및 관련 법규를 준수하는 것은 사용자의 책임입니다. 자동화 사용으로 인한 계정 제재에 대해 저장소 유지자는 책임을 지지 않습니다.

## 라이선스 / License

이 저장소는 [LICENSE](LICENSE) 파일에 명시된 조건에 따라 배포됩니다.