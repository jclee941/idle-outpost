# Idle Outpost Codes

![Python](https://img.shields.io/badge/python-3.11%2B-blue) ![uv](https://img.shields.io/badge/deps-uv-purple) [![License](https://img.shields.io/badge/license-MIT-green)](LICENSE) [![Bot](https://img.shields.io/badge/optional-android%20bot-orange)](#android-bot) [![Worker](https://img.shields.io/badge/optional-cloudflare%20worker-orange)](#cloudflare-worker)

> **프로모 코드 모니터링 · 일일 보상 클레임 · 안드로이드 자동화 봇**
> *Promo code monitor · daily-reward claim CLI · Android automation bot*

## 요약 (Summary, 한국어)

`idle-outpost-codes`는 모바일 게임 *Idle Outpost*를 위한 통합 자동화 키트입니다. 공개 웹에서 새 프로모션 코드를 주기적으로 수집하고, 게임의 공식 HTTP API로 코드를 등록(Redeem)하며, 일일 보상을 자동으로 클레임합니다. 선택적으로 안드로이드 디바이스/에뮬레이터에서 비전 기반 UI 봇을 구동하거나, Cloudflare Worker로 엣지 스케줄링을 연동할 수 있습니다. 모든 단계는 단일 영속 레이어와 단일 발신 알림 모듈을 공유하므로 멱등(idempotent)이며 재시작에 안전합니다.

운영자는 단일 진입점 `python main.py`만 기억하면 됩니다. 봇과 워커는 옵션이므로 가벼운 컨테이너나 로컬 크론으로도 핵심 파이프라인을 운용할 수 있습니다.

## Overview (English)

`idle-outpost-codes` is an automation kit for the mobile game *Idle Outpost*. It scrapes public sources for new promotional codes, redeems them through the game's official HTTP API, and claims daily rewards on a schedule. An optional Android UI bot (Appium + PaddleOCR) drives the game on a real device or emulator, and a Cloudflare Worker can trigger scheduled work from the edge. A single persistence layer and a single outbound notifier are shared by every stage so runs are idempotent and restart-safe.

The operator-facing entry point is `python main.py`. The Android bot and the Cloudflare Worker are optional add-ons and the core pipeline runs comfortably from a small container or a local cron.

## 상태 / Status

| 항목 / Item | 값 / Value | 비고 / Notes |
|---|---|---|
| 패키지명 / Package name | `idle-outpost-codes` | `pyproject.toml` |
| 버전 / Version | 0.1.0 | 사전 배포 / pre-release |
| Python | ≥ 3.11 | `requires-python` |
| 의존성 관리 / Dependency manager | `uv` 권장 / recommended | `uv.lock` 동봉 / shipped |
| 라이선스 / License | MIT | [LICENSE](LICENSE) |
| 메인 파이프라인 / Main pipeline | Active | `python main.py` |
| Android 봇 / Android bot | Optional | `[bot]` extra |
| Cloudflare Worker | Optional | `worker/wrangler.jsonc` |
| 자동 테스트 / Automated tests | 없음 / None | 수동 검증 권장 / manual verification |

## 한눈에 보는 흐름 / Flow at a Glance

운영자가 가장 자주 호출하는 진입점은 `python main.py`이며, 보조 진입점은 `python -m idle_outpost_bot` (안드로이드 자동화)입니다. 단계별 책임은 다음 표와 같습니다.

| 단계 / Stage | 모듈 / Module | 책임 / Responsibility |
|---|---|---|
| 1. 스크래핑 / Scrape | `scraper.py` | 공개 소스에서 신규 코드 후보 수집 / collect candidate codes from public sources |
| 2. 클레임 API / Claim API | `claim_api.py` | 게임 HTTP API에 코드 등록 요청 / POST redeemed codes to the game API |
| 3. 리디머 / Redeemer | `redeemer.py` | 스크랩 결과 → API 호출 오케스트레이션 / orchestrate scrape → claim |
| 4. 영속 / Persistence | `store.py` | 코드/일일 보상 처리 이력 저장 / persist claim history |
| 5. 인증 / Auth | `auth.py` | API 토큰 로테이션·갱신 / handle auth tokens |
| 6. 알림 / Notify | `notifier.py` | 실패/성공 알림 발송 / outbound notifications |
| 7. 진입점 / Entry | `main.py` | 위 단계를 한 사이클로 실행 / run a single cycle |

## 구성 요소 / Components

루트 디렉터리의 모듈은 코어 파이프라인을 구성합니다.

| 경로 / Path | 역할 / Role |
|---|---|
| `main.py` | 운영자 진입점. 스크랩 → 클레임 → 일일 보상 → 알림 한 사이클 실행 |
| `scraper.py` | 코드 후보 수집 (BeautifulSoup 기반) |
| `redeemer.py` | 후보 코드 → `claim_api.py` 오케스트레이션 |
| `claim_api.py` | 게임의 공식 코드 등록 엔드포인트 호출 |
| `auth.py` | API 인증 토큰 처리 |
| `store.py` | 처리 이력의 로컬 영속 레이어 |
| `notifier.py` | 단일 발신 채널(실패/성공 알림) |
| `pyproject.toml`, `uv.lock` | 의존성 선언과 잠금 파일 |
| `LICENSE` | MIT 라이선스 전문 |
| `CONTRIBUTING.md` | 기여 가이드 |
| `video1.png` | README/문서용 스크린샷 |

옵션 구성 요소는 다음과 같습니다.

| 경로 / Path | 역할 / Role |
|---|---|
| `worker/` | Cloudflare Worker. 엣지에서 주기 트리거 역할 (선택) |
| `idle_outpost_bot/` | 안드로이드 UI 자동화 봇 (Appium + PaddleOCR 기반, 선택) |

## 빠른 시작 / Quickstart

### 1. 저장소 준비 / Clone & enter

```bash
git clone <your-fork-url> idle-outpost-codes
cd idle-outpost-codes
```

### 2. 의존성 설치 / Install dependencies

`uv` 사용을 권장합니다.

```bash
# 핵심 파이프라인만 / core pipeline only
uv sync

# 안드로이드 봇까지 / include the Android bot
uv sync --extra bot
```

`pip`를 사용할 경우:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .                # 코어 / core
pip install -e ".[bot]"         # 코어 + 봇 / core + bot
```

### 3. 환경 변수 / Environment variables

`.env` 파일을 만들고 아래 키를 채워주세요. 실제 값은 본인 발급본으로 교체합니다.

```ini
# 게임 API / Game API
IDLE_OUTPOST_API_BASE=https://<game-api-host>
IDLE_OUTPOST_AUTH_TOKEN=<your-token>

# 알림 채널 / Notification channel (예: webhook URL, 이메일 등)
NOTIFIER_WEBHOOK_URL=<your-webhook-url>

# 봇 사용 시 / Bot only
ANDROID_DEVICE_UDID=<device-or-emulator-udid>
APPIUM_SERVER_URL=http://127.0.0.1:4723
```

비공개 호스트명·IP·토큰은 커밋하지 않습니다. 저장소에는 호스트 자리표시자만 기록하고, 실제 값은 본인 환경에서 주입합니다.

### 4. 한 사이클 실행 / Run one cycle

```bash
python main.py
```

성공 로그 예시:

```
[scrape] N candidate codes collected
[redeem] K new codes submitted
[daily] daily reward claimed
[notify] cycle complete
```

## 명령어 참고 / Commands Reference

| 명령 / Command | 설명 / Description |
|---|---|
| `python main.py` | 스크랩 → 클레임 → 일일 보상 → 알림 한 사이클 실행 |
| `python -m idle_outpost_bot` | 안드로이드 UI 자동화 봇 실행 |
| `python -m idle_outpost_bot.calibrate` | 보정 이미지/영역 재생성 (옵션) |
| `python -m idle_outpost_bot.auto_calibrate` | 자동 보정 모드 (옵션) |
| `uv sync` | 의존성 동기화 |
| `uv sync --extra bot` | 봇 의존성까지 동기화 |
| `uv run ruff check .` | 린트 (선택) |

## 설정 / Configuration

| 항목 / Item | 위치 / Location | 설명 / Description |
|---|---|---|
| API 엔드포인트 / API endpoint | `.env` (`IDLE_OUTPOST_API_BASE`) | 게임 서버 주소 |
| 인증 / Auth | `.env` (`IDLE_OUTPOST_AUTH_TOKEN`) | 토큰 또는 자격증명 |
| 알림 / Notifier | `notifier.py`, `.env` | 실패·성공 단일 채널 |
| 영속 / Persistence | `store.py` | 로컬 처리 이력 저장 |
| 봇 디바이스 / Bot device | `.env` (`ANDROID_DEVICE_UDID`, `APPIUM_SERVER_URL`) | Appium 세션 대상 |
| 봇 보정 / Bot calibration | `idle_outpost_bot/calibration/` | 화면 캡처·OCR 좌표 |

## Cloudflare Worker

`worker/` 디렉터리는 Wrangler 기반의 엣지 워커입니다. 스케줄러에서 주기적으로 `main.py` 또는 외부 트리거를 호출하기 위한 어댑터입니다.

| 파일 / File | 역할 / Role |
|---|---|
| `worker/wrangler.jsonc` | Wrangler 설정 (이름, 크론 트리거 등) |
| `worker/src/index.ts` | 워커 핸들러 |
| `worker/package.json`, `worker/tsconfig.json` | 의존성·TypeScript 설정 |
| `worker/package-lock.json` | 잠금 파일 |

자세한 내용은 [worker/README.md](worker/README.md)를 참조하세요.

## Android Bot

`idle_outpost_bot/`은 실제 디바이스나 에뮬레이터에서 게임 UI를 구동하는 비전 기반 봇입니다. Appium으로 안드로이드를 제어하고 PaddleOCR로 화면을 판독합니다.

| 하위 모듈 / Submodule | 역할 / Role |
|---|---|
| `__main__.py`, `loop.py` | 진입점과 메인 루프 |
| `driver.py` | Appium 세션 관리 |
| `vision.py` | PaddleOCR 기반 화면 인식 |
| `actions.py` | 클릭·스와이프 등 액션 프리미티브 |
| `discover.py`, `calibrate.py`, `auto_calibrate.py` | 화면 요소 발견·보정 |
| `safety.py` | 안전 가드 (이상 상태 중단 등) |
| `state.py` | 봇 내부 상태 머신 |
| `settings.py`, `config_loader.py` | 설정 로딩 |
| `notify.py` | 봇 전용 알림 채널 |
| `i18n_ko.properties` | 한국어 문자열 리소스 |
| `calibration/` | 화면별 캡처·OCR 좌표 자산 |

추가 문서:

- [idle_outpost_bot/README.md](idle_outpost_bot/README.md) — 봇 개요와 실행 절차
- [idle_outpost_bot/AD_REWARDS.md](idle_outpost_bot/AD_REWARDS.md) — 광고 보상 자동화 메모
- [idle_outpost_bot/AUTOMATION_TARGETS.md](idle_outpost_bot/AUTOMATION_TARGETS.md) — 자동화 대상 화면 목록
- [idle_outpost_bot/API_RESEARCH.md](idle_outpost_bot/API_RESEARCH.md) — 게임 API 리서치 노트
- [idle_outpost_bot/CALIBRATION_FULL.md](idle_outpost_bot/CALIBRATION_FULL.md) — 보정 절차 전문
- [idle_outpost_bot/JADX_FULL_INVENTORY.md](idle_outpost_bot/JADX_FULL_INVENTORY.md) — APK 인벤토리 (참고용)

## 로컬 개발 / Local Development

```bash
# 가상환경 / virtualenv
uv venv && source .venv/bin/activate

# 의존성 / deps
uv sync --extra bot

# 워커 의존성 / worker deps (Node.js 필요)
cd worker && npm install && cd ..
```

권장 워크플로:

1. `main.py` 한 사이클을 dry-run(또는 소규모 데이터)으로 호출해 회귀를 확인합니다.
2. UI 변경이 의심될 경우 `idle_outpost_bot/calibrate.py`로 캡처를 재생성합니다.
3. 봇 변경 후에는 `idle_outpost_bot/loop.py`를 짧은 시간 동안만 실행해 동작을 확인합니다.

## 테스트 / Testing

현재 자동 테스트 스위트는 포함되어 있지 않습니다. 변경 시 권장 절차는 다음과 같습니다.

| 단계 / Step | 검증 / Verification |
|---|---|
| 1 | `python main.py`를 dry-run으로 1회 실행, 종료 코드와 로그 확인 |
| 2 | 코드 후보가 비어 있을 때의 클레임 단계 동작 확인 |
| 3 | 네트워크 실패 시 `notifier.py` 발신 경로 확인 |
| 4 | 봇 변경 시 짧은 `loop.py` 실행으로 안전 가드 동작 확인 |

## 기여 / Contributing

1. 이슈 또는 PR로 변경 의도를 먼저 공유합니다.
2. `pyproject.toml`의 의존성을 가능한 한 좁은 범위로 유지합니다.
3. 비밀값(토큰·IP·자격증명)은 절대 커밋하지 않습니다.
4. 자세한 규칙은 [CONTRIBUTING.md](CONTRIBUTING.md)를 참조하세요.

## 라이선스 / License

본 저장소는 [LICENSE](LICENSE) (MIT) 조건 하에 배포됩니다.

## 운영·문의 / Operators & Contact

| 역할 / Role | 안내 / Pointer |
|---|---|
| 메인 파이프라인 운영 / Main pipeline ops | `python main.py`, `scraper.py`, `redeemer.py`, `claim_api.py`, `store.py`, `notifier.py`, `auth.py` |
| 봇 운영 / Bot ops | `idle_outpost_bot/`, `worker/` |
| 일반 문서 / General docs | [CONTRIBUTING.md](CONTRIBUTING.md), [LICENSE](LICENSE) |
| 봇 심화 문서 / Bot deep dive | [idle_outpost_bot/README.md](idle_outpost_bot/README.md) 및 동 폴더 내 `*.md` |

## 더 보기 / Further Reading

- [worker/README.md](worker/README.md) — Cloudflare Worker 사용법
- [idle_outpost_bot/README.md](idle_outpost_bot/README.md) — 안드로이드 봇 개요
- [idle_outpost_bot/AUTOMATION_TARGETS.md](idle_outpost_bot/AUTOMATION_TARGETS.md) — 자동화 대상 화면 정리
- [idle_outpost_bot/CALIBRATION_FULL.md](idle_outpost_bot/CALIBRATION_FULL.md) — 보정 절차
- [idle_outpost_bot/API_RESEARCH.md](idle_outpost_bot/API_RESEARCH.md) — 게임 API 리서치 노트