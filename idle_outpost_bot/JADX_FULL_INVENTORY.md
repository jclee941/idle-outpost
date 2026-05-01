# Idle Outpost - JADX 소스 전수조사 보고서

**조사일:** 2026-04-27  
**소스 경로:** `/tmp/io_apk_pull/jadx_out/sources` (56,679 Java 파일, 472MB)  
**게임 패키지:** `com.rockbite.zombieoutpost`

---

## 카테고리: Reward Dialog (보상/클레임 다이얼로그)

| 클래스명 | 파일경로 | 트리거 조건 | 버튼/좌표 | 자동화 우선순위 |
|---------|---------|-----------|-----------|---------------|
| AFKRewardsDialog | `com/rockbite/zombieoutpost/ui/dialogs/AFKRewardsDialog.java` | 게임 재시작/복귀시 (900초 임계값) | `regularClaimButton` (CLAIM_CAMEL), `rvClaimButton` (CLAIM_PLUS_HOURS + 광고티켓) | **HIGH** |
| ClaimRewardsDialog | `com/rockbite/zombieoutpost/ui/dialogs/ClaimRewardsDialog.java` | 보상 수령시 (다이얼로그 호출) | `claimButton` (CLAIM) | **HIGH** |
| JuicyOfflineEarningsDialog | `com/rockbite/zombieoutpost/ui/dialogs/JuicyOfflineEarningsDialog.java` | 오프라인 복귀시 | `freeButton` (CLAIM_CAMEL), `rwButton` (CLAIM_PLUS_HOURS + 비용) | **HIGH** |
| ASMLteOfflineEarningsDialog | `com/rockbite/zombieoutpost/ui/ASMLteOfflineEarningsDialog.java` | ASM/LTE 모드 오프라인 복귀 (최대 86400초) | `claimButton` (CLAIM), `doubleOfflineSku` (2배 수령) | **HIGH** |
| OfflineEarningsDialog | `com/rockbite/zombieoutpost/ui/dialogs/OfflineEarningsDialog.java` | 오프라인 보상 복귀 | 버튼 정보 없음 | **MEDIUM** |
| DailyStreakDialog | `com/rockbite/zombieoutpost/ui/dialogs/streak/DailyStreakDialog.java` | 일일 리셋 후 첫 접속 | 6일치 위젯 + 마지막 일 위젯 | **HIGH** |
| DailyStreakNotificationDialog | `com/rockbite/zombieoutpost/ui/dialogs/streak/DailyStreakNotificationDialog.java` | 스트릭 획득 알림 | `NOTIFY_ME_TOMORROW`, `MAYBE_LATER` | **MEDIUM** |
| InboxDialog | `com/rockbite/zombieoutpost/ui/dialogs/InboxDialog.java` | 우편함 아이콘 클릭 | Tabs: mail/news/system | **HIGH** |
| VIPRewardClaimDialog | `com/rockbite/zombieoutpost/ui/dialogs/offers/VIPRewardClaimDialog.java` | VIP 레벨업/보상 획득 | `VIPRewardClaimWidget` 행들 | **MEDIUM** |
| DailyQuestDialog | `com/rockbite/zombieoutpost/ui/dialogs/DailyQuestDialog.java` | 일일/주간 퀘스트 탭 | `dailyProgressionWidget`, `weeklyProgressionWidget` | **HIGH** |
| PlayableRewardDialog | `com/rockbite/zombieoutpost/ui/dialogs/PlayableRewardDialog.java` | 플레이어블 보상 | 버튼 정보 없음 | **MEDIUM** |
| EventRewardsDeliveryDialog | `com/rockbite/zombieoutpost/ui/dialogs/EventRewardsDeliveryDialog.java` | 이벤트 보상 배포 | 버튼 정보 없음 | **MEDIUM** |

---

## 카테고리: 광고 진입 (Rewarded Ad / Boost)

