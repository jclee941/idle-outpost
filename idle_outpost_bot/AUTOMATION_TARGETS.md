# Idle Outpost 자동화 요소 종합 (실측 + jadx 기반)

생성: 실제 폰 Samsung A35 (1080x2340) + base.apk jadx 분석.

## 게임 구조 요약

- **장르**: Idle business sim (Trade) + Idle RPG (Fight) + LTE 이벤트
- **133개 in-game manager 클래스** + **수백 개 dialog**
- **이미 게임이 자동화한 시스템** (봇이 추가 작업 불필요):
  - `AutoLooter` — Fight Mode 자동 loot
  - `FarmAutoWorkManager`, `FarmAFKManager` — 농장/AFK
  - `MorningResetManager` — 일일 리셋

→ 봇의 역할 = **메뉴 진입 + 다이얼로그 dismiss + claim 버튼 탭**.

## 자동화 우선순위 (실측 좌표)

| Pri | 액션 | 좌표 (center) | 빈도 | 위험 |
|-----|------|---------------|------|------|
| 1 | **Inbox/메일 claim** | (860, 135) | 1회/일 | 안전 |
| 2 | **Daily Streak claim** | 좌측 캘린더 (75, 348) | 1회/일 | 안전 |
| 3 | **Tasks claim** | 좌측 체크리스트 (75, 636) | 4시간 | 안전 |
| 4 | **Wheel/룰렛** (`!` 알림) | 좌측 휠 (75, 491) | 8시간 | 안전 |
| 5 | **Quest board** (`!` 알림) | 좌측 지도 (75, 780) | 시간당 | 안전 |
| 6 | **Ad TV reward** (1h42m 쿨) | 좌측 TV (77, 1242) | 1.5h | 광고 시청 |
| 7 | **Cards/카드 팩** | 좌측 cards (75, 936) | 비정기 | 안전 |
| 8 | **이벤트 진입** | 상단 banner (548, 365) | 이벤트 기간 | 안전 |
| 9 | **Trade Mode 진입** | 거래 (316, 1890) | 시작 시 | 안전 |
| 10 | **Fight Mode 진입** | 전투 (760, 1890) | 시작 시 | 안전 |
| 11 | **우측 이벤트 캐릭터** | (993, 316) | 비정기 | 결제 페이지 가능 |
| 12 | **Trophy/리더보드** | (1005, 522) | 시즌 종료 | 안전 |

## 화면 영역 매핑 (1080x2340)

```
y=0    ┌──────────────────────────────────────┐
       │ [👤avatar 72,158][name][💎82 480,133]│
       │ [🔥flame 265,205] [📧860][i951][≡1030]│
y=170  ├──────────────────────────────────────┤
       │   ┌──────────────────────────────┐    │
       │   │ 🏆 Cornfield Dream  548,365 │    │ <- LTE event banner
y=505  │   └──────────────────────────────┘    │
       ├──┐                              ┌─────┤
       │📅│  Calendar 75,348             │ 🐰  │ Right event 993,316
       │🎰!│ Wheel 75,491 (notif!)       │ 🏆  │ Trophy 1005,522
       │✅│  Tasks 75,636                │ 📜  │ Pass 1004,701
       │🗺!│ Quest 75,780 (notif!)       │     │
y=1300 │🎴│  Cards 75,936                │     │
       │🐷│  Piggy 75,1078 (구매주의!)   │     │
       │📺│  Ad TV 77,1242 (1h42m cool) │     │
       └──┘                              └─────┘
       │              [character on scene]      │
y=1772 ├──────────────────────────────────────┤
       │  ┌─────거래────┐    ┌─────전투───┐    │
       │  │  316,1890   │    │  760,1890  │    │ <- Bottom action
y=2008 │  │ 해변6-3     │    │ 겨울숲5-2  │    │
       │  └─────────────┘    └────────────┘    │
y=2030 │💬 chat 44,2054                        │
y=2150 ├──────────────────────────────────────┤
       │ [🎯94][🔧296][🏠541][🛡788][🛒985]   │ <- Bottom nav
y=2320 └──────────────────────────────────────┘
```

## 발견된 게임 백엔드 (참고용 - API 우회 불가)

17개 마이크로서비스 (`*.svc.rockbitegames.com`):

| 서비스 | URL | 인증 |
|---|---|---|
| auth | `/api/auth/login` | App Check 필요 |
| outpost | `/api/...` | App Check 필요 |
| ud (user data) | `/api/userdata/save` | App Check 필요 |
| rc (remote config) | `/api/remote-configs` | **공개 (App Check 면제)** ✅ |
| gameauth_health | `/api/health/liveness` | **공개** ✅ |

**API 자동화 불가**: 모든 상태 변경 endpoint = Firebase Play Integrity App Check 토큰 필수.

## 위험 영역 — 봇이 절대 누르지 말 것

| 영역 | 결과 |
|------|------|
| **Hamburger menu (1030, 131) → Server Switch** | 진행도 영구 리셋 |
| **Piggy bank (75, 1078)** | 실제 결제 |
| **Cart/shop (985, 2238)** | 결제 페이지 |
| **이벤트 banner Power Pack** | 결제 가능 |
| **우측 이벤트 (993, 316)** | 결제 가능 |

## 봇 sequence (한 사이클)

```
1. 게임 실행 → 로딩 대기 (region 자동 선택)
2. 메인 화면 인식 (거래/전투 버튼 OCR로 확인)
3. dismiss popups: 일일 streak dialog → claim
4. inbox 메일 (860, 135) → claim all → close
5. daily 캘린더 (75, 348) → claim → close
6. tasks (75, 636) → claim_all → close
7. wheel (75, 491) → spin if 무료 → close
8. quest (75, 780) → claim → close
9. ad TV (77, 1242) → 시청 가능 시 → 광고 → claim → close
10. (선택) Trade Mode → 스테이션 자동 업그레이드 (게임 자체 자동화 의존)
11. (선택) Fight Mode → AutoLooter 의존
12. 30분 sleep → 반복
```

## 다음 단계

`screens.yaml`에 위 좌표를 detect_text + buttons로 채워서 dry-run.
