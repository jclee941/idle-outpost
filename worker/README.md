# idle-outpost-claim (Cloudflare Worker)

`claim_api.py`를 TypeScript로 포팅한 Worker. Xsolla user-id 서비스에 로그인해
giveaway 아이템을 매일 자동 수령한다. 외부 서버 없이 Worker 단독으로 동작한다.

## 동작
- **cron**: 매일 00:10 KST (15:10 UTC) 자동 실행 — `wrangler.jsonc`의 `triggers.crons`
- **수동**: `GET /` 호출 시 즉시 수령하고 JSON 결과 반환
- 결과는 `IDLE_OUTPOST_SLACK_WEBHOOK`이 있으면 Slack으로도 전송

## 배포

```sh
cd worker
npm install

# 1) 비밀값 등록 (프롬프트에 값 입력)
wrangler secret put IDLE_OUTPOST_USER_IDS         # 예: 79da57a5-...,b4fdf547-...
wrangler secret put IDLE_OUTPOST_XSOLLA_LOGIN_ID  # 048e3522-75bd-43f5-95da-6ec145b9723a
wrangler secret put IDLE_OUTPOST_SLACK_WEBHOOK    # (선택) 없으면 생략 가능

# 2) 배포
npm run deploy
```

비-비밀 설정(PROJECT_ID, MERCHANT_ID, WEBHOOK_URL)은 `wrangler.jsonc`의 `vars`에 있다.

## 로컬 테스트

```sh
cp .dev.vars.example .dev.vars   # 값 채우기
npm run dev                      # http://localhost:8787 접속 → 수령 실행
```

## 로그 확인 / cron 트리거

```sh
wrangler tail                                  # 실시간 로그
curl https://idle-outpost-claim.<subdomain>.workers.dev   # 수동 트리거
```

크론 스케줄 변경은 `wrangler.jsonc`의 `triggers.crons` 수정 후 재배포.
