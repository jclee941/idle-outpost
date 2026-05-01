# Idle Outpost — 광고 보상 요소 (실측 정정판)

이전 분석 오류 정정.

## 메인 화면 좌측 (75, 1242) 아이콘 — 광고 아님!

이전엔 "TV with AD = ad reward 버튼"으로 식별했으나 잘못. 실제 분석:

- 아트: 파란 TV에 **빨간 X 처리된 "AD"** 표시
- 의미: **광고 제거 (No-Ads) 버프 버튼** — 일정 시간 광고 안 보게 해주는 토큰
- 탭하면: 액션 패널이 열림 (Trade/Battle 선택지) — *부수 효과로 다른 패널 열림*
- 타이머 (예: "9m 20s") = no-ads 활성 시간 또는 다음 사용 가능 시간

→ **봇이 이 버튼 자동으로 누르면 안 됨** (광고 보상 못 받고 의미 없는 동작)

## 메인 화면 다른 광고 진입점 — 0개

OCR로 메인 화면 25개 텍스트 분석:
```
'거래', '전투', '해변가 6-3', '겨울 숲 5-2~9', 'sexsexbo', '28.6m', '74',
'Cornfield Dream', '+412% POWER', 'Win Exclusive Set!', '2/6 items collected',
'Profit', '+2.23k%', '14h 54m', '14h 55m', '45m 35s', '2d 14h',
'2h 50m', '2h 51m', '#22'
```

광고 키워드 없음:
- ❌ "AD", "Watch", "광고", "▶", "x2"
- ❌ "free spin" 류 명시 텍스트
- ❌ "boost" (Profit 옆 +2.23k%는 누적치 표시일 뿐)

**결론: 메인 화면에서 자동화 가능한 광고 보상 = 없음**.

## 광고는 어디서 나오나

코드 분석 (jadx)으로 확인된 광고 트리거 위치:

| 클래스 | 위치 | 효과 |
|--------|------|------|
| `AdSkipButton` | Trade Mode 보스전 쿨다운 | 보스 즉시 진입 |
| `UpgradeAdButton` | Trade Mode 스테이션 업그레이드 패널 | 광고 보고 N레벨 즉시 |
| `JuicyTotalProfitBoostButton` | Trade Mode 화면 상단 | Profit 일시 부스트 |
| `LFBoostButton` | Fight Mode 라이브파이트 | 라이브파이트 부스트 |
| `LFShovelDropChanceBoostDialogButton` | Fight Mode 다이얼로그 | 삽 드랍률 증가 |
| `RewardedAdConfirmDialog` | 광고 시청 직전 확인 | "Watch Ad?" |
| `AFKRewardsDialog` | 게임 재시작 시 자동 popup | 오프라인 보상 (x2 ad option) |

→ **모두 Trade/Fight Mode 진입 후에만 등장**.

## 봇 자동화 가능 vs 불가

| 시점 | 가능? | 노트 |
|------|-------|------|
| 게임 첫 실행 | ✅ AFK 보상 dialog 자동 popup → 광고 x2 옵션 탭 | 가장 확실 |
| 메인 화면 정주 | ❌ 광고 진입점 없음 | 패널만 있음 |
| Trade Mode 진입 | △ 화면 동적, 안전한 좌표 매핑 어려움 | OCR로 "AD"/"Watch" 텍스트 검색 후 좌표 |
| Fight Mode 진입 | △ 동일 |

## 봇 정확한 광고 자동화 전략

```
LOOP:
  1. 게임 launch (force-stop 후 재시작) - AFKRewardsDialog popup 유도
  2. 30초 대기
  3. 화면 OCR
     - "x2" + "광고" 또는 "Watch" 텍스트 발견 → 그 좌표 탭
     - "Claim" 버튼 → 탭
  4. 화면 OCR 재
     - 메인 화면 ("거래"/"전투" bottom) 복귀 확인
  5. 30분 sleep → 반복
```

## 메인 화면에서 진짜 자동 가능한 것

| 좌표 | 효과 |
|------|------|
| (75, 348) Calendar | 일일 출석 보상 |
| (75, 491) Wheel | 무료 스핀 (광고 추가 옵션 있음) |
| (75, 636) Tasks | 미션 보상 클레임 |
| (75, 780) Quest | 퀘스트 보상 |
| (860, 135) Inbox | 우편 보상 |

이것들 전부 광고 없이 **무료 보상**이라 봇이 안전히 처리 가능.
**광고 보상은 게임 재시작 → AFK dialog 경로가 가장 확실하고 정량적**.
