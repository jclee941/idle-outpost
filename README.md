# idle-outpost-codes

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
[![License](https://img.shields.io/badge/license-MIT-green)](#LICENSE)
[![Worker](https://img.shields.io/badge/worker-Cloudflare%20Workers-orange)](#worker)

**Idle Outpost 프로모 코드 모니터링, 매일 자동 수령 CLI, 그리고 Android 인게임 자동화 봇**을 한 저장소에서 묶은 프로젝트입니다. 게임 측 코드 배포 채널(소셜/공지/이벤트 페이지)을 긁어 코드를 모으고, 게임 API 또는 에뮬레이터 기반 봇으로 일일 보상을 수령하며, Cloudflare Worker 기반 알림 채널로 변경 사항을 푸시합니다.

| 항목 | 값 |
| --- | --- |
| 주 언어 | Python 3.11+ (CLI/봇) / TypeScript (Worker) |
| 패키지명 | `idle-outpost-codes` (v0.1.0) |
| 라이선스 | MIT (`LICENSE`) |
| 상태 | 활발히 개발 중 (안정 기능: 코드 스크레이퍼, 알림 Worker / 실험적: Android 봇 자동 보상) |
| 운영 진입점 | `python -m idle_outpost_bot`, `python main.py`, `wrangler deploy` |
| 대상 사용자 | "Idle Outpost" 게임 플레이어, 본인을 위한 매크로 운영자 |

### 동작 흐름 (한눈에 보기)

1. `scraper.py`가 코드 배포 소스(설정 가능한 URL 목록)에서 새 프로모 코드를 감지합니다.
2. `store.py`가 로컬 SQLite/JSON 캐시에 이미 알려진 코드인지 비교합니다.
3. 신규 코드는 `auth.py` → `claim_api.py` → `redeemer.py`로 게임 측에 자동 수령을 요청합니다.
4. `notifier.py`가 결과를 `worker/`의 Cloudflare Worker 엔드포인트로 전송하고, Worker가 푸시/웹훅으로 사용자에게 전달합니다.
5. (선택) `idle_outpost_bot/`의 Android 봇이 에뮬레이터에서 비전 기반으로 일일 퀘스트/광고 보상을 수령합니다.

---

## 목차

- [개요 / Purpose](#개요--purpose)
- [패키지 구성 / Package Contents](#패키지-구성--package-contents)
- [상태 / Status](#상태--status)
- [먼저 읽을 파일 / First Files to Read](#먼저-읽을-파일--first-files-to-read)
- [API / 엔트리포인트](#api--엔트리포인트)
- [빠른 시작 / Quickstart](#빠른-시작--quickstart)
- [명령어 / Commands Reference](#명령어--commands-reference)
- [설정 / Configuration](#설정--configuration)
- [로컬 개발 / Local Development](#로컬-개발--local-development)
- [테스트 / Testing](#testing)
- [기여 / Contributing](#기여--contributing)
- [유지보수자 / Maintainers](#유지보수자--maintainers)
- [추가 문서 / Further Documentation](#추가-문서--further-documentation)
- [라이선스 / License](#라이선스--license)

---

## 개요 / Purpose

이 프로젝트는 모바일 게임 **Idle Outpost**의 두 가지 번거로운 작업을 자동화합니다.

- **프로모 코드 모니터링 + 자동 수령**: 게임 측 코드 배포 페이지와 공식 채널을 주기적으로 스크레이핑하고, 새 코드를 감지하면 인증 후 게임 API로 즉시 수령합니다.
- **매일 보상 자동화 (Android 봇)**: PaddleOCR + Appium 기반 비전 봇이 에뮬레이터에서 일일 퀘스트, 캘린더 출석, 광고 보상, 카드 보상 등을 자동 수령합니다. 모든 동작은 안전 가드(`safety.py`)와 OCR 캘리브레이션 데이터(`idle_outpost_bot/calibration/`)로 제어됩니다.

대상 사용자는 본인의 계정에 한해 QoL(품질-of-라이프) 자동화를 원하는 게이머입니다. 본 프로젝트는 게임 이용약관을 우회하지 않으며, 운영 책임은 사용자 본인에게 있습니다.

---

## 패키지 구성 / Package Contents

| 경로 | 역할 |
| --- | --- |
| `main.py` | CLI 오케스트레이터. 스크레이퍼 → 수령 → 알림 파이프라인 진입점 |
| `scraper.py` | 코드 배포 소스 파싱 (`beautifulsoup4`, `httpx`) |
| `auth.py` | 게임 측 인증 토큰 발급/갱신 |
| `claim_api.py` | 일일 보상 / 코드 수령 API 클라이언트 |
| `redeemer.py` | 인증된 세션으로 프로모 코드 적용 |
| `notifier.py` | 결과/이벤트 알림 직렬화 및 Worker로 전송 |
| `store.py` | 로컬 코드 캐시 및 수령 이력 (SQLite) |
| `idle_outpost_bot/` | Android 에뮬레이터 비전 봇 패키지 |
| `idle_outpost_bot/driver.py` | Appium 세션 관리 |
| `idle_outpost_bot/vision.py` | PaddleOCR 스크린샷 인식 |
| `idle_outpost_bot/actions.py` | 탭/스와이프/입력 동작 프리미티브 |
| `idle_outpost_bot/loop.py` | 일일 루프 (퀘스트 → 광고 → 캘린더 → 카드) |
| `idle_outpost_bot/calibrate.py`, `auto_calibrate.py` | 화면 템플릿/OCR 캘리브레이션 |
| `idle_outpost_bot/calibration/` | 화면별 OCR YAML 및 기준 PNG |
| `idle_outpost_bot/safety.py` | 비정상 상태 감지 및 정지 가드 |
| `idle_outpost_bot/state.py`, `settings.py`, `config_loader.py` | 봇 상태/설정 |
| `idle_outpost_bot/notify.py` | 봇 결과 알림 어댑터 |
| `worker/` | Cloudflare Worker (TypeScript) 알림 엔드포인트 |
| `worker/src/index.ts` | 푸시/웹훅 핸들러 |
| `worker/wrangler.jsonc` | Worker 배포 설정 |
| `pyproject.toml`, `uv.lock` | Python 의존성 잠금 |
| `LICENSE`, `CONTRIBUTING.md` | 라이선스, 기여 가이드 |

---

## 상태 / Status

| 구성 요소 | 상태 | 비고 |
| --- | --- | --- |
| `main.py` CLI 파이프라인 | 안정 | 소규모 단일 사용자 운영 검증 |
| `worker/` 알림 | 안정 | Cloudflare Workers 무료 플랜에서 동작 |
| `idle_outpost_bot/` | 실험적 | 게임 UI 변경 시 `calibration/` 업데이트 필요 |
| 다국어 | 부분 (`i18n_ko.properties` 한국어) | 영어 기본, 한국어 리소스 포함 |
| 테스트 | 제한적 | 수동 시나리오 위주, 자동화는 추후 보강 |

**프로덕션 준비도**: 개인 백오피스 도구 수준. 다중 사용자/무인 장기 운영을 위한 관측성/재시도/백오프는 아직 기본 수준입니다.

---

## 먼저 읽을 파일 / First Files to Read

| 우선순위 | 파일 | 이유 |
| --- | --- | --- |
| 1 | `pyproject.toml` | 의존성, 선택적 extras(`bot`), Python 버전 확인 |
| 2 | `main.py` | CLI 진입점과 파이프라인 호출 순서 파악 |
| 3 | `scraper.py` | 코드 소스 URL과 파싱 전략 |
| 4 | `auth.py` + `claim_api.py` | 게임 측 인증/수령 흐름 |
| 5 | `notifier.py` + `worker/src/index.ts` | 알림 송수신 계약 |
| 6 | `idle_outpost_bot/loop.py` | 봇 일일 루프의 단계 정의 |
| 7 | `idle_outpost_bot/calibration/` | 화면 인식 기준 데이터, 디버깅 시 1순위 |
| 8 | `idle_outpost_bot/safety.py` | 봇 안전 정지 조건 |

---

## API / 엔트리포인트

### Python CLI

| 모듈 | 호출 형태 | 용도 |
| --- | --- | --- |
| `main.py` | `python main.py scrape` | 코드 스크레이퍼 단독 실행 |
| `main.py` | `python main.py claim` | 캐시된 신규 코드 수령 |
| `main.py` | `python main.py notify` | 미전송 알림 재시도 |
| `main.py` | `python main.py all` | 스크레이프 → 수령 → 알림 풀 파이프라인 |
| `idle_outpost_bot` | `python -m idle_outpost_bot` | Android 봇 일일 루프 |
| `idle_outpost_bot` | `python -m idle_outpost_bot.calibrate` | 화면 캘리브레이션 도구 |
| `idle_outpost_bot` | `python -m idle_outpost_bot.auto_calibrate` | 자동 캘리브레이션 |

### Cloudflare Worker

| 메서드 | 경로 | 용도 |
| --- | --- | --- |
| `POST` | `/notify` | `notifier.py`가 보내는 알림 수신 후 푸시/웹훅 전달 |
| `GET` | `/health` | Worker 상태 확인 |
| `GET` | `/` | 서비스 정보 |

요청 스키마 예시(`/notify`):

```json
{
  "type": "code_claimed",
  "code": "SUMMER2024",
  "reward": "Gold x1000",
  "account": "<account-id>",
  "ts": "2024-01-01T00:00:00Z"
}
```

---

## 빠른 시작 / Quickstart

### 1. 저장소 클론 및 Python 의존성 설치

```bash
git clone <your-fork-url> idle-outpost-codes
cd idle-outpost-codes
# uv 사용 시
uv sync
# 또는 표준 venv
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

### 2. 환경 변수

`.env` 파일을 저장소 루트에 작성합니다 (예시는 `notifier.py`/`auth.py` 키 이름과 일치).

```dotenv
# 게임 인증
GAME_ACCOUNT_ID=<your-account-id>
GAME_AUTH_TOKEN=<token>

# 알림 Worker
WORKER_URL=https://<your-worker>.workers.dev
WORKER_SHARED_SECRET=<shared-secret>

# 스크레이퍼 소스 (콤마 구분 URL 목록)
SCRAPE_SOURCES=https://example.com/news,https://example.com/codes
```

### 3. 코드 파이프라인 실행

```bash
python main.py all
```

### 4. (선택) Android 봇 설치

```bash
pip install -e ".[bot]"
python -m idle_outpost_bot --help
```

봇을 처음 실행하면 `idle_outpost_bot/calibration/`의 기준 화면과 실제 에뮬레이터 화면이 일치하는지 확인합니다. 게임 UI가 바뀌었다면 캘리브레이션을 다시 수행하세요.

```bash
python -m idle_outpost_bot.calibrate --screen main_screen
```

### 5. (선택) Worker 배포

```bash
cd worker
npm install
npx wrangler deploy
```

---

## 명령어 / Commands Reference

| 명령 | 설명 |
| --- | --- |
| `python main.py scrape` | 소스에서 코드 수집, 신규 항목만 `store.py`에 기록 |
| `python main.py claim` | `store.py`의 미수령 코드를 API로 일괄 수령 |
| `python main.py notify` | 알림 전송 실패 항목 재시도 |
| `python main.py all` | 위 세 단계를 순차 실행 |
| `python -m idle_outpost_bot` | Android 봇 일일 루프 시작 |
| `python -m idle_outpost_bot.calibrate --screen <name>` | 특정 화면 캘리브레이션 |
| `python -m idle_outpost_bot.auto_calibrate` | 다중 화면 자동 캘리브레이션 |
| `python -m idle_outpost_bot --dry-run` | 동작 로그만 출력하고 실제 탭/스와이프 생략 |
| `cd worker && npx wrangler dev` | Worker 로컬 개발 서버 |
| `cd worker && npx wrangler deploy` | Worker 배포 |
| `ruff check .` | 린트 (선택) |
| `basedpyright` | 타입 검사 (선택) |

---

## 설정 / Configuration

| 설정 | 위치 | 기본값/형식 |
| --- | --- | --- |
| 스크레이퍼 소스 | `SCRAPE_SOURCES` (env) | URL 콤마 구분 목록 |
| 인증 토큰 | `auth.py` 로더 | env 기반 |
| 알림 엔드포인트 | `WORKER_URL`, `WORKER_SHARED_SECRET` | env 기반 |
| 봇 디바이스 | `idle_outpost_bot/settings.py` | Appium capability dict |
| OCR 임계값 | `idle_outpost_bot/vision.py` | 신뢰도 0.0~1.0 |
| 안전 가드 | `idle_outpost_bot/safety.py` | 비정상 화면 감지 시 자동 정지 |
| 화면 캘리브레이션 | `idle_outpost_bot/calibration/<screen>.ocr.yaml` | ROI 박스 + 텍스트 기대값 |
| Worker 라우트 | `worker/wrangler.jsonc` | Cloudflare 라우팅 규칙 |
| 한국어 리소스 | `idle_outpost_bot/i18n_ko.properties` | 키=값 |

---

## 로컬 개발 / Local Development

- Python 3.11+, `uv` 권장 (lockfile이 `uv.lock`).
- 선택적 `bot` extras는 `paddleocr`/`paddlepaddle` 등 무거운 의존성을 포함하므로 기본 설치에서 제외되어 있습니다. 봇 작업 시에만 설치하세요.
- Worker 개발은 `worker/` 디렉터리에서 `npm install` 후 `npx wrangler dev`로 로컬에서 `notifier.py`의 요청을 받을 수 있습니다.
- 코드 스타일: `ruff` (`line-length = 100`, `target-version = py311`).
- 타입 검사: `basedpyright` (venv 경로 `.venv`).
- 게임 UI 변경이 감지되면 `idle_outpost_bot/calibration/`의 기준 PNG와 OCR YAML을 갱신한 뒤 PR을 올려 주세요.

---

## Testing

자동화 테스트는 아직 제한적입니다. 수동 시나리오는 다음 순서로 검증합니다.

1. `python main.py scrape`로 신규 코드가 `store.py` 캐시에 들어가는지 확인
2. `python main.py claim`로 API 수령이 성공하고 알림이 발송되는지 확인
3. `python -m idle_outpost_bot --dry-run`으로 봇이 화면을 정확히 인식하는지 확인
4. `python -m idle_outpost_bot`으로 실 디바이스에서 1회 일일 루프 완주
5. `worker/`를 `wrangler dev`로 띄우고 `curl`로 `/health`, `/notify` 확인

PR 전에는 최소한 위 1~3단계를 직접 수행해 주세요.

---

## 기여 / Contributing

기여 절차는 `CONTRIBUTING.md`를 따릅니다. 핵심 규칙:

- 게임 서버에 부하를 주지 않도록 스크레이퍼는 캐시 기반 폴링을 사용합니다.
- 봇 PR에는 영향받는 화면의 캘리브레이션 데이터 갱신을 포함합니다.
- 환경 변수 이름과 Worker 스키마는 호환성을 유지합니다.
- 커밋 메시지는 변경 범위가 명확하도록 작성합니다.

---

## 유지보수자 / Maintainers

| 역할 | 책임 |
| --- | --- |
| CLI 파이프라인 (`main.py`, `scraper.py`, `claim_api.py`, `redeemer.py`, `notifier.py`, `store.py`, `auth.py`) | 코드 수집·수령·알림 파이프라인 |
| Worker (`worker/`) | 알림 수신·푸시·웹훅 엔드포인트 |
| Android 봇 (`idle_outpost_bot/`) | 에뮬레이터 일일 루프, 비전 캘리브레이션 |

이슈/PR은 저장소 트래커를 통해 받습니다. 보안 관련 보고는 공개 이슈 대신 비공개 채널을 사용하세요.

---

## 추가 문서 / Further Documentation

| 문서 | 경로 | 내용 |
| --- | --- | --- |
| Worker 모듈 README | [`worker/README.md`](worker/README.md) | Cloudflare Worker 배포/로컬 실행 세부 절차 |
| 봇 패키지 README | [`idle_outpost_bot/README.md`](idle_outpost_bot/README.md) | 봇 운영 가이드, 캘리브레이션 절차 |
| 광고 보상 자동화 | [`idle_outpost_bot/AD_REWARDS.md`](idle_outpost_bot/AD_REWARDS.md) | 광고 보상 흐름 및 안전 가드 |
| API 리서치 노트 | [`idle_outpost_bot/API_RESEARCH.md`](idle_outpost_bot/API_RESEARCH.md) | 게임 측 API/엔드포인트 조사 메모 |
| 자동화 대상 정리 | [`idle_outpost_bot/AUTOMATION_TARGETS.md`](idle_outpost_bot/AUTOMATION_TARGETS.md) | 자동화 대상 화면/동작 카탈로그 |
| 캘리브레이션 전문 | [`idle_outpost_bot/CALIBRATION_FULL.md`](idle_outpost_bot/CALIBRATION_FULL.md) | 캘리브레이션 원리와 신규 화면 추가 절차 |
| JADX 인벤토리 | [`idle_outpost_bot/JADX_FULL_INVENTORY.md`](idle_outpost_bot/JADX_FULL_INVENTORY.md) | 디컴파일 결과에서 추출한 식별자/리소스 메모 |
| 기여 가이드 | [`CONTRIBUTING.md`](CONTRIBUTING.md) | PR/이슈 규칙 |
| 데모 화면 | `video1.png` | 메인 화면 시연 이미지 |

---

## 라이선스 / License

이 저장소는 `LICENSE` 파일(MIT)에 따라 배포됩니다. 서드파티 의존성(Appium, PaddleOCR, Selenium, Cloudflare Workers SDK 등)은 각자의 라이선스를 따릅니다.