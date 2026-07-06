# idle-outpost-codes

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Cloudflare Workers](https://img.shields.io/badge/Cloudflare-Workers-F38020?logo=cloudflare&logoColor=white)](https://workers.cloudflare.com/)
[![Appium](https://img.shields.io/badge/Appium-Android-662D91)](http://appium.io/)
[![PaddleOCR](https://img.shields.io/badge/PaddleOCR-vision-0072CE)](https://github.com/PaddlePaddle/PaddleOCR)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## 한국어 요약

`idle-outpost-codes` 는 모바일 게임 **Idle Outpost** 의 프로모션 코드와 일일 보상을 자동으로 모니터링하고
수령하기 위한 워크스페이스입니다. 세 가지 배포 단위로 구성됩니다.

- **프로모션 코드 파이프라인** (`scraper.py`, `claim_api.py`, `redeemer.py`, `store.py`, `auth.py`, `notifier.py`)
  - 공개된 코드 목록을 주기적으로 스크랩하고, 인증 후 게임 API 로 클레임하고, 상태를 저장하고 알림을 보냅니다.
- **Cloudflare Worker HTTP API** (`worker/src/index.ts`)
  - 코드 목록과 클레임 상태를 외부에 노출하는 경량 엔드포인트입니다.
- **Android 자동화 봇** (`idle_outpost_bot/`)
  - Appium + Selenium 으로 기기를 제어하고, PaddleOCR 과 템플릿 매칭으로 화면을 판독하여 출석·퀘스트·광고 보상 루틴을
    반복 실행합니다.

## English Summary

A workspace for monitoring Idle Outpost promo codes, claiming daily rewards, and running an on-device Android
automation loop. It combines a Python scrape/claim pipeline, a Cloudflare Worker API, and an Appium-driven
Android bot with PaddleOCR vision calibration.

## Status

| Component            | Runtime                | Status         | Entry point                  | Owner surface                |
| -------------------- | ---------------------- | -------------- | ---------------------------- | ---------------------------- |
| Promo code pipeline  | Python 3.11+ CLI       | Active         | `python main.py`             | `main.py` orchestration      |
| HTTP API             | Cloudflare Worker      | Active         | `worker/src/index.ts`        | `wrangler.jsonc` deploy      |
| Android bot          | Python + Appium client | Active         | `python -m idle_outpost_bot` | `idle_outpost_bot/loop.py`   |
| Calibration assets   | YAML + PNG templates   | Active         | `idle_outpost_bot/calibrate.py` | OCR / template matchers   |
| Local dev tooling    | `uv` lockfile          | Active         | `pyproject.toml` / `uv.lock` | Optional `[bot]` extras      |

## At a Glance

1. `scraper.py` 가 외부 코드 소스를 가져와 `store.py` 에 저장합니다.
2. `auth.py` + `claim_api.py` 가 게임 측 API 로 일일 보상과 코드를 클레임합니다.
3. `redeemer.py` 가 결과를 `store.py` 에 반영하고 `notifier.py` 가 알림을 발송합니다.
4. `worker/` 가 외부에서 조회 가능한 읽기 전용 HTTP API 를 제공합니다.
5. `idle_outpost_bot/` 은 안드로이드 기기에서 동일한 일일 루틴을 자동화합니다.

운영자가 가장 자주 만지는 진입점은 `python main.py` (파이프라인) 와 `npx wrangler deploy` (Worker),
그리고 `python -m idle_outpost_bot` (봇) 입니다.

## Table of Contents

- [Package Contents](#package-contents)
- [Architecture](#architecture)
- [Quickstart](#quickstart)
- [Commands Reference](#commands-reference)
- [Configuration](#configuration)
- [Local Development](#local-development)
- [Testing](#testing)
- [Bot Calibration](#bot-calibration)
- [Maintainers](#maintainers)
- [License](#license)

## Package Contents

| Path                        | Role                                                                 |
| --------------------------- | -------------------------------------------------------------------- |
| `main.py`                   | 파이프라인 오케스트레이터 (스크랩 → 클레임 → 알림).                   |
| `scraper.py`                | 공개 코드 소스 파싱 (BeautifulSoup 기반).                            |
| `claim_api.py`              | 게임 측 일일 보상 / 코드 클레임 HTTP 호출.                           |
| `redeemer.py`               | 클레임 결과 검증 및 회수 처리.                                        |
| `auth.py`                   | 클레임 API 인증 토큰 발급/갱신.                                       |
| `store.py`                  | 코드/상태 영속화 추상화 (파일/메모리 백엔드).                         |
| `notifier.py`               | 결과 알림 (콘솔 / 확장 훅).                                           |
| `worker/src/index.ts`       | Cloudflare Worker HTTP 핸들러.                                       |
| `worker/wrangler.jsonc`     | Worker 배포 설정.                                                    |
| `idle_outpost_bot/`         | Appium 기반 안드로이드 자동화 패키지.                                 |
| `idle_outpost_bot/loop.py`  | 일일 루프 본체.                                                       |
| `idle_outpost_bot/driver.py`| Appium 드라이버 래퍼.                                                |
| `idle_outpost_bot/vision.py`| PaddleOCR + 템플릿 매칭 비전 파이프라인.                             |
| `idle_outpost_bot/calibrate.py` | 캘리브레이션 도구 (OCR/이미지 자산 등록).                         |
| `idle_outpost_bot/calibration/` | 화면별 OCR YAML 과 PNG 템플릿 자산.                               |
| `idle_outpost_bot/safety.py`| 안전 가드 (탭 횟수 제한, 무한 루프 차단).                            |
| `idle_outpost_bot/state.py` | 봇 상태 머신.                                                        |
| `idle_outpost_bot/notify.py`| 봇 알림 훅.                                                          |
| `idle_outpost_bot/i18n_ko.properties` | 한국어 OCR/UI 라벨.                                          |
| `pyproject.toml` / `uv.lock`| Python 의존성 잠금.                                                  |

## Architecture

세 컴포넌트는 같은 데이터 모델(코드 목록 + 일일 클레임 상태) 을 공유하지만 배포 표면이 다릅니다.

| Tier            | Where it runs         | Responsibility                                       | Talks to                  |
| --------------- | --------------------- | ---------------------------------------------------- | ------------------------- |
| Pipeline        | 로컬 / 스케줄러       | 스크랩 → 인증 → 클레임 → 저장 → 알림                 | 게임 API, 알림 훅         |
| Worker API      | Cloudflare Workers    | 외부 조회용 읽기 전용 HTTP                           | Pipeline 의 출력 저장소   |
| Android bot     | USB / Wi-Fi 디바이스  | 동일 일일 루틴을 UI 레벨에서 재현                     | 게임 클라이언트           |

### Request Flow (Pipeline)

1. `main.py` 가 스케줄러/수동 호출로 시작됩니다.
2. `scraper.py` 가 코드 소스에서 활성 코드를 추출해 `store.py` 에 기록합니다.
3. `auth.py` 가 만료된 토큰을 검사하고 필요 시 재발급합니다.
4. `claim_api.py` + `redeemer.py` 가 일일 보상과 코드를 게임 API 에 요청합니다.
5. `notifier.py` 가 성공/실패 요약을 발송합니다.

### Request Flow (Android Bot)

1. `python -m idle_outpost_bot` 이 `loop.py` 의 상태 머신을 시작합니다.
2. `driver.py` 가 Appium 세션을 열고 `safety.py` 가 동작 한도를 초기화합니다.
3. `vision.py` 가 PaddleOCR 과 `calibration/` 의 PNG/YAML 자산을 사용해 현재 화면을 판별합니다.
4. `actions.py` 가 화면별로 정의된 탭/스와이프/입력 시퀀스를 실행합니다.
5. `state.py` 가 다음 화면으로 전이하고 루프가 종료 조건을 만족할 때까지 반복합니다.

### Request Flow (Worker API)

1. `worker/src/index.ts` 가 HTTP 요청을 수신합니다.
2. 핸들러가 저장된 코드/상태를 조회해 JSON 으로 응답합니다.
3. 인증이 필요한 경로는 `wrangler.jsonc` 의 시크릿/바인딩을 사용합니다.

## Quickstart

### 1. 파이프라인 (Python CLI)

```bash
git clone <repository-url> idle-outpost-codes
cd idle-outpost-codes
uv sync
cp .env.example .env   # 실제 파일이 없으면 아래 Configuration 참고
uv run python main.py
```

### 2. Cloudflare Worker

```bash
cd worker
npm install
npx wrangler dev      # 로컬 개발
npx wrangler deploy   # 배포
```

### 3. Android Bot (선택)

```bash
uv sync --extra bot
python -m idle_outpost_bot
```

`[bot]` extras 는 무거운 의존성 (Appium, Selenium, PaddleOCR, PaddlePaddle, Pillow, numpy, pyyaml) 을
포함하므로, 파이프라인만 사용할 경우 설치하지 마세요.

## Commands Reference

| Command                                          | Where   | Purpose                                       |
| ------------------------------------------------ | ------- | --------------------------------------------- |
| `uv run python main.py`                          | root    | 1 회 파이프라인 실행 (스크랩 + 클레임 + 알림). |
| `uv run python -m idle_outpost_bot`              | root    | 안드로이드 봇 일일 루프 실행.                  |
| `uv run python -m idle_outpost_bot.calibrate`    | root    | 새 화면 캘리브레이션 자산 생성.                |
| `uv run python -m idle_outpost_bot.auto_calibrate` | root  | 캘리브레이션 자동 보정.                        |
| `uv run python -m idle_outpost_bot.discover`     | root    | 디바이스/앱 메타데이터 탐색.                   |
| `npx wrangler dev`                               | worker  | Worker 로컬 실행.                             |
| `npx wrangler deploy`                            | worker  | Worker 배포.                                  |
| `npm test`                                       | worker  | Worker 단위 테스트 (정의된 경우).             |
| `uv run ruff check .`                            | root    | 린트.                                          |
| `uv run basedpyright`                            | root    | 타입 검사.                                     |

## Configuration

### Python 파이프라인

`.env` (또는 환경 변수) 로 다음 키를 제공합니다. 실제 키 이름은 사용 중인 게임/알림 백엔드에 맞춰 조정하세요.

| Key                | Purpose                                          |
| ------------------ | ------------------------------------------------ |
| `GAME_AUTH_TOKEN`  | `auth.py` 가 사용하는 게임 API 토큰.             |
| `GAME_API_BASE`    | `claim_api.py` 의 엔드포인트 베이스 URL.         |
| `NOTIFY_WEBHOOK`   | `notifier.py` 의 알림 훅 (선택).                  |
| `STORE_BACKEND`    | `store.py` 백엔드 선택 (예: `file`, `memory`).   |
| `LOG_LEVEL`        | 로깅 레벨 (예: `INFO`, `DEBUG`).                 |

### Cloudflare Worker

`worker/wrangler.jsonc` 에서 다음을 확인하세요.

| Setting             | Purpose                                          |
| ------------------- | ------------------------------------------------ |
| `name`              | Worker 이름.                                     |
| `main`              | 엔트리 (`src/index.ts`).                         |
| `compatibility_date`| Workers 런타임 버전.                             |
| `vars`              | 비밀이 아닌 환경 변수.                           |
| `kv_namespaces`     | (선택) 코드/상태 저장소 바인딩.                   |
| `secrets`           | 인증 토큰 등 — `wrangler secret put` 으로 주입.  |

### Android Bot

캘리브레이션 자산은 `idle_outpost_bot/calibration/` 에 YAML + PNG 쌍으로 저장되며, `settings.py` 와
`config_loader.py` 가 이를 로드합니다. 화면 인식이 흔들리면 `calibrate.py` 로 자산을 재생성하세요.

| Asset                      | Purpose                                          |
| -------------------------- | ------------------------------------------------ |
| `*.png`                    | 템플릿 매칭용 기준 이미지.                       |
| `*.ocr.yaml`               | OCR 좌표/라벨 메타데이터.                         |
| `*.yaml` (대형 정의)       | 화면 단위 상태 정의 (`main_screen.yaml` 등).     |
| `i18n_ko.properties`       | 한국어 라벨. 다른 언어 추가 시 동일 키 사용.     |

## Local Development

- Python: [`uv`](https://docs.astral.sh/uv/) 로 `uv sync` → `uv run python main.py`.
- Worker: `cd worker && npm install && npx wrangler dev`.
- 봇: Appium 서버가 로컬에서 동작 중이어야 하며, ADB 로 디바이스가 연결되어 있어야 합니다.
- 가상환경은 `.venv` (basedpyright 의 `venv` 설정과 일치) 를 권장합니다.

### 코드 스타일

- Ruff: line-length 100, target Python 3.11 (`pyproject.toml` 참고).
- 타입 검사: basedpyright (`pyproject.toml` 의 `[tool.basedpyright]` 섹션).

## Testing

현재 저장소에는 별도 테스트 디렉터리가 포함되어 있지 않습니다. 권장 절차:

1. `scraper.py` 파싱 로직 — 샘플 HTML/JSON 픽스처로 단위 테스트.
2. `claim_api.py` / `redeemer.py` — 게임 API 응답 모킹으로 단위 테스트.
3. `worker/src/index.ts` — `npm test` 또는 `vitest` 추가.
4. `idle_outpost_bot/vision.py` — 캘리브레이션 자산 변경 시 회귀 테스트.

## Bot Calibration

게임 클라이언트 UI 가 바뀌면 비전 파이프라인이 실패합니다. 이 경우:

1. 새 화면의 스크린샷을 `idle_outpost_bot/calibration/<screen>.png` 로 저장합니다.
2. `python -m idle_outpost_bot.calibrate` 으로 OCR 좌표 메타데이터를 생성합니다.
3. `actions.py` 에 해당 화면의 시퀀스를 추가합니다.
4. `safety.py` 의 한도 (탭 횟수, 최대 루프) 가 새 화면에 맞는지 확인합니다.

자세한 절차는 `idle_outpost_bot/CALIBRATION_FULL.md` 와 `JADX_FULL_INVENTORY.md` 를 참고하세요.

## Maintainers

| Area                | Contact                                              |
| ------------------- | ---------------------------------------------------- |
| 파이프라인 / Worker | 저장소 소유자 (GitHub 이슈 트래커).                  |
| Android 봇          | `idle_outpost_bot/AUTOMATION_TARGETS.md` 참고.       |
| 게임 API 변경       | `idle_outpost_bot/API_RESEARCH.md` 참고.             |

상세 문서 위치:

- `idle_outpost_bot/AD_REWARDS.md` — 광고 보상 흐름.
- `idle_outpost_bot/API_RESEARCH.md` — 게임 API 분석 노트.
- `idle_outpost_bot/AUTOMATION_TARGETS.md` — 자동화 대상 화면.
- `idle_outpost_bot/CALIBRATION_FULL.md` — 캘리브레이션 전체 절차.
- `idle_outpost_bot/JADX_FULL_INVENTORY.md` — APK 디컴파일 인벤토리.
- `worker/README.md` — Worker 운영 노트.
- `CONTRIBUTING.md` — 기여 절차.

## License

이 저장소는 `LICENSE` 파일에 명시된 라이선스를 따릅니다.