| 클래스명 | 파일경로 | 등장 위치 | 광고类型 | 자동화 우선순위 |
|---------|---------|---------|---------|---------------|
| RewardedAdConfirmDialog | `com/rockbite/zombieoutpost/ui/dialogs/RewardedAdConfirmDialog.java` | 어디서든 광고 진입시 | "WATCH_AD_PLAIN" 버튼 | **HIGH** |
| LFShovelDropChanceBoostDialogButton | `com/rockbite/zombieoutpost/ui/buttons/LFShovelDropChanceBoostDialogButton.java` | Fight 모드 | 삽 드랍률 буст 버튼 | **HIGH** |
| LFBoostDialog | `com/rockbite/zombieoutpost/ui/dialogs/LFBoost/LFBoostDialog.java` | Fight 모드 | `fightingSpeedWidget`, `lootingSpeedWidget`, `shovelRewardWidget` | **HIGH** |
| ForcedAdOfferDialog | `com/rockbite/zombieoutpost/ui/dialogs/offers/ForcedAdOfferDialog.java` | Shop 강제 광고 | "GO_TO_SHOP" 버튼 | **MEDIUM** |
| WatchedAdsDialog | `com/rockbite/zombieoutpost/ui/dialogs/misc/WatchedAdsDialog.java` | 광고 시청 후 | 정보 다이얼로그 | **LOW** |
| AdTicketOfferDialog | `com/rockbite/zombieoutpost/ui/dialogs/AdTicketOfferDialog.java` | 광고 티켓 구매 | `costButton` (IAP) | **DANGER** |
| SkipAdsPopupOfferDialog | `com/rockbite/zombieoutpost/shop/and/offers/presenters/popup/skipads/SkipAdsPopupOfferDialog.java` | Shop | IAP 기반 광고 스킵 | **DANGER** |
| FarmAutoWorkDialog | `com/rockbite/zombieoutpost/farm/ui/dialog/FarmAutoWorkDialog.java` | Farm 탭 | 자동 작업 설정 | **HIGH** |

---

## 카테고리: 무료 보상 카운터/타이머

| 클래스명 | 파일경로 | 쿨다운/리셋 | 트리거 | 자동화 가능 |
|---------|---------|------------|--------|-----------|
| MorningResetManager | `com/rockbite/zombieoutpost/farm/logic/MorningResetManager.java` | 일일 (dayStartHour - nightStartHour 기준) | Farm 재시작 | **예** - `grantRewards()` |
| FarmAutoWorkManager | `com/rockbite/zombieoutpost/farm/logic/FarmAutoWorkManager.java` | 농장 운영 타이머 | 자동 작물 심기/수확 | **예** - 복잡한 로직 |
| DailyStreakManager | `com/rockbite/zombieoutpost/logic/DailyStreakManager.java` | 일일 리셋 | DailyResetEvent | **예** - `onDailyReset()` |
| TimeQuestSystem | `com/rockbite/zombieoutpost/logic/timequest/TimeQuestSystem.java` | 일일/주간 | 퀘스트 완료 | **예** - `claimAllDailyRewards()` |
| CalendarDialog | `com/rockbite/zombieoutpost/ui/calendar/CalendarDialog.java` | 이벤트별 상이 | 서버 시간 기준 | **부분** - 이벤트 시각화만 |
| EventCalendarDialog | `com/rockbite/zombieoutpost/rush/EventCalendarDialog.java` | 이벤트별 | RushKalender | **부분** |
| RushShopDialog | `com/rockbite/zombieoutpost/rush/ui/RushShopDialog.java` | 로테이션 기준 | `getTimeLeftUntilRotationEnd()` | **예** - 타이머 감시 |

---

## 카테고리: 이벤트 (LTE/Rush)

