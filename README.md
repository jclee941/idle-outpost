# idle-outpost-codes

![Python](https://img.shields.io/badge/python-3.11%2B-3776AB)
![Status](https://img.shields.io/badge/status-experimental-yellow)
[![License](https://img.shields.io/badge/license-see%20LICENSE-blue)](LICENSE)

## 한 줄 요약

Idle Outpost 게임의 프로모션 코드를 모니터링하고 일일 보상을 자동 수령하는 Python 도구 모음과, Android UI 자동화 봇, Cloudflare Worker 알림 게이트웨이를 한 저장소에서 관리하는 프로젝트.

## Overview

`idle-outpost-codes`는 세 가지 책임으로 나뉘는 컴포지트 워크스페이스입니다.

| 책임 | 구성 요소 | 언어 / 런타임 |
| --- | --- | --- |
| 프로모션 코드 수집 | `scraper.py` | Python 3.11+ |
| 일일 보상 / 코드 클레임 | `main.py`, `claim_api.py`, `redeemer.py`, `auth.py`, `store.py`, `notifier.py` | Python 3.11+ |
| Android 게임 자동화 | `idle_outpost_bot/` 패키지 | Python + Appium + PaddleOCR |
| 알림 / 스케줄 게이트웨이 | `worker/` | TypeScript / Cloudflare Workers |

`pyproject.toml`의 `description`은 이 저장소를 "Idle Outpost promo code monitor + daily claim CLI + Android automation bot"으로 정의합니다. 이름에 `monorepo`라는 단어를 사용하지는 않지만, 실제로는 위 네 가지 책임이 공존하는 다중-언어 워크스페이스입니다.

## 빠른 상태

| 항목 | 값 |
| --- | --- |
| PyPI 이름 | `idle-outpost-codes` |
| 버전 | `0.1.0` |
| Python | `>=3.11` |
| 의존성 | `beautifulsoup4`, `httpx`, `python-dotenv`, `scipy` |
| 선택 의존성 `[bot]` | `Appium-Python-Client`, `selenium`, `paddleocr`, `paddlepaddle`, `Pillow`, `numpy`, `pyyaml` |
| 린터 | `ruff` (line-length 100, target py311) |
| 타입 검사 | `basedpyright` (`.venv`) |
| Android 자동화 | Appium + Selenium + PaddleOCR 기반 OCR |
| 알림 게이트웨이 | Cloudflare Worker (`worker/src/index.ts`) |
| 보조 산출물 | UI 보정용 스크린샷 + OCR YAML (`idle_outpost_bot/calibration/`) |

## 구성 요소 흐름

1. `scraper.py`가 공개 소스에서 새 Idle Outpost 프로모션 코드를 수집합니다.
2. `auth.py`가 계정 자격증명을 안전하게 로드하고, `claim_api.py`가 게임 API로 코드를 전송합니다.
3. `redeemer.py`가 일일 보상 수령 흐름을 실행하고, `store.py`가 결과를 로컬에 기록합니다.
4. `notifier.py`가 Cloudflare Worker (`worker/src/index.ts`) 또는 다른 채널로 알림을 전달합니다.
5. `idle_outpost_bot/` 패키지는 선택적 Android 자동화 경로입니다. Appium 드라이버와 PaddleOCR로 화면 상태를 판독하고 캘리브레이션 자산과 비교해 액션을 결정합니다.

## Features

- **프로모션 코드 스크래퍼**: `httpx` + `beautifulsoup4` 기반의 HTTP 수집기 (`scraper.py`).
- **API 클레임 파이프라인**: 인증, 요청, 응답 처리, 로컬 저장을 분리한 모듈 구조 (`auth.py` / `claim_api.py` / `redeemer.py` / `store.py`).
- **알림 어댑터**: `notifier.py`와 Cloudflare Worker가 알림 게이트웨이를 구성.
- **Android 자동화 봇**: Appium + Selenium으로 디바이스를 구동하고, PaddleOCR + Pillow로 화면을 판독 (`idle_outpost_bot/driver.py`, `vision.py`).
- **캘리브레이션 시스템**: 화면 상태별 기준 이미지와 OCR 결과 YAML을 함께 보관 (`idle_outpost_bot/calibration/`).
- **한국어 로컬라이제이션**: `idle_outpost_bot/i18n_ko.properties`로 게임 UI 문자열을 매핑.
- **안전 모드**: `safety.py`가 위험 동작에 대한 가드를 제공.
- **리서치 노트**: `AD_REWARDS.md`, `API_RESEARCH.md`, `AUTOMATION_TARGETS.md`, `JADX_FULL_INVENTORY.md`, `CALIBRATION_FULL.md`에 정적 분석 결과를 누적.

## Repository Layout

| 경로 | 역할 |
| --- | --- |
| `main.py` | 일일 클레임 CLI 진입점 |
| `auth.py` | 자격증명 / 인증 헬퍼 |
| `claim_api.py` | 게임 API 클라이언트 |
| `redeemer.py` | 일일 보상 / 코드 사용 로직 |
| `scraper.py` | 프로모션 코드 수집기 |
| `store.py` | 로컬 결과 저장소 |
| `notifier.py` | 알림 발송 어댑터 |
| `pyproject.toml` | 패키지 메타데이터, 의존성, 린터 설정 |
| `uv.lock` | uv 잠금 파일 |
| `idle_outpost_bot/` | Android 자동화 봇 패키지 |
| `idle_outpost_bot/calibration/` | UI 캘리브레이션 이미지 / OCR YAML |
| `worker/` | Cloudflare Worker (TypeScript) |
| `worker/src/index.ts` | Worker 핸들러 |
| `worker/wrangler.jsonc` | Worker 배포 설정 |
| `LICENSE` / `CONTRIBUTING.md` | 라이선스 / 기여 정책 |

## Quickstart

### 1. Python 환경 준비

```bash
# uv 사용
uv sync

# 또는 표준 venv + pip
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

선택 의존성 그룹 `[bot]`은 Android 자동화에 필요합니다.

```bash
uv sync --extra bot
# 또는
pip install -e ".[bot]"
```

### 2. 환경 변수

`python-dotenv`을 통해 다음 변수를 로드합니다 (필수 변수는 사용자 환경에 맞춰 결정).

```env
# 예시 키 이름 (실제 키는 게임 / API 문서 또는 리서치 노트 참고)
IDLE_OUTPOST_AUTH_TOKEN=...
IDLE_OUTPOST_DEVICE_ID=...
# Worker 알림 게이트웨이를 사용할 경우
WORKER_NOTIFY_URL=...
```

### 3. 일일 클레임 실행

```bash
python main.py
# 또는 모듈로
python -m idle_outpost_bot
```

`main.py`는 `scraper → claim_api/redeemer → store → notifier` 순으로 일일 작업을 오케스트레이션하도록 설계된 진입점입니다.

### 4. Android 자동화 봇 (선택)

```bash
# Appium 서버가 별도로 떠 있어야 합니다.
python -m idle_outpost_bot
```

봇은 `idle_outpost_bot/calibration/`의 기준 이미지와 OCR YAML을 사용해 화면을 판독합니다. 새 화면이 추가되면 `auto_calibrate.py` / `calibrate.py`로 캘리브레이션을 갱신할 수 있습니다.

### 5. Cloudflare Worker (선택)

```bash
cd worker
npm install
npx wrangler dev      # 로컬 실행
npx wrangler deploy    # 배포
```

## Commands Reference

| 명령 | 위치 | 설명 |
| --- | --- | --- |
| `python main.py` | 루트 | 일일 프로모션 코드 / 보상 파이프라인 실행 |
| `python -m idle_outpost_bot` | 루트 | Android 자동화 봇 실행 |
| `python -m idle_outpost_bot.auto_calibrate` | 봇 | 캘리브레이션 자동 갱신 |
| `python -m idle_outpost_bot.calibrate` | 봇 | 캘리브레이션 수동 갱신 |
| `npx wrangler dev` | `worker/` | Cloudflare Worker 로컬 실행 |
| `npx wrangler deploy` | `worker/` | Cloudflare Worker 배포 |
| `ruff check .` | 루트 | 린트 (line-length 100) |
| `basedpyright` | 루트 | 타입 검사 (`.venv` 기준) |

## Configuration

- **Python 린트**: `pyproject.toml`의 `[tool.ruff]` (line-length 100, target py311).
- **타입 검사**: `[tool.basedpyright]`에서 `venvPath = "."`, `venv = ".venv"`을 가정.
- **봇 캘리브레이션**: `idle_outpost_bot/calibration/*.ocr.yaml`이 화면 상태별 OCR 임계값과 라벨을 정의.
- **한국어 UI 매핑**: `idle_outpost_bot/i18n_ko.properties`.
- **Worker**: `worker/wrangler.jsonc`에 배포 이름, 트리거, 바인딩이 정의됨.

## Local Development

1. `uv sync --extra bot`으로 전체 의존성 설치.
2. `.env`에 자격증명 작성 (저장소에는 커밋하지 않음).
3. 코드 변경 시 `ruff check .`과 `basedpyright`로 정적 검사를 함께 실행.
4. 새 화면을 자동화할 때는 `idle_outpost_bot/calibration/`에 기준 이미지를 추가하고 `auto_calibrate.py`로 YAML을 갱신.
5. Worker 변경 시 `npx wrangler dev`로 로컬에서 페이로드 형태를 확인한 뒤 `npx wrangler deploy`.

## Testing

이 저장소에는 별도 테스트 디렉터리가 선언되어 있지 않습니다. 검증 전략은 다음과 같습니다.

- **단위 검증**: 신규 모듈 추가 시 `pytest` 기반 테스트를 권장하며, CI 도입 시 `pyproject.toml`에 `[tool.pytest.ini_options]`를 추가할 수 있습니다.
- **정적 검사**: `ruff`, `basedpyright`로 회귀를 1차로 차단.
- **캘리브레이션 회귀**: `idle_outpost_bot/calibration/`의 OCR YAML과 이미지를 변경한 경우, `auto_calibrate.py`의 출력이 결정적(deterministic)인지 수동으로 확인.
- **Worker**: `npx wrangler dev`로 페이로드 회귀 확인.

## Status & Support

- 저장소는 **실험적(experimental)** 단계입니다. 게임 서버 변경 시 API 클레임 경로가 깨질 수 있으며, 디바이스/OS 변경 시 Android 자동화 캘리브레이션이 무효화될 수 있습니다.
- 외부 게임 API에 의존하므로 **운영 환경용 프로덕션 보장**은 제공되지 않습니다. 본 저장소는 연구 / 개인용 보조 도구로 다루는 것을 권장합니다.
- 자세한 리서치는 `idle_outpost_bot/` 하위의 `AD_REWARDS.md`, `API_RESEARCH.md`, `AUTOMATION_TARGETS.md`, `JADX_FULL_INVENTORY.md`, `CALIBRATION_FULL.md`를 참고하세요.
- 이슈 트래커와 디스커션은 저장소 소유자가 운영하는 GitHub Issues / Discussions를 사용합니다.

## Maintainers

- 저장소 소유자가 단일 관리자 역할입니다. 책임 영역은 다음과 같습니다.
  - `scraper.py`, `claim_api.py`, `redeemer.py`, `store.py`, `notifier.py` — 프로모션 코드 파이프라인.
  - `idle_outpost_bot/` — Android 자동화 및 캘리브레이션 자산.
  - `worker/` — 알림 / 스케줄 게이트웨이.

## Contributing

기여 절차는 `CONTRIBUTING.md`를 따릅니다. 큰 변경을 제안할 때는 다음을 함께 준비해 주세요.

1. 변경 모듈과 그 영향 범위 설명.
2. 새 캘리브레이션 이미지를 추가하는 경우 기준 화면 캡처 절차 명시.
3. 외부 게임 API 또는 광고 SDK에 의존하는 변경은 관련 리서치 노트 갱신.

## License

`LICENSE` 파일을 참고하세요. 저장소 표준 라이선스가 모든 하위 컴포넌트(`worker/` 포함)에 적용됩니다.

## Further Documentation

- `idle_outpost_bot/README.md` — Android 자동화 봇 상세.
- `idle_outpost_bot/AD_REWARDS.md` — 광고 보상 흐름 분석.
- `idle_outpost_bot/API_RESEARCH.md` — 게임 API 정적 분석.
- `idle_outpost_bot/AUTOMATION_TARGETS.md` — 자동화 후보 화면 목록.
- `idle_outpost_bot/CALIBRATION_FULL.md` — 캘리브레이션 절차 상세.
- `idle_outpost_bot/JADX_FULL_INVENTORY.md` — APK 디컴파일 결과 인벤토리.
- `worker/README.md` — Worker 세부 설정.

---

## English Summary

`idle-outpost-codes` is a multi-language workspace that combines a Python promo-code monitor, a daily claim CLI, an Android automation bot, and a Cloudflare Worker notification gateway for the game *Idle Outpost*.

| Component | Path | Role |
| --- | --- | --- |
| Scraper | `scraper.py` | Collects new promo codes from public sources |
| Claim pipeline | `main.py`, `auth.py`, `claim_api.py`, `redeemer.py`, `store.py`, `notifier.py` | Authenticates, claims codes, stores results, dispatches notifications |
| Android bot | `idle_outpost_bot/` | Appium + PaddleOCR driven UI automation with calibrated OCR references |
| Worker | `worker/` | Cloudflare Worker used as a notification / scheduling endpoint |

**Status:** experimental. The project relies on third-party game APIs and live UI screens, so it is not production-hardened. Use it as a personal / research aid and expect calibration work whenever the game client or backend changes.

**Getting started:** install with `uv sync --extra bot` (or `pip install -e ".[bot]"`), provide credentials through a `.env` file, then run `python main.py` for the daily claim pipeline or `python -m idle_outpost_bot` for the Android automation. Worker code is developed under `worker/` with `wrangler dev` / `wrangler deploy`.

**Maintenance:** see `CONTRIBUTING.md` for contribution policy and the `idle_outpost_bot/` research notes (`AD_REWARDS.md`, `API_RESEARCH.md`, `AUTOMATION_TARGETS.md`, `CALIBRATION_FULL.md`, `JADX_FULL_INVENTORY.md`) for technical background.