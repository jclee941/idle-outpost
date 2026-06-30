# idle-outpost Codebase Architecture

## Module Dependency Diagram

#### Diagram summary 1

- Type: flowchart
- Component: main.py / Promo Code CLI (MAIN)
- Component: idleoutpostbot/main.py / Android Bot CLI (BOT)
- Component: auth.py / Xsolla Auth (AUTH)
- Component: claimapi.py / Daily Claim (CLAIM)
- Component: redeemer.py / Code Redeem (REDEEM)
- Component: scraper.py / Code Scraper (SCRAPE)
- Component: store.py / JSON Store (STORE)
- Component: notifier.py / Slack Notify (NOTIFY)
- Component: settings.py / Env Config (SETTINGS)
- Component: state.py / Bot State (STATE)
- Component: configloader.py / YAML Config (CFG)
- Component: loop.py / Main Loop (LOOP)
- Component: driver.py / Appium Driver (DRIVER)
- Component: vision.py / OCR / CV (VISION)
- Component: actions.py / Tap / Swipe (ACTIONS)
- Component: safety.py / Guardrails (SAFETY)
- Component: tasks/ / Task Registry (TASKS)
- Component: notify.py / Bot Notify (BOTNOTIFY)
- Component: client.py / HTTP Client (APICLIENT)
- Component: api/auth.py / GameAuth (APIAUTH)
- Component: endpoints.py / URLs (ENDPOINTS)
- Component: firebaseconfig.py / Firebase (FIREBASE)
- Component: analyzecapture.py / Capture Analysis (ANALYZE)
- Component: Slack Webhook (SLACK)
- Component: Xsolla API (XSOLLA)
- Component: Idle Outpost API (IDLE)
- Component: Firebase API (FIREBASEAPI)
- main.py / Promo Code CLI (MAIN) -> auth.py / Xsolla Auth (AUTH)
- main.py / Promo Code CLI (MAIN) -> claimapi.py / Daily Claim (CLAIM)
- main.py / Promo Code CLI (MAIN) -> redeemer.py / Code Redeem (REDEEM)
- main.py / Promo Code CLI (MAIN) -> scraper.py / Code Scraper (SCRAPE)
- main.py / Promo Code CLI (MAIN) -> store.py / JSON Store (STORE)
- main.py / Promo Code CLI (MAIN) -> notifier.py / Slack Notify (NOTIFY)
- auth.py / Xsolla Auth (AUTH) -> Xsolla API (XSOLLA)
- claimapi.py / Daily Claim (CLAIM) -> auth.py / Xsolla Auth (AUTH)
- claimapi.py / Daily Claim (CLAIM) -> notifier.py / Slack Notify (NOTIFY)
- redeemer.py / Code Redeem (REDEEM) -> auth.py / Xsolla Auth (AUTH)
- redeemer.py / Code Redeem (REDEEM) -> Idle Outpost API (IDLE)
- scraper.py / Code Scraper (SCRAPE) -> Idle Outpost API (IDLE)
- notifier.py / Slack Notify (NOTIFY) -> Slack Webhook (SLACK)
- idleoutpostbot/main.py / Android Bot CLI (BOT) -> settings.py / Env Config (SETTINGS)
- idleoutpostbot/main.py / Android Bot CLI (BOT) -> state.py / Bot State (STATE)
- idleoutpostbot/main.py / Android Bot CLI (BOT) -> configloader.py / YAML Config (CFG)
- idleoutpostbot/main.py / Android Bot CLI (BOT) -> loop.py / Main Loop (LOOP)
- idleoutpostbot/main.py / Android Bot CLI (BOT) -> driver.py / Appium Driver (DRIVER)
- idleoutpostbot/main.py / Android Bot CLI (BOT) -> vision.py / OCR / CV (VISION)
- idleoutpostbot/main.py / Android Bot CLI (BOT) -> notify.py / Bot Notify (BOTNOTIFY)
- loop.py / Main Loop (LOOP) -> configloader.py / YAML Config (CFG)
- loop.py / Main Loop (LOOP) -> state.py / Bot State (STATE)
- loop.py / Main Loop (LOOP) -> tasks/ / Task Registry (TASKS)
- loop.py / Main Loop (LOOP) -> vision.py / OCR / CV (VISION)
- loop.py / Main Loop (LOOP) -> notify.py / Bot Notify (BOTNOTIFY)
- tasks/ / Task Registry (TASKS) -> actions.py / Tap / Swipe (ACTIONS)
- tasks/ / Task Registry (TASKS) -> safety.py / Guardrails (SAFETY)
- tasks/ / Task Registry (TASKS) -> vision.py / OCR / CV (VISION)
- actions.py / Tap / Swipe (ACTIONS) -> vision.py / OCR / CV (VISION)
- safety.py / Guardrails (SAFETY) -> vision.py / OCR / CV (VISION)
- driver.py / Appium Driver (DRIVER) -> settings.py / Env Config (SETTINGS)
- notify.py / Bot Notify (BOTNOTIFY) -> notifier.py / Slack Notify (NOTIFY)
- configloader.py / YAML Config (CFG) -> vision.py / OCR / CV (VISION)
- client.py / HTTP Client (APICLIENT) -> api/auth.py / GameAuth (APIAUTH)
- client.py / HTTP Client (APICLIENT) -> endpoints.py / URLs (ENDPOINTS)
- client.py / HTTP Client (APICLIENT) -> firebaseconfig.py / Firebase (FIREBASE)
- api/auth.py / GameAuth (APIAUTH) -> endpoints.py / URLs (ENDPOINTS)
- api/auth.py / GameAuth (APIAUTH) -> Xsolla API (XSOLLA)
- analyzecapture.py / Capture Analysis (ANALYZE) -> firebaseconfig.py / Firebase (FIREBASE)
- firebaseconfig.py / Firebase (FIREBASE) -> Firebase API (FIREBASEAPI)
- claimapi.py / Daily Claim (CLAIM) -> client.py / HTTP Client (APICLIENT)
- redeemer.py / Code Redeem (REDEEM) -> client.py / HTTP Client (APICLIENT)


## Directory Structure

```text
idle-outpost/
├── main.py                      # Promo code monitor CLI
├── auth.py                      # Xsolla authentication
├── claim_api.py                 # Daily giveaway claimer
├── redeemer.py                  # Promo code redeemer
├── scraper.py                   # Code scraper from web
├── store.py                     # JSON-backed code storage
├── notifier.py                  # Slack notification
├── .env.example                 # Required env vars
│
├── idle_outpost_bot/            # Android automation bot
│   ├── __main__.py              # Bot CLI entry
│   ├── settings.py              # Environment settings
│   ├── state.py                 # Persistent bot state
│   ├── config_loader.py         # YAML screen config
│   ├── loop.py                  # Main automation loop
│   ├── driver.py                # Appium driver wrapper
│   ├── vision.py                # OCR + CV utilities
│   ├── actions.py               # Touch actions
│   ├── safety.py                # Guardrail checks
│   ├── calibrate.py             # Screen calibration
│   ├── discover.py              # Package discovery
│   ├── notify.py                # Bot notifications
│   ├── auto_calibrate.py        # Auto calibration tool
│   └── tasks/                   # Task implementations
│       ├── base.py
│       ├── registry.py
│       └── __init__.py
│
└── idle_outpost_api/            # HTTP API client
    ├── client.py                # HTTP client (httpx)
    ├── auth.py                  # Game authentication
    ├── endpoints.py             # Service endpoints
    ├── firebase_config.py       # Firebase configuration
    └── analyze_capture.py       # Capture analyzer
```

## Data Flow (Promo Code Monitor)

#### Diagram summary 2

- Type: sequence
- Participant: User
- Participant: main.py
- Participant: scraper.py
- Participant: store.py
- Participant: redeemer.py
- Participant: auth.py
- Participant: notifier.py
- User -> main.py: python main.py check
- main.py -> scraper.py: scrapecodeswithmetadata()
- scraper.py -> main.py: list[Code]
- main.py -> store.py: getnewcodes()
- store.py -> main.py: newcodes[]
- main.py -> store.py: savecodes()
- main.py -> notifier.py: notifynewcodes()
- notifier.py -> notifier.py: POST Slack webhook
- main.py -> store.py: getretryablecodes()
- store.py -> main.py: retryable[]
- main.py -> redeemer.py: attemptredeem(code)
- redeemer.py -> auth.py: getbearertoken()
- auth.py -> redeemer.py: Bearer token
- redeemer.py -> redeemer.py: POST /redeem
- redeemer.py -> main.py: RedeemResult
- main.py -> store.py: markredeemresult()


## Data Flow (Android Bot)

#### Diagram summary 3

- Type: sequence
- Participant: User
- Participant: main.py
- Participant: loop.py
- Participant: driver.py
- Participant: vision.py
- Participant: tasks/registry.py
- Participant: state.py
- User -> main.py: python -m idleoutpostbot run
- main.py -> loop.py: runloop()
- loop -> state.py: loadstate()
- state.py -> loop.py: BotState
- loop -> driver.py: session()
- driver.py -> loop.py: WebDriver
- loop -> vision.py: Ocr(lang=...)
- loop -> loop.py: while running
- loop -> vision.py: grabscreenshot()
- vision.py -> loop.py: PIL.Image
- loop -> vision.py: findtext(image, "text")
- vision.py -> loop.py: OcrHit[]
- loop -> tasks: runtask()
- tasks -> driver.py: tap(x, y)
- tasks -> loop.py: TaskResult
- loop -> state.py: savestate()
