# Idle Outpost Full Calibration Report

**Generated:** 2026-04-27  
**Device:** 192.168.50.240:35641  
**Screen Size:** 1080x2340  
**User:** sexsexbo (Lv.74)

---

## Screen Matrix

### 1. main_screen (베이스라인)
- **진입 좌표:** N/A (Starting screen)
- **발견 텍스트:**
  - `sexsexbo` @ (username area)
  - `74` @ (level)
  - `28.6m` @ (coins)
  - `Cornfield Dream` @ (current zone)
  - `Win Exclusive Set!` @ (event banner)
  - `+412% P0WER` @ (power buff)
  - `#24` @ (rank)
  - `SURF`, `SHOT` @ (skills)
  - `거래` (Trade) / `전투` (Fight) @ bottom nav
  - `해변가 6-3` / `겨울 숲 5-2~10` @ zone info
  - `3/3`, `4/3` @ (resource caps)
  - `199`, `70` @ (resource amounts)
- **자동화 후보:**
  - `claim_tips` → tip collection button exists
  - `upgrade_stations` → multiple upgrade buttons in bottom bar
- **참고:** 메인 게임 화면, 하단 내비게이션에 거래/전투 버튼

---

### 2. event_screen (calendar 버튼 → events)
- **진입 좌표:** (75, 348)
- **실제 화면:** Event screen (not calendar)
- **발견 텍스트:**
  - `소버넌트 세트` (Sovereign Set)
  - `Get Exclusive Set!`
  - `+412% POWER`
  - `Next chance: 4 Months Away`
  - `13h 4m left`
  - `Event rewards`
  - `Cornfield Dream`
  - `퀴스트 러시` (Quest Rush) - `종료: 1h 1m`
  - `소방울 러시` (Fire alarm rush) - `종료: 1h 1m`
  - `옥수수밭 꿈` (Cornfield Dream)
- **자동화 후보:**
  - `claim_event_rewards` → event reward claim button
- **종료:** X 버튼 (1020, 130)

---

### 3. wheel ( Lucky Wheel - 행운의 바퀴)
- **진입 좌표:** (75, 491)
- **발견 텍스트:**
  - `행운의 바퀴` (Lucky Wheel)
  - `30`, `15`, `100` @ (spin costs/quantities)
  - `애니메이션` (Animation)
  - `건너뛰기` (Skip)
  - `돌리기` (Spin) @ main action button
  - `(3/3)` @ (spins remaining)
- **자동화 후보:**
  - `spin_wheel` → `돌리기` 버튼 탭 (3/3 spins available)
  - `skip_animation` → `건너뛰기` 버튼 탭
- **종료:** BACK 키

---

### 4. tasks_screen (임무)
- **진입 좌표:** (75, 636)
- **발견 텍스트:**
  - `임무` (Tasks)
  - `주간` (Weekly) rewards: 230, X120, X2, X3, 140, 280, 420, 560, 700
  - `일일` (Daily) rewards: 10, x50, X2, x1, 20, 40, 60, 80, 100
  - `일일 임무` (Daily Tasks)
  - `초기화까지:16h58m` (Reset in 16h58m)
  - Tasks with `+10` rewards:
    - `애완동물 달리기 3회 플레이` → `0/3`
    - `30전술 장비 뽑기` → `0/30`
    - `애완동물 30마리 뽑기` → `0/30`
    - `애완동물 달리기 6회 플레이` → `0/6`
    - `끝없는 무덤 3회 플레이` → `0/3`
    - `120회 노획` → progress shown
  - `이동` (Move) button per task
- **자동화 후보:**
  - `claim_daily_tasks` → claim all daily tasks
  - `claim_weekly_tasks` → claim all weekly tasks
  - `collect_task_reward_<name>` → per-task reward collection
- **종료:** BACK 키 (주의: 게임이 백그라운드로 전환됨)

---

### 5. quest_board / pass_screen (항구 패스)
- **진입 좌표:** (75, 780)
- **실제 화면:** Harbor Pass (Battle Pass) screen
- **발견 텍스트:**
  - `항구 패스` (Harbor Pass)
  - `4d 16h` @ (time remaining)
  - `7/100` @ (progress)
  - `정예` (Elite)
  - `프리미엄` (Premium)
  - `무료` (Free) @ tier
  - `$9.99`, `$1.99` @ (prices)
  - `X1` buttons (multiple reward tiers)
  - `x20`, `x1` @ (quantities)
  - `+`, `10`, `11` @ (reward values)
- **자동화 후보:**
  - `claim_free_pass_rewards` → claim free tier rewards
  - `collect_pass_progress` → pass progression collection
- **종료:** X 버튼 닫기困难 (현재 메뉴 상태로 유지)