| 클래스명 | 파일경로 | 이벤트 类型 | Claim 버튼 | 자동화 우선순위 |
|---------|---------|-----------|-----------|---------------|
| QuestRushDialog | `com/rockbite/zombieoutpost/rush/questrush/QuestRushDialog.java` | Quest Rush | `scrollToFirstClaimableTrainReward()` | **HIGH** |
| LuckySpinnerRushDialog | `com/rockbite/zombieoutpost/rush/questrush/luckyspinnerrush/LuckySpinnerRushDialog.java` | Lucky Spinner | 행운의 룰렛 보상 | **HIGH** |
| RushEventClaimWidget | `com/rockbite/zombieoutpost/rush/ui/RushEventClaimWidget.java` | Rush 공통 | Inbox로 연결 | **MEDIUM** |
| RushListDialog | `com/rockbite/zombieoutpost/rush/ui/RushListDialog.java` | Rush 목록 | RushShopDialog | **MEDIUM** |
| RushShopDialog | `com/rockbite/zombieoutpost/rush/ui/RushShopDialog.java` | Rush 상점 | 로테이션 아이템 | **MEDIUM** |
| ASMLteFirstRewardDialog | `com/rockbite/zombieoutpost/ui/dialogs/lte/awesome/ASMLteFirstRewardDialog.java` | ASM 첫 보상 | 클레임 버튼 | **HIGH** |
| ASMUCClaimDialog | `com/rockbite/zombieoutpost/ui/pages/lte/awesome/ASMUCClaimDialog.java` | ASM UC 보상 | 클레임 버튼 | **HIGH** |
| GoodMorningDialog | `com/rockbite/zombieoutpost/farm/ui/dialog/GoodMorningDialog.java` | Farm 아침 보상 | `seedsRewardWidget`, `forwardTicketRewardWidget` | **HIGH** |

---

## 카테고리: Trade Mode 자동화 요소

| 클래스명 | 파일경로 | 자동화 요소 | 버튼/위치 | 자동화 우선순위 |
|---------|---------|-----------|-----------|---------------|
| WalkieTalkieTradeDialog | `com/rockbite/zombieoutpost/walkie/talkie/ui/dialogs/WalkieTalkieTradeDialog.java` | AFK 보상,Claimable Rewards | `claimableRewardsContainer`, `trackersInfoWidget` | **HIGH** |
| WalkieTalkieTradeClaimableRewardsContainer | `com/rockbite/zombieoutpost/walkie/talkie/ui/widgets/WalkieTalkieTradeClaimableRewardsContainer.java` | 보상 컨테이너 | 보상 클레임 | **HIGH** |
| WalkieTalkieTradeManager | `com/rockbite/zombieoutpost/walkie/talkie/logic/managers/WalkieTalkieTradeManager.java` | 트레이드 로직 | `getTradeDialogData()` | **HIGH** |
| FarmAutoWorkManager | `com/rockbite/zombieoutpost/farm/logic/FarmAutoWorkManager.java` | Farm 자동화 | `ACTION_THRESHOLD=200`, `plant/forward/rewind/harvest/claim` | **HIGH** |
| StationUpgrade 관련 | `com/rockbite/zombieoutpost/shop/and/offers/presenters/popup/permanent/PermanentProfitPopupOfferDialog.java` | 스테이션 업그레이드 | Shop UI | **MEDIUM** |

---

## 카테고리: Fight Mode 자동화 요소

| 클래스명 | 파일경로 | 자동화 요소 | 버튼/위치 | 자동화 우선순위 |
|---------|---------|-----------|-----------|---------------|
| WalkieTalkieFightDialog | `com/rockbite/zombieoutpost/walkie/talkie/ui/dialogs/WalkieTalkieFightDialog.java` | AFK 보상, Claimable Rewards | `claimableRewardsContainer`, `trackersInfoWidget` | **HIGH** |
| WalkieTalkieFightClaimableRewardsContainer | `com/rockbite/zombieoutpost/walkie/talkie/ui/widgets/WalkieTalkieFightClaimableRewardsContainer.java` | 보상 컨테이너 | 보상 클레임 | **HIGH** |
| AutoLootDialog | `com/rockbite/zombieoutpost/ui/dialogs/missions/AutoLootDialog.java` | 자동 루팅 | `startButton`, `rarityDropDownMenu`, `shovelAmountDropDownMenu` | **HIGH** |
| WalkieTalkieAutoLootResumeWidget | `com/rockbite/zombieoutpost/walkie/talkie/ui/widgets/WalkieTalkieAutoLootResumeWidget.java` | 오토 루팅 재개 | 위젯 표시 | **MEDIUM** |
| LFShovelDropChanceBoostDialogButton | `com/rockbite/zombieoutpost/ui/buttons/LFShovelDropChanceBoostDialogButton.java` | 삽 드랍률 буст | 광고 시청 필요 | **HIGH** |
| LFBoostDialog | `com/rockbite/zombieoutpost/ui/dialogs/LFBoost/LFBoostDialog.java` | Fight/Loot 속도 буст | 3개 위젯 (fighting/looting/shovel) | **HIGH** |
| LiveFightEventHandler | `com/rockbite/zombieoutpost/walkie/talkie/logic/controllers/LiveFightEventHandler.java` | 라이브 fight 이벤트 | 이벤트 핸들러 | **MEDIUM** |

