# Idle Outpost Codes

![Python](https://img.shields.io/badge/python-3.11%2B-blue) ![uv](https://img.shields.io/badge/deps-uv-purple) [![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE) ![Bot](https://img.shields.io/badge/optional-android%20bot-orange) ![Worker](https://img.shields.io/badge/optional-cloudflare%20worker-orange) ![Status](https://img.shields.io/badge/status-experimental-yellow)

> **프로모션 코드 모니터링 · 일일 보상 클레임 · 안드로이드 자동화(옵션)**
> *Promo-code monitor · daily-reward claim CLI · optional Android automation bot*

## 한 줄 요약 / One-line summary

핵심 파이프라인은 단일 Python CLI(`python main.py`)이며, 같은 저장소에서 안드로이드 비전 봇과 Cloudflare Worker를 옵션으로 활성화할 수 있습니다.

The core pipeline is a single Python CLI (`python main.py`); an Android vision bot and a Cloudflare Worker live in the same repository and can be enabled independently.

## 빠른 상태 / Quick status

| 항목 / Item | 값 / Value | 비고 / Notes |
|---|---|---|
| 패키지 / Package | `idle-outpost-codes` | [`pyproject.toml`](pyproject.toml) |
| 버전 / Version | `0.1.0` | 사전 배포 / pre-release |
| Python | `>= 3.11` | `requires-python` |
| 의존성 관리 / Dependency manager | `uv` 권장 / recommended | [`uv.lock`](uv.lock) 포함 |
| 라이선스 / License | MIT | [`LICENSE`](LICENSE) |
| 운영 준비도 / Production readiness | Experimental | 스크래퍼 + 클레임 CLI 안정, 봇은 실험적 |
| 진입점 / Entry point | `python main.py` | 단일 진입점 |
| 옵션 A / Optional A | Android vision bot | [`idle_outpost_bot/`](idle_outpost_bot/) |
| 옵션 B / Optional B | Cloudflare Worker | [`worker/`](worker/) |
| 영속 레이어 / Persistence | `store.py` | 코드 ID 기준 멱등 |
| 알림 채널 / Notifications | `notifier.py` | 단일 어댑터 |

## 흐름 한눈에 / Flow at a glance

1. `scraper.py` — 공개 웹에서 프로모션 코드를 수집합니다.
2. `redeemer.py` — 새 코드를 게임 HTTP API로 등록(클레임)합니다.
3. `claim_api.py` — 클레임 HTTP 호출을 래핑합니다.
4. `store.py` — 모든 결과를 단일 영속 레이어에 기록합니다.
5. `notifier.py` — 결과를 단일 알림 어댑터로 푸시합니다.
6. (옵션) `idle_outpost_bot/` — 안드로이드 디바이스에서 비전 기반 UI 자동화.
7. (옵션) `worker/` — Cloudflare Edge에서 스케줄링 트리거.

English:

1. `scraper.py` collects promo codes from public web sources.
2. `redeemer.py` registers new codes through the game's HTTP API.
3. `claim_api.py` wraps the claim HTTP call.
4. `store.py` records every result in a single persistence layer.
5. `notifier.py` pushes results through one notification adapter.
6. (optional) `idle_outpost_bot/` runs vision-based UI automation on Android.
7. (optional) `worker/` triggers scheduled runs at the Cloudflare Edge.

## 목차 / Contents

- [목적 / Purpose](#목적--purpose)
- [패키지 구성 / Package contents](#패키지-구성--package-contents)
- [첫 번째로 읽을 파일 / First files to read](#첫-번째로-읽을-파일--first-files-to-read)
- [API / 진입점 / Entry points](#api--진입점--entry-points)
- [빠른 시작 / Quickstart](#빠른-시작--quickstart)
- [설정 / Configuration](#설정--configuration)
- [명령 참조 / Commands reference](#명령-참조--commands-reference)
- [로컬 개발 / Local development](#로컬-개발--local-development)
- [테스트 / Testing](#테스트--testing)
- [기여 / Contributing](#기여--contributing)
- [운영 및 도움말 / Operations & help](#운영-및-도움말--operations--help)
- [유지보수자 / Maintainers](#유지보수자--maintainers)
- [추가 문서 / Further documentation](#추가-문서--further-documentation)
- [라이선스 / License](#라이선스--license)

## 목적 / Purpose

`idle-outpost-codes`는 모바일 게임 *Idle Outpost*의 프로모션 코드를 모니터링하고 일일 보상을 자동으로 클레임하기 위한 Python 패키지입니다. 수집과 클레임 두 단계가 같은 저장소와 같은 알림 채널을 공유해 멱등(idempotent)이며 재시작에 안전합니다.

핵심 사용자:

- 게임 신규/복귀 플레이어 — 새 코드를 놓치지 않고 자동으로 클레임.
- 다중 계정 운영자 — 여러 계정의 일일 보상을 스케줄링.
- 자동화 연구자 — 게임 자동화 참고 구현(봇 모듈).

이 패키지가 유용한 이유: 프로모션 코드는 자주 교체되고 인게임 UI 클레임 절차가 여러 단계라 수동 루프가 비효율적입니다. 단일 CLI가 모니터링/클레임/기록을 처리해 수동 루프를 제거합니다.

운영 준비도: 스크래퍼 + 클레임 CLI는 사전 배포 단계지만 일상적 사용에 안정적입니다. 안드로이드 봇은 실험적이며 게임 UI 변경에 취약합니다. 자세한 주의 사항은 [`idle_outpost_bot/README.md`](idle_outpost_bot/README.md)와 [`CALIBRATION_FULL.md`](idle_outpost_bot/CALIBRATION_FULL.md)를 참조하세요.

## 패키지 구성 / Package contents

루트는 Python CLI 패키지, `idle_outpost_bot/`은 옵션 안드로이드 봇, `worker/`는 옵션 Cloudflare Worker입니다.

| 경로 / Path | 역할 / Role | 언어 / Language |
|---|---|---|
| `main.py` | 단일 CLI 진입점 / single CLI entry point | Python |
| `scraper.py` | 공개 웹 코드 수집 / public-web code collector | Python |
| `redeemer.py` | 게임 API로 코드 등록 / code redemption via game API | Python |
| `claim_api.py` | 클레임 HTTP 호출 래퍼 / claim-call wrapper | Python |
| `auth.py` | 인증 헬퍼 / authentication helper | Python |
| `store.py` | 영속 레이어(공유) / shared persistence layer | Python |
| `notifier.py` | 알림 어댑터(공유) / shared notification adapter | Python |
| `pyproject.toml` | 패키지 메타 + 의존성 / package meta + deps | TOML |
| `uv.lock` | 잠긴 의존성 그래프 / locked dep graph | TOML |
| `LICENSE` | MIT 라이선스 / MIT license | — |
| `CONTRIBUTING.md` | 기여 가이드 / contribution guide | — |
| `video1.png` | 데모 / demo screenshot | image |
| `idle_outpost_bot/` | 옵션 안드로이드 비전 봇 / optional Android vision bot | Python |
| `idle_outpost_bot/calibration/` | OCR 템플릿 + 캘리브레이션 자산 / OCR templates + calibration assets | YAML + PNG |
| `idle_outpost_bot/AD_REWARDS.md` | 광고 보상 메모 / ad-reward notes | — |
| `idle_outpost_bot/API_RESEARCH.md` | API 리서치 노트 / API research notes | — |
| `idle_outpost_bot/AUTOMATION_TARGETS.md` | 자동화 대상 인벤토리 / automation-target inventory | — |
| `idle_outpost_bot/CALIBRATION_FULL.md` | 캘리브레이션 가이드 / calibration guide | — |
| `idle_outpost_bot/JADX_FULL_INVENTORY.md` | 디컴파일 인벤토리 / decompile inventory | — |
| `idle_outpost_bot/i18n_ko.properties` | 한국어 i18n / Korean i18n | properties |
| `worker/` | 옵션 Cloudflare Worker / optional CF Worker | TypeScript |
| `worker/src/index.ts` | Worker 핸들러 / Worker handler | TypeScript |
| `worker/wrangler.jsonc` | Worker 설정 / Worker config | JSONC |
| `worker/package.json` | Node 의존성 / Node deps | JSON |

## 첫 번째로 읽을 파일 / First files to read

운영자가 가장 먼저 볼 파일 권장 순서:

1. [`README.md`](README.md) (이 파일) — 무엇이 무엇인지.
2. [`pyproject.toml`](pyproject.toml) — 의존성과 옵션 그룹.
3. [`main.py`](main.py) — 단일 진입점의 명령 구조.
4. [`store.py`](store.py) — 영속 모델(중복 방지 키).
5. [`notifier.py`](notifier.py) — 알림 어댑터 인터페이스.
6. (봇 활성화 시) [`idle_outpost_bot/README.md`](idle_outpost_bot/README.md).
7. (워커 활성화 시) [`worker/README.md`](worker/README.md).

## API / 진입점 / Entry points

### CLI 진입점 / CLI entry point

- `python main.py` — 단일 진입점. 사용 가능한 서브커맨드와 플래그는 `--help`로 확인합니다.

### Python 모듈 진입점 / Python module entry points

| 모듈 / Module | 역할 / Role |
|---|---|
| `idle_outpost_codes.scraper` | 공개 웹에서 코드 수집 |
| `idle_outpost_codes.redeemer` | 게임 API로 코드 클레임 |
| `idle_outpost_codes.claim_api` | 클레임 HTTP 호출 |
| `idle_outpost_codes.auth` | 인증 헬퍼 |
| `idle_outpost_codes.store` | 영속 레이어 |
| `idle_outpost_codes.notifier` | 알림 어댑터 |

### (옵션) Worker 엔드포인트 / Optional Worker endpoint

`worker/src/index.ts`는 Cloudflare Workers 핸들러입니다. HTTP 요청 또는 Cron Trigger로 스케줄 실행을 시작할 수 있습니다. 정확한 경로와 페이로드는 [`worker/README.md`](worker/README.md)를 참조하세요.

### (옵션) Bot 진입점 / Optional Bot entry point

`idle_outpost_bot/__main__.py`는 안드로이드 디바이스에서 비전 기반 자동화를 시작합니다. 디바이스 연결과 캘리브레이션이 사전 요구됩니다.

## 빠른 시작 / Quickstart

### 1. 저장소 준비 / Get the source

```bash
git clone <repository-url> idle-outpost-codes
cd idle-outpost-codes
```

> 참고: 사내 Git 호스트를 사용하세요. README는 외부 원격 URL을 가정하지 않습니다.

### 2. 의존성 설치 / Install dependencies

`uv` 사용(권장):

```bash
uv sync
```

또는 pip:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 3. 환경 변수 / Environment variables

`.env` 파일을 작성합니다. 실제 키 이름은 [`auth.py`](auth.py)와 [`notifier.py`](notifier.py)의 `os.getenv`/`dotenv` 사용처에서 확인하세요.

```dotenv
# 예시 — 실제 키 이름은 코드 내 환경변수 사용처를 확인하세요
IDLE_OUTPOST_AUTH_TOKEN=
IDLE_OUTPOST_NOTIFY_WEBHOOK=
```

### 4. 첫 실행 / First run

```bash
python main.py --help
```

사용 가능한 서브커맨드 출력 후 일반적 흐름:

```bash
python main.py scrape
python main.py redeem
```

### 5. (옵션) 안드로이드 봇 / Optional Android bot

```bash
uv sync --extra bot
# 디바이스(Appium 서버) 연결 + OCR 템플릿 캘리브레이션 후
python -m idle_outpost_bot
```

자세한 절차는 [`idle_outpost_bot/README.md`](idle_outpost_bot/README.md)와 [`CALIBRATION_FULL.md`](idle_outpost_bot/CALIBRATION_FULL.md) 참조.

### 6. (옵션) Cloudflare Worker / Optional Cloudflare Worker

```bash
cd worker
npm install
npx wrangler deploy
```

자세한 절차는 [`worker/README.md`](worker/README.md) 참조.

## 설정 / Configuration

| 영역 / Area | 위치 / Location | 형식 / Format |
|---|---|---|
| 의존성 / Dependencies | [`pyproject.toml`](pyproject.toml) | TOML |
| 런타임 비밀값 / Runtime secrets | `.env` (코드에서 로드) | dotenv |
| 봇 디바이스 / Bot device | [`idle_outpost_bot/settings.py`](idle_outpost_bot/settings.py) | Python |
| 봇 상태 모델 / Bot state model | [`idle_outpost_bot/state.py`](idle_outpost_bot/state.py) | Python |
| 봇 OCR 템플릿 / Bot OCR templates | `idle_outpost_bot/calibration/*.ocr.yaml` | YAML |
| 봇 안전 정책 / Bot safety policy | [`idle_outpost_bot/safety.py`](idle_outpost_bot/safety.py) | Python |
| 워커 트리거 / Worker trigger | [`worker/wrangler.jsonc`](worker/wrangler.jsonc) | JSONC |

## 명령 참조 / Commands reference

CLI 서브커맨드(실제 이름은 [`main.py`](main.py)에서 확인):

| 명령 패턴 / Pattern | 목적 / Purpose |
|---|---|
| `python main.py --help` | 사용 가능한 서브커맨드 표시 |
| `python main.py scrape` | 공개 소스에서 새 코드 수집 |
| `python main.py redeem` | 미등록 코드 클레임 |
| `python main.py` (기본) | 전체 파이프라인 실행 |

모든 서브커맨드는 결과를 `store.py`에 기록하며 `notifier.py`로 알림을 발송합니다.

봇/워커 명령:

| 명령 / Command | 목적 / Purpose |
|---|---|
| `python -m idle_outpost_bot` | 안드로이드 비전 자동화 시작 |
| `python -m idle_outpost_bot.calibrate` | OCR 템플릿 캘리브레이션 |
| `python -m idle_outpost_bot.auto_calibrate` | 자동 캘리브레이션 |
| `cd worker && npm run dev` | Worker 로컬 실행(wrangler dev) |
| `cd worker && npx wrangler deploy` | Worker 배포 |

## 로컬 개발 / Local development

- Python 3.11+ 가상환경 사용(`.venv`).
- 린트: `ruff`(설정은 [`pyproject.toml`](pyproject.toml)).
- 타입 체크: `basedpyright`(설정은 [`pyproject.toml`](pyproject.toml)).
- 의존성 잠금: [`uv.lock`](uv.lock) 커밋 필수.
- 보안: 디바이스 IP/계정 정보는 커밋 금지. 호스트는 `localhost` 또는 환경변수로만 지정.

봇 모듈 작업 시:

```bash
uv sync --extra bot
python -m idle_outpost_bot.calibrate
```

OCR 템플릿은 `idle_outpost_bot/calibration/*.ocr.yaml`에 있고, 동일 경로의 PNG가 기준 이미지입니다. 화면 UI가 바뀌면 두 파일을 함께 갱신하세요.

워커 모듈 작업 시:

```bash
cd worker
npm install
npm run dev
```

## 테스트 / Testing

저장소는 사전 배포 단계로 표준화된 테스트 인프라가 정해져 있지 않습니다. 권장 절차:

1. 모의(mock) HTTP 서버를 두고 `scraper`/`redeemer`의 호출 단위 검증.
2. `store`의 멱등성(같은 코드 재시도 시 중복 기록 없음) 회귀 검증.
3. `notifier` 어댑터 인터페이스에 대한 페이크 어댑터 단위 테스트.
4. 봇 변경 시 `idle_outpost_bot/calibration/`의 OCR 템플릿 재캘리브레이션 + 화면 단위 테스트.

자동화된 테스트가 추가되면 이 섹션이 갱신됩니다.

## 기여 / Contributing

[`CONTRIBUTING.md`](CONTRIBUTING.md) 참조. 일반 원칙:

- 새 코드 소스를 추가할 때는 `scraper.py`의 추상화에 맞춰 어댑터 형태로 작성.
- 영속 스키마를 변경할 때는 `store.py`에서 마이그레이션 헬퍼를 함께 제공.
- 봇 UI 변경 시 `idle_outpost_bot/calibration/`의 OCR 템플릿 + [`CALIBRATION_FULL.md`](idle_outpost_bot/CALIBRATION_FULL.md)를 함께 갱신.
- 워커 변경 시 `worker/README.md`도 갱신.

## 운영 및 도움말 / Operations & help

운영자가 자주 보는 항목:

| 상황 / Situation | 조치 / Action |
|---|---|
| 파이프라인 동작 확인 / Pipeline check | `python main.py --help` + dry-run 옵션 확인 |
| 중복 클레임 방지 / Duplicate-claim guard | `store.py`가 코드 ID로 멱등 보장 — 재시작 안전 |
| 알림 채널 추가 / Add a notification backend | `notifier.py`에 새 어댑터 구현 추가 |
| 게임 UI 변경 / Game UI change | 봇 모듈 캘리브레이션 자산 재캘리브레이션 |
| 스크래퍼 소스 변경 / Scraper source change | `scraper.py`의 어댑터 시그니처 유지한 채 소스만 교체 |
| 버그 리포트 / Bug report | 재현 절차 + 로그 + 환경 정보(디바이스/워커) 첨부 |

도움이 필요하면 [`CONTRIBUTING.md`](CONTRIBUTING.md)의 연락처를 참조하세요.

## 유지보수자 / Maintainers

이 저장소는 게임 자동화/스크래핑 커뮤니티 기여로 유지됩니다. 신규 유지보수자는 [`CONTRIBUTING.md`](CONTRIBUTING.md)를 통해 합류할 수 있습니다. 공개된 개인 연락처는 README에 기재하지 않습니다 — 저장소 이슈 트래커와 [`CONTRIBUTING.md`](CONTRIBUTING.md)를 정식 채널로 사용하세요.

## 추가 문서 / Further documentation

| 문서 / Document | 위치 / Location | 내용 / Contents |
|---|---|---|
| 패키지 메타 / Package meta | [`pyproject.toml`](pyproject.toml) | 의존성 + 옵션 그룹 |
| 봇 모듈 가이드 / Bot module guide | [`idle_outpost_bot/README.md`](idle_outpost_bot/README.md) | 디바이스 연결, 캘리브레이션 |
| 광고 보상 메모 / Ad reward notes | [`idle_outpost_bot/AD_REWARDS.md`](idle_outpost_bot/AD_REWARDS.md) | 광고 보상 자동화 노트 |
| API 리서치 / API research | [`idle_outpost_bot/API_RESEARCH.md`](idle_outpost_bot/API_RESEARCH.md) | 게임 API 조사 결과 |
| 자동화 대상 / Automation targets | [`idle_outpost_bot/AUTOMATION_TARGETS.md`](idle_outpost_bot/AUTOMATION_TARGETS.md) | 자동화 가능한 화면 인벤토리 |
| 캘리브레이션 가이드 / Calibration guide | [`idle_outpost_bot/CALIBRATION_FULL.md`](idle_outpost_bot/CALIBRATION_FULL.md) | OCR 템플릿 캘리브레이션 절차 |
| 디컴파일 인벤토리 / Decompile inventory | [`idle_outpost_bot/JADX_FULL_INVENTORY.md`](idle_outpost_bot/JADX_FULL_INVENTORY.md) | APK 디컴파일 결과 |
| 워커 가이드 / Worker guide | [`worker/README.md`](worker/README.md) | Cloudflare Worker 배포/실행 |
| 기여 가이드 / Contributing | [`CONTRIBUTING.md`](CONTRIBUTING.md) | PR 절차, 코딩 규칙 |

## 라이선스 / License

MIT — 자세한 내용은 [`LICENSE`](LICENSE) 참조.