---

### 6. cards_screen (노획 카드)
- **진입 좌표:** (75, 936)
- **발견 텍스트:**
  - `노획 카드` (Loot Card)
  - `15일` @ (duration)
  - `노획 속도` (Loot speed) - `X2`
  - `가치` (Value) - `950%`
  - `자동 노획 수량` (Auto loot quantity) - `X2`
  - `즉석 보상` (Instant reward):
    - `x500`, `x15k`
  - `일일 보상` (Daily reward) - `비활성화` (Disabled)
  - `$14.99` @ (price)
  - `광고 이용권 카드` (Ad ticket card)
  - `14일` @ (duration)
  - `즉석 보상` - `x100`, `x150`
  - `일일 보상` - `비활성화`
- **자동화 후보:**
  - `activate_daily_card_reward` → 일일 보상 활성화 (if not disabled)
  - `buy_loot_card` → purchase card ($14.99)
- **종료:** BACK 키 (주의: 게임이 백그라운드로 전환됨)

---

## 미탐색 화면 (Game instability로 인해 미완료)

아래 화면들은 게임이 백그라운드로 전환되는 问题로 캡처 실패:
- **ad_tv** (77,1242) - AD panel
- **right_event** (993,316) - Event button
- **trophy** (1005,522) - Leaderboard
- **pass** (1004,701) - Pass button (quest_board와 중복 가능)
- **enter_trade** (316,1890) - Trade mode entry
- **enter_fight** (760,1890) - Fight mode entry
- **event_banner** (548,365) - Top event banner

---

## 자동화 후보 신규 액션 (발견된 것 기준)

| # | 액션 이름 | 화면 |トリガー | 좌표 | 비고 |
|---|----------|------|--------|------|------|
| 1 | `spin_wheel` | wheel | `돌리기` | TBD | 3/3 spins |
| 2 | `skip_wheel_animation` | wheel | `건너뛰기` | TBD | 애니메이션 스킵 |
| 3 | `claim_daily_tasks` | tasks | 일일 임무 클레임 | TBD | +10 보상들 |
| 4 | `claim_weekly_tasks` | tasks | 주간 임무 클레임 | TBD | larger rewards |
| 5 | `claim_event_rewards` | event | Event reward button | TBD | 13h remaining |
| 6 | `claim_free_pass_rewards` | quest_board | 무료 티어 | TBD | 7/100 progress |
| 7 | `activate_daily_card_reward` | cards | 일일 보상 활성화 | TBD | currently disabled |
| 8 | `buy_loot_card` | cards | 구매 버튼 | TBD | $14.99 |

**총 신규 자동화 후보: 8개**

---

## TOP 5 새로 발견된 보상

1. **Lucky Wheel spins** - 3/3 일일 스핀, 돌리면 코인/보석 획득 가능
2. **Tasks (일일 임무)** - 각 +10 보상, 하루에 여러 작업 완료 가능
3. **Tasks (주간 임무)** - 더 큰 보상 (140~700 범위)
4. **Event rewards** - 13시간 남은 이벤트,Exclusive Set 획득 가능
5. **Cards (노획 카드)** - x500, x15k 즉석 보상, 950% 가치 버프

---

## screens.yaml Patch Data

```yaml
# 신규/수정할 화면 설정
screens:
  wheel:
    detect_text: "행운의 바퀴"
    buttons:
      spin: {x: TBD, y: TBD}  # 돌리기 버튼
      skip: {x: TBD, y: TBD}  # 건너뛰기 버튼
  
  tasks_screen:
    detect_text: "임무"
    buttons:
      claim_daily: {x: TBD, y: TBD}  # 일일 임무 클레임
      claim_weekly: {x: TBD, y: TBD}  # 주간 임무 클레임
  
  event_screen:
    detect_text: "Event rewards"
    buttons:
      claim: {x: TBD, y: TBD}  # 이벤트 보상 클레임
  
  cards_screen:
    detect_text: "노획 카드"
    buttons:
      claim_daily: {x: TBD, y: TBD}  # 일일 보상
      buy: {x: TBD, y: TBD}  # 구매 ($14.99)
```

---

## 참고사항

- **Payment Dialog 주의:** IAP 팝업은 `X` 버튼 (1020, 130) 또는 BACK으로 즉시 닫기
- **광고 시청:** "Watch" 버튼 누르지 말고 "later"/X로 닫기 (1분+ 소요)
- **게임 instability:** BACK 키 사용 시 게임이 백그라운드로 전환되는 问题 - Appium으로 직접控制了 필요
- **calibration_dir:** `/home/jclee/dev/idle/idle_outpost_bot/calibration/`

---

*Generated by idle_outpost_bot calibrate workflow*