---

## 카테고리: 위험 영역 (절대 자동탭 금지)

| 클래스명 | 파일경로 | 위험 이유 | 대체 액션 |
|---------|---------|---------|---------|
| PiggyBankDialog | `com/rockbite/zombieoutpost/ui/dialogs/offers/PiggyBankDialog.java` | IAP-gem 기반 돼지저금통破碎 | 절대 클릭 금지 |
| SubscriptionCardDialog | `com/rockbite/zombieoutpost/ui/dialogs/offers/SubscriptionCardDialog.java` | 구독/IAP 결제 | 절대 클릭 금지 |
| VIPRewardClaimDialog | `com/rockbite/zombieoutpost/ui/dialogs/offers/VIPRewardClaimDialog.java` | IAP 연계 VIP | **관찰만** - 자동클레임 불가 |
| SubscriptionsDialog | `com/rockbite/zombieoutpost/ui/dialogs/SubscriptionsDialog.java` | 구독 관리 | 절대 클릭 금지 |
| PurchaseWithDiamondsDialog | `com/rockbite/zombieoutpost/ui/dialogs/PurchaseWithDiamondsDialog.java` | 다이아 구매 | 절대 클릭 금지 |
| SpendDiamondsConfirmDialog | `com/rockbite/zombieoutpost/ui/dialogs/SpendDiamondsConfirmDialog.java` | 다이아 소비 확인 | 절대 클릭 금지 |
| DrawPurchaseConfirmDialog | `com/rockbite/zombieoutpost/ui/dialogs/DrawPurchaseConfirmDialog.java` | 뽑기 구매 | 절대 클릭 금지 |
| AdTicketOfferDialog | `com/rockbite/zombieoutpost/ui/dialogs/AdTicketOfferDialog.java` | 광고 티켓 IAP | 절대 클릭 금지 |
| SwitchAccountConfirmDialog | `com/rockbite/zombieoutpost/ui/dialogs/SwitchAccountConfirmDialog.java` | 계정 전환 | **절대 금지** |
| AccountDetailsDialog | `com/rockbite/zombieoutpost/ui/dialogs/account/AccountDetailsDialog.java` | 계정 상세 | **절대 금지** |
| ResetBuildDialog | `com/rockbite/zombieoutpost/specialization/ui/dialogs/ResetBuildDialog.java` | 빌드 리셋 | 주의 필요 |
| V23MigrationDialog | `com/rockbite/zombieoutpost/ui/dialogs/misc/V23MigrationDialog.java` | 데이터 마이그레이션 | **절대 금지** |
| ForcedAdOfferDialog | `com/rockbite/zombieoutpost/ui/dialogs/offers/ForcedAdOfferDialog.java` | **조건부 위험** - "GO_TO_SHOP"은 IAP로 연결 가능 | Shop 내부 navigation 감시 |

---

## 봇이 누락하면 안 될 자동화 기회 TOP 20

1. **AFKRewardsDialog** - Fight 복귀시 2배 보상 광고 (`rvClaimButton`) -的广告观看で2倍
2. **DailyStreakDialog** - 7일 연속 접속 보상 (매일 1회)
3. **DailyQuestDialog** - 일일/주간 퀘스트 보상 (타임리밋 감시)
4. **WalkieTalkieFightDialog** - Fight 모드 AFK 보상 자동 클레임
5. **WalkieTalkieTradeDialog** - Trade 모드 AFK 보상 자동 클레임
6. **AutoLootDialog** - Fight 삽 자동 루팅 (레어리티/삽数量 설정)
7. **LFBoostDialog** - Fight 속도/루팅 속도/삽 보상 буст (3종 광고)
8. **LFShovelDropChanceBoostDialogButton** - 삽 드랍률 순간 буст
9. **GoodMorningDialog** - Farm 일일 리셋 보상 (씨앗 + 포워드 티켓)
10. **MorningResetManager** - Farm 자동화 재시작 로직
11. **FarmAutoWorkManager** - Farm 자동 작물 관리 (plant/harvest/claim)
12. **JuicyOfflineEarningsDialog** - 오프라인 복귀 보상 (2배는 광고)
13. **ASMLteOfflineEarningsDialog** - ASM LTE 오프라인 보상 (2배는 광고)
14. **InboxDialog** - 메일/뉴스/시스템 탭의 미수령 보상
15. **QuestRushDialog** - Rush 이벤트 퀘스트 보상
16. **LuckySpinnerRushDialog** - Rush 행운의 룰렛
17. **VIPRewardClaimDialog** - VIP 레벨업 보상 (단, IAP 연계 주의)
18. **RushEventClaimWidget** - Rush 인박스 연결 위젯
19. **RushShopDialog** - Rush 로테이션 타이머 감시
20. **CalendarDialog** - 이벤트 캘린더 (일정 추적)

