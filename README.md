# idle-outpost-codes

[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](#quickstart)
[![Worker](https://img.shields.io/badge/worker-cloudflare-orange)](#worker)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](#license)

Idle Outpost 게임의 **프로모 코드 모니터링**, **일일 보상 수령 CLI**, **Android 자동화 봇**을 한 곳에서 제공하는 프로젝트입니다. Python 패키지로 웹 스크레이퍼와 API 클라이언트를, Cloudflare Worker로 알림 디스패처를, Appium/Selenium 기반 봇으로 게임 내 일상 임무를 자동화합니다.

This repository bundles a promo-code monitor, a daily-claim CLI, a Cloudflare notification Worker, and an Android automation bot for the *Idle Outpost* game.

## 한눈에 보기 / At a glance

| 항목 / Item | 값 / Value |
| --- | --- |
| 언어 / Language | Python 3.11+ (메인), TypeScript (Worker) |
| 진입점 / Entry points | `python main.py`, `python -m idle_outpost_bot`, `wrangler dev` |
| 핵심 산출물 / Artifacts | 코드 목록, 일일 보상, 알림 메시지 |
| 배포 대상 / Deploy targets | 로컬 CLI, Cloudflare Worker, Android 디바이스(USB 디버깅) |
| 상태 / Status | 개인 자동화 도구 / personal automation tool |
| 라이선스 / License | 저장소 `LICENSE` 참조 / see `LICENSE` |

## 처리 흐름 / End-to-end flow

1. `scraper.py` 가 게임 공지/리딤 페이지를 폴링하여 새 프로모 코드를 감지합니다.
2. `store.py` 가 코드 이력과 마지막 실행 상태를 로컬에 보관합니다.
3. `auth.py` → `claim_api.py` → `redeemer.py` 가 게임 API에 인증 후 보상을 수령합니다.
4. `notifier.py` 가 결과를 Cloudflare Worker `worker/` 로 전송합니다.
5. Worker가 디스코드/텔레그램 등 외부 채널로 알림을 디스패치합니다.
6. (선택) `idle_outpost_bot/` 의 안드로이드 봇이 OCR + UI 자동화로 일상 임무를 수행합니다.

## 패키지 구성 / Package contents

### 루트 Python 모듈 / Root Python modules

| 파일 / File | 역할 / Role |
| --- | --- |
| `main.py` | 일일 수령 + 코드 모니터링 CLI 진입점 |
| `scraper.py` | 외부 페이지에서 프로모 코드 스크레이핑 |
| `auth.py` | 게임 계정 인증/세션 유지 |
| `claim_api.py` | 일일 보상 API 호출 래퍼 |
| `redeemer.py` | 코드 입력/등록 비즈니스 로직 |
| `store.py` | 코드/실행 이력 로컬 저장소 |
| `notifier.py` | 외부 알림 채널 어댑터 |

### 서브 프로젝트 / Sub-projects

| 경로 / Path | 설명 / Description |
| --- | --- |
| `worker/` | Cloudflare Worker (TypeScript). 알림 수신·디스패치. |
| `idle_outpost_bot/` | Android 자동화 봇. Appium + PaddleOCR 기반. |
| `idle_outpost_bot/calibration/` | 화면 캡처·OCR 좌표 정의 YAML/PNG 자산. |

## 빠른 시작 / Quickstart

### 1. Python 환경 / Python environment

```bash
# uv 권장 / uv recommended
uv sync
cp .env.example .env  # 필요 시 / if available
```

`.env` 예시 키 / example keys:

- `IDLE_OUTPOST_USER`, `IDLE_OUTPOST_PASS`
- `IDLE_OUTPOST_DEVICE_ID`
- `NOTIFY_WEBHOOK_URL` (Worker 엔드포인트)

### 2. 코드 모니터 + 일일 수령 / Monitor + daily claim

```bash
# 새 코드 스캔 / scan codes
python main.py scan

# 일일 보상 수령 / claim daily reward
python main.py claim

# 전체 파이프라인 / full pipeline
python main.py run
```

### 3. Cloudflare Worker / Notification Worker

```bash
cd worker
npm install
npx wrangler dev          # 로컬 개발
npx wrangler deploy       # 배포 / deploy
```

자세한 옵션은 `worker/README.md` 를 참조하세요. See `worker/README.md` for details.

### 4. Android 자동화 봇 / Android automation bot (선택)

```bash
uv sync --extra bot
# USB 디버깅 활성화 + Appium 서버 기동 후:
python -m idle_outpost_bot calibrate   # 좌표 캘리브레이션
python -m idle_outpost_bot run         # 일상 루프 실행
```

봇 사용 전 `idle_outpost_bot/AUTOMATION_TARGETS.md` 와 `JADX_FULL_INVENTORY.md` 를 먼저 읽어 주세요. 게임 클라이언트 변경 시 좌표 재캘리브레이션이 필요할 수 있습니다.

## 명령어 요약 / Command reference

| 명령 / Command | 설명 / Description |
| --- | --- |
| `python main.py scan` | 코드 페이지 스크레이핑 |
| `python main.py claim` | 일일 보상 수령 |
| `python main.py run` | scan + claim + notify 전체 실행 |
| `python -m idle_outpost_bot run` | Android 일상 임무 자동화 |
| `python -m idle_outpost_bot calibrate` | 화면 좌표 캘리브레이션 |
| `python -m idle_outpost_bot auto_calibrate` | 자동 캘리브레이션 시도 |
| `npx wrangler dev` | Worker 로컬 실행 |

## 운영 메모 / Operations notes

- 게임 서버 변경으로 API 스키마가 바뀌면 `claim_api.py` 와 `redeemer.py` 가 즉시 영향을 받습니다.
- 캘리브레이션 PNG/YAML 자산은 디바이스 해상도와 안드로이드 버전에 종속됩니다. 변경 시 `idle_outpost_bot/calibration/` 의 해당 PNG 와 `.yaml` 을 함께 갱신하세요.
- 알림 엔드포인트는 공개 노출을 피하고 Worker 시크릿을 사용하세요. `worker/wrangler.jsonc` 의 `vars` / `secrets` 설정을 확인하세요.
- 자동화 봇은 교육/개인 용도입니다. 이용약관 준수는 사용자의 책임입니다.

## 추가 문서 / Further documentation

| 문서 / Document | 주제 / Topic |
| --- | --- |
| `worker/README.md` | Cloudflare Worker 설정 |
| `idle_outpost_bot/README.md` | Android 봇 사용법 |
| `idle_outpost_bot/AD_REWARDS.md` | 광고 보상 동작 정리 |
| `idle_outpost_bot/API_RESEARCH.md` | 게임 API 리서치 노트 |
| `idle_outpost_bot/AUTOMATION_TARGETS.md` | 자동화 대상 화면 목록 |
| `idle_outpost_bot/CALIBRATION_FULL.md` | 캘리브레이션 절차 |
| `idle_outpost_bot/JADX_FULL_INVENTORY.md` | APK 디컴파일 인벤토리 |
| `CONTRIBUTING.md` | 기여 가이드 |

## 기여 / Contributing

이슈와 PR 환영합니다. 게임 API 변경, 캘리브레이션 자산 추가, 새 알림 채널(텔레그램/슬랙 등) 어댑터가 특히 유용합니다. 큰 변경 전 `CONTRIBUTING.md` 를 읽어 주세요.

## 도움 받기 / Getting help

- 동작/오류 재현: GitHub 이슈를 열고 로그, 디바이스 모델, OS 버전을 첨부해 주세요.
- 보안 관련: 공개 이슈 대신 메인테이너에게 비공개로 연락하세요.

## 메인테이너 / Maintainers

저장소 오너가 직접 유지보수합니다. 자세한 연락처는 저장소 메타데이터를 참조하세요. / Maintained by the repository owner; see repo metadata for contact.

## License

`LICENSE` 파일을 참조하세요. / See the `LICENSE` file.