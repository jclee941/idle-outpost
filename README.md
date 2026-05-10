```markdown
# idle-outpost-codes

> Idle Outpost 프로모션 코드 모니터링, 일일 보상 CLI 청구, Android 게임 자동화 봇

## 소개

이 프로젝트는 모바일 게임 **Idle Outpost**의 프로모션 코드를 자동으로 수집·모니터링하고, 게임 내 일일 보상을 API 또는 Android 자동화를 통해 청구하는 통합 도구입니다.  
웹 스크래핑, API 연동, 그리고 Appium + PaddleOCR 기반 안드로이드 봇을 하나의 저장소에서 관리합니다.

## 주요 기능

- **프로모션 코드 모니터링**: 웹사이트에서 최신 게임 코드를 스크래핑하고 변경 사항을 감지합니다.
- **자동 보상 청구**: `claim_api` 및 `redeemer`를 통해 코드를 자동으로 등록하고 보상을 수령합니다.
- **알림 시스템**: 새 코드 발생 또는 청구 결과를 외부 웹훅 등으로 알립니다.
- **Android 게임 자동화 봇** (`idle_outpost_bot/`):
  - Appium 기반 디바이스 제어
  - PaddleOCR 템플릿 매칭으로 게임 화면 인식
  - YAML 기반 캘리브레이션으로 UI 요소 자동 탐지 및 터치 수행
- **확장 가능한 태스크 시스템**: `tasks/` 디렉터리 기반으로 봇 동작을 모듈화합니다.

## 설치

### 요구사항

- Python >= 3.11
- (선택) Android 자동화 사용 시: Appium Server, Android Emulator 또는 실제 기기
- (선택) OCR 기능 사용 시: PaddleOCR 관련 시스템 의존성

### 패키지 설치

```bash
# 저장소 클론
git clone https://github.com/jclee941/idle-outpost.git
cd idle-outpost

# 가상 환경 생성 (권장)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 기본 CLI 도구 설치
pip install -e .

# Android 자동화 봇 포함 설치
pip install -e ".[bot]"
```

> `uv`를 사용하는 경우: `uv sync` 또는 `uv sync --extra bot`

## 사용 방법

### 1. 프로모션 코드 모니터링 및 청구 (CLI)

```bash
# 메인 CLI 실행
python main.py

# 개별 모듈 실행 예시
python scraper.py       # 최신 코드 수집
python claim_api.py     # API 보상 청구
python notifier.py      # 알림 테스트
```

### 2. Android 자동화 봇

```bash
# 봇 모듈 실행
python -m idle_outpost_bot
```

> 자세한 봇 설정, 디바이스 연결 및 캘리브레이션 방법은 `idle_outpost_bot/README.md`와 `idle_outpost_bot/scripts/` 문서를 참고하세요.

## 프로젝트 구조

```
idle-outpost-codes/
├── main.py                  # CLI 진입점
├── scraper.py               # 웹 코드 스크래핑
├── claim_api.py             # 보상 청구 API 클라이언트
├── redeemer.py              # 코드 등록/교환 로직
├── notifier.py              # 알림 발송
├── auth.py                  # 인증 처리
├── store.py                 # 상태/데이터 저장
├── pyproject.toml           # 프로젝트 의존성
├── idle_outpost_bot/        # Android 게임 자동화 봇
│   ├── driver.py            # Appium 드라이버 제어
│   ├── vision.py            # OCR 기반 화면 인식
│   ├── actions.py           # UI 자동화 액션
│   ├── calibrate.py         # 화면 캘리브레이션
│   ├── tasks/               # 자동화 태스크 모듈
│   ├── calibration/         # OCR 템플릿 및 화면 설정
│   └── config/              # 화면 정의 YAML
└── _bot-scripts/            # GitHub 봇/에이전트 자동화 스크립트
    ├── scripts/             # PR 리뷰 러너 등
    └── Dockerfile.*         # GitHub Actions/App 컨테이너
```

## 기여하기

버그 리포트, 기능 제안, Pull Request 모두 환영합니다.  
자세한 기여 가이드는 [CONTRIBUTING.md](CONTRIBUTING.md)를 참고해 주세요.

## 라이선스

이 프로젝트는 [MIT 라이선스](LICENSE) 하에 배포됩니다.
```