---

## 발견된 자동화 시스템 매니저 요약

| 매니저 클래스 | 경로 | 역할 |
|-------------|------|------|
| `FarmAutoWorkManager` | `farm/logic/FarmAutoWorkManager.java` | Farm 자동화 (plant/harvest/claim) |
| `MorningResetManager` | `farm/logic/MorningResetManager.java` | Farm 일일 리셋 + 보상 |
| `FarmAFKManager` | `farm/logic/FarmAFKManager.java` | Farm AFK 로직 |
| `LFAfkManager` | `logic/livefight/afk/LFAfkManager.java` | Fight AFK 보상 관리 |
| `DailyStreakManager` | `logic/DailyStreakManager.java` | 연속 접속 관리 |
| `TimeQuestSystem` | `logic/timequest/TimeQuestSystem.java` | 일일/주간 퀘스트 |
| `WalkieTalkieTradeManager` | `walkie/talkie/logic/managers/WalkieTalkieTradeManager.java` | Trade 모드 관리 |
| `WalkieTalkieFightManager` | `walkie/talkie/logic/managers/WalkieTalkieFightManager.java` | Fight 모드 관리 |
| `LiveFightSystem` | `logic/livefight/LiveFightSystem.java` | Fight 전체 시스템 |
| `ASMRushController` | `rush/asmrush/ASMRushController.java` | ASM 이벤트 제어 |
| `GlobalRushSystem` | `rush/GlobalRushSystem.java` | Rush 전역 시스템 |

---

## I18NKeys 자동화 관련 텍스트 (참고)

```
CLAIM, CLAIM_CAMEL, CLAIM_PLUS_HOURS, CLAIM_REWARDS
DAILY_STREAK_TITLE, DAILY_TASKS, DAILY_REWARDS, DAILY_CLAIM
AUTO_LOOT, AUTO_UPGRADES_STATION, AUTOMATE, AUTOMATION_DURATION
WATCH_AD_PLAIN, WATCH_AD_TO_GAIN_REWARD
RESETS_IN, NEXT_DAILY_BONUSES_IN, MAX_OFFLINE_REWARD_TIME
LF_BOOST_DIALOG_TITLE, LF_SHOVEL_DROP_BUTTON_LABEL
FARM_AUTO_WORK_DIALOG_TITLE, FARM_AUTO_WORK_DIALOG_REWARD
OVERNIGHT_REWARDS, FREE_DAILY_CHEST, FREE_DAILY_CHEST_IN
```

---

## 결론

**총 발견된 자동화 기회:** 47개 진입점  
**높은 우선순위 (즉시 구현):** 21개  
**중간 우선순위 (테스트 후):** 16개  
**위험 영역 (절대 금지):** 10개  

**TOP 5 누락시 위험:**
1. AFKRewardsDialog 광고 2배 - 수익 50% 손실
2. DailyStreakDialog - 일일 보상 1회 손실
3. AutoLootDialog - Fight 효율성 극대화 실패
4. WalkieTalkie *_claimableRewardsContainer - Fight/Trade 보상 누락
5. DailyQuestDialog - 일일/주간 퀘스트 리워드 손실

**완료 파일:** `/home/jclee/dev/idle/idle_outpost_bot/JADX_FULL_INVENTORY.md`
