# Idle Outpost Codes

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](pyproject.toml)
[![License: MIT](LICENSE)](LICENSE)

## 요약

`idle-outpost-codes`는 모바일 게임 *Idle Outpost*를 위한 통합 도구 묶음입니다.
**프로모션 코드 모니터링**, **일일 보상 자동 수령 CLI**, **Android 자동화 봇**을 한 패키지로 제공합니다.

- 외부 소스에서 새 코드를 수집해 로컬에 안전하게 저장합니다.
- Cloudflare Worker 기반 클레임 API로 코드를 멱등하게 등록·조회합니다.
- 디바이스에서 PaddleOCR과 Appium으로 일일 퀘스트·광고를 자동 클리어합니다.

운영자가 가장 자주 사용하는 진입점은 두 가지입니다.

- `python main.py` — 코드 스크랩·저장·알림·리딤
- `python -m idle_outpost_bot` — 디바이스 자동화

## 상태

| 구성 요소 | 진입점 | 상태 | 비고 |
|---|---|---|---|
| CLI / 스크레이퍼 | `main.py` | 동작 | httpx + BeautifulSoup |
| 로컬 저장소 | `store.py` | 동작 | 중복 제거 포함 |
| 클레임 API 클라이언트 | `claim_api.py` | 동작 | Worker 호출 |
| Worker 백엔드 | `worker/src/index.ts` | 동작 | Cloudflare Workers |
| 리디머 | `redeemer.py` | 동작 | 게임 측 API 연동 |
| 알림 | `notifier.py` | 동작 | 신규 코드 푸시 |
| Android 봇 | `idle_outpost_bot/__main__.py` | 캘리브레이션 필요 | PaddleOCR + Appium |

## 동작 흐름 요약

1. `scraper.py`가 등록된 소스에서 새 코드를 수집합니다.
2. `store.py`가 중복 없이 저장하고 변경분을 `notifier.py`로 통지합니다.
3. `redeemer.py`가 게임 측 클레임 엔드포인트를 호출해 실제 보상을 수령합니다.
4. `claim_api.py`는 Worker(`worker/src/index.ts`)에 등록/조회 요청을 보냅니다.
5. 디바이스 자동화가 필요하면 `idle_outpost_bot.loop`이 일일 퀘스트·광고를 수행합니다.
6. `safety.py`가 휴면·쿨다운·이상 화면을 감지해 무한 루프를 차단합니다.

## 목차

- [패키지 구성](#패키지-구성)
- [먼저 읽을 파일](#먼저-읽을-파일)
- [API / 진입점](#api--진입점)
- [빠른 시작](#빠른-시작)
- [설정](#설정)
- [명령어](#명령어)
- [워커](#워커)
- [로컬 개발](#로컬-개발)
- [테스트](#테스트)
- [기여](#기여)
- [유지보수 / 문의](#유지보수--문의)
- [추가 문서](#추가-문서)
- [라이선스](#라이선스)

## 패키지 구성

루트 모듈 (Python)

- `main.py` — CLI 진입점
- `scraper.py` — 외부 소스에서 코드 수집
- `store.py` — 로컬 영속 저장소 (중복 방지)
- `auth.py` — 클레임 API 인증 헬퍼
- `claim_api.py` — Worker 클레임 API 클라이언트
- `redeemer.py` — 게임 측 리딤 호출
- `notifier.py` — 신규 코드 알림 채널
- `pyproject.toml`, `uv.lock` — 의존성·락파일
- `video1.png` — 데모 스크린샷

워커 (`worker/`, Cloudflare Workers + TypeScript)

- `src/index.ts` — Worker 핸들러 (`fetch`)
- `wrangler.jsonc` — 배포 설정
- `package.json`, `tsconfig.json`, `package-lock.json` — 빌드 메타데이터
- `README.md` — 워커 전용 가이드

봇 (`idle_outpost_bot/`)

- `__main__.py` — 봇 모듈 진입점
- `driver.py` — Appium 기반 Android 드라이버
- `vision.py` — PaddleOCR 기반 화면 인식
- `actions.py` — 탭·스와이프 등 UI 액션
- `loop.py` — 자동화 메인 루프
- `safety.py` — 이상 상태 감지 및 쿨다운
- `state.py` — 세션·플래그 상태 관리
- `notify.py` — 봇 알림
- `settings.py`, `config_loader.py` — 설정 로더
- `discover.py` — UI 요소 자동 디스커버리
- `calibrate.py`, `auto_calibrate.py` — 캘리브레이션 도구
- `calibration/` — OCR 레퍼런스 이미지와 YAML
- `i18n_ko.properties` — 한국어 리소스
- `README.md` — 봇 전용 가이드
- `AD_REWARDS.md`, `API_RESEARCH.md`, `AUTOMATION_TARGETS.md`,
  `CALIBRATION_FULL.md`, `JADX_FULL_INVENTORY.md` — 운영·리서치 노트

## 먼저 읽을 파일

1. `main.py` — CLI 흐름 한눈에 파악
2. `scraper.py` → `store.py` → `redeemer.py` — 코드 라이프사이클
3. `worker/src/index.ts` — 클레임 API 동작
4. `idle_outpost_bot/loop.py` — 자동화 메인 루프
5. `idle_outpost_bot/safety.py` — 안전 정책과 휴면 로직
6. `idle_outpost_bot/vision.py` — OCR 파이프라인

## API / 진입점

| 진입점 | 종류 | 위치 |
|---|---|---|
| CLI 메인 | Python | `python main.py` |
| 봇 메인 | Python | `python -m idle_outpost_bot` |
| Worker 핸들러 | HTTP | `worker/src/index.ts` (`fetch`) |
| 캘리브레이션 | Python | `python -m idle_outpost_bot calibrate` |

Worker는 보통 `POST /claim`, `GET /codes` 같은 JSON 엔드포인트를 노출합니다. 정확한 라우팅은 `worker/src/index.ts`에서 확인하세요.

## 빠른 시작

요구 사항: Python 3.11+, `uv`. 워커 사용 시 Node.js 18+. 봇 사용 시 Android 디바이스와 Appium 서버.

```bash
# 의존성 설치 (봇 옵션 포함)
uv sync --extra bot

# CLI 도움말
python main.py --help

# 봇 실행
python -m idle_outpost_bot
```

`.env`는 저장소 루트에 둡니다.

## 설정

| 변수 | 용도 | 필수 여부 |
|---|---|---|
| `CLAIM_API_BASE` | Worker 클레임 API 베이스 URL | 선택 |
| `CLAIM_API_TOKEN` | Worker 인증 토큰 | 선택 |
| `NOTIFY_TARGET` | 신규 코드 알림 대상 (URL·채널) | 선택 |
| `SCRAPER_SOURCES` | 스크랩 소스 화이트리스트 (콤마 구분) | 선택 |
| `DEVICE_UDID` | Appium 타깃 디바이스 식별자 | 봇 사용 시 |
| `APP_PACKAGE` | 자동화 대상 앱 패키지명 | 봇 사용 시 |

`worker/wrangler.jsonc`에는 KV 네임스페이스, 비밀 키, 트리거를 설정합니다.

## 명령어

| 명령 | 설명 |
|---|---|
| `python main.py scrape` | 외부 소스에서 코드 수집 |
| `python main.py redeem <CODE>` | 코드 1회 리딤 |
| `python main.py notify` | 알림 채널에 큐 푸시 |
| `python -m idle_outpost_bot run` | 자동화 루프 실행 |
| `python -m idle_outpost_bot calibrate <name>` | 캘리브레이션 실행 |
| `python -m idle_outpost_bot auto-calibrate` | 자동 캘리브레이션 |
| `cd worker && npx wrangler dev` | Worker 로컬 실행 |
| `cd worker && npx wrangler deploy` | Worker 배포 |

## 워커

Cloudflare Worker 기반 클레임 API 백엔드입니다. 멱등한 코드 등록과 조회를 제공합니다.

```bash
cd worker
npm install
npx wrangler dev    # 로컬
npx wrangler deploy # 배포
```

## 로컬 개발

- 패키지 매니저: `uv`
- 포맷터·린터: `ruff` (`pyproject.toml` `[tool.ruff]`, line-length 100)
- 타입 검사: `basedpyright` (`.venv` 사용)
- 가상 환경: `.venv/` (저장소 외부 권장)

```bash
uv sync --extra bot
uv run ruff check .
uv run basedpyright
```

## 테스트

자동 테스트는 아직 저장소에 포함되어 있지 않습니다. 로컬 검증 절차는 다음과 같습니다.

- `python main.py scrape --dry-run` — 스크레이퍼 동작 확인
- `python -m idle_outpost_bot calibrate` — OCR 레퍼런스 점검
- `python -m idle_outpost_bot run --once` — 디바이스 1회 실행

## 기여

[CONTRIBUTING.md](CONTRIBUTING.md) 참고. PR 전 `ruff check .`와 `basedpyright`를 통과해 주세요.

## 유지보수 / 문의

- 저장소 maintainer 팀이 운영합니다.
- 이슈는 저장소 Issues 탭에서 접수하세요.
- 운영·리서치 노트는 `idle_outpost_bot/AD_REWARDS.md`, `idle_outpost_bot/API_RESEARCH.md`,
  `idle_outpost_bot/AUTOMATION_TARGETS.md`, `idle_outpost_bot/CALIBRATION_FULL.md`,
  `idle_outpost_bot/JADX_FULL_INVENTORY.md`에서 확인하세요.

## 추가 문서

- 워커 가이드: [worker/README.md](worker/README.md)
- 봇 가이드: [idle_outpost_bot/README.md](idle_outpost_bot/README.md)
- 기여 가이드: [CONTRIBUTING.md](CONTRIBUTING.md)
- 라이선스: [LICENSE](LICENSE)

## 라이선스

[MIT](LICENSE)

## English Summary

`idle-outpost-codes` bundles three coordinated tools for the mobile game *Idle Outpost*: a promo-code scraper, a daily-claim CLI backed by a Cloudflare Worker, and an Android automation bot. Operators usually run `python main.py` for the code lifecycle and `python -m idle_outpost_bot` for on-device automation. The bot relies on PaddleOCR + Appium for vision-driven UI actions, with safety guards and per-screen calibration assets under `idle_outpost_bot/calibration/`. Entry points to read first: `main.py`, `worker/src/index.ts`, and `idle_outpost_bot/loop.py`. See [CONTRIBUTING.md](CONTRIBUTING.md) and [LICENSE](LICENSE).