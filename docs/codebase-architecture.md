# idle-outpost Codebase Architecture

## Module Dependency Diagram

```mermaid
flowchart TB
    subgraph Entry["📌 Entry Points"]
        MAIN["main.py<br/>Promo Code CLI"]
        BOT["idle_outpost_bot/__main__.py<br/>Android Bot CLI"]
    end

    subgraph Promo["🎁 Promo Code Monitor"]
        AUTH["auth.py<br/>Xsolla Auth"]
        CLAIM["claim_api.py<br/>Daily Claim"]
        REDEEM["redeemer.py<br/>Code Redeem"]
        SCRAPE["scraper.py<br/>Code Scraper"]
        STORE["store.py<br/>JSON Store"]
        NOTIFY["notifier.py<br/>Slack Notify"]
    end

    subgraph BotCore["🤖 Android Bot Core"]
        SETTINGS["settings.py<br/>Env Config"]
        STATE["state.py<br/>Bot State"]
        CFG["config_loader.py<br/>YAML Config"]
        LOOP["loop.py<br/>Main Loop"]
        DRIVER["driver.py<br/>Appium Driver"]
        VISION["vision.py<br/>OCR / CV"]
        ACTIONS["actions.py<br/>Tap / Swipe"]
        SAFETY["safety.py<br/>Guardrails"]
        TASKS["tasks/<br/>Task Registry"]
        BOT_NOTIFY["notify.py<br/>Bot Notify"]
    end

    subgraph ApiClient["🔌 API Client"]
        API_CLIENT["client.py<br/>HTTP Client"]
        API_AUTH["api/auth.py<br/>GameAuth"]
        ENDPOINTS["endpoints.py<br/>URLs"]
        FIREBASE["firebase_config.py<br/>Firebase"]
        ANALYZE["analyze_capture.py<br/>Capture Analysis"]
    end

    subgraph External["🌐 External"]
        SLACK["Slack Webhook"]
        XSOLLA["Xsolla API"]
        IDLE["Idle Outpost API"]
        FIREBASE_API["Firebase API"]
    end

    %% Entry -> Promo
    MAIN --> AUTH
    MAIN --> CLAIM
    MAIN --> REDEEM
    MAIN --> SCRAPE
    MAIN --> STORE
    MAIN --> NOTIFY

    %% Promo internal
    AUTH --> XSOLLA
    CLAIM --> AUTH
    CLAIM --> NOTIFY
    REDEEM --> AUTH
    REDEEM --> IDLE
    SCRAPE --> IDLE
    NOTIFY --> SLACK

    %% Entry -> Bot
    BOT --> SETTINGS
    BOT --> STATE
    BOT --> CFG
    BOT --> LOOP
    BOT --> DRIVER
    BOT --> VISION
    BOT --> BOT_NOTIFY

    %% Bot internal
    LOOP --> CFG
    LOOP --> STATE
    LOOP --> TASKS
    LOOP --> VISION
    LOOP --> BOT_NOTIFY
    TASKS --> ACTIONS
    TASKS --> SAFETY
    TASKS --> VISION
    ACTIONS --> VISION
    SAFETY --> VISION
    DRIVER --> SETTINGS
    BOT_NOTIFY --> NOTIFY
    CFG --> VISION

    %% API Client
    API_CLIENT --> API_AUTH
    API_CLIENT --> ENDPOINTS
    API_CLIENT --> FIREBASE
    API_AUTH --> ENDPOINTS
    API_AUTH --> XSOLLA
    ANALYZE --> FIREBASE
    FIREBASE --> FIREBASE_API

    %% Cross-cutting
    CLAIM -.->|uses| API_CLIENT
    REDEEM -.->|uses| API_CLIENT

    style MAIN fill:#e1f5fe
    style BOT fill:#e1f5fe
    style NOTIFY fill:#fff3e0
    style BOT_NOTIFY fill:#fff3e0
    style FIREBASE fill:#ffebee
    style AUTH fill:#ffebee
    style API_CLIENT fill:#f3e5f5
```

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

```mermaid
sequenceDiagram
    actor User
    participant main.py
    participant scraper.py
    participant store.py
    participant redeemer.py
    participant auth.py
    participant notifier.py

    User->>main.py: python main.py check
    main.py->>scraper.py: scrape_codes_with_metadata()
    scraper.py-->>main.py: list[Code]
    main.py->>store.py: get_new_codes()
    store.py-->>main.py: new_codes[]
    alt new codes found
        main.py->>store.py: save_codes()
        main.py->>notifier.py: notify_new_codes()
        notifier.py->>notifier.py: POST Slack webhook
    end
    main.py->>store.py: get_retryable_codes()
    store.py-->>main.py: retryable[]
    loop retryable codes
        main.py->>redeemer.py: attempt_redeem(code)
        redeemer.py->>auth.py: get_bearer_token()
        auth.py-->>redeemer.py: Bearer token
        redeemer.py->>redeemer.py: POST /redeem
        redeemer.py-->>main.py: RedeemResult
        main.py->>store.py: mark_redeem_result()
    end
```

## Data Flow (Android Bot)

```mermaid
sequenceDiagram
    actor User
    participant __main__.py
    participant loop.py
    participant driver.py
    participant vision.py
    participant tasks/registry.py
    participant state.py

    User->>__main__.py: python -m idle_outpost_bot run
    __main__.py->>loop.py: run_loop()
    loop->>state.py: load_state()
    state.py-->>loop.py: BotState
    loop->>driver.py: session()
    driver.py-->>loop.py: WebDriver
    loop->>vision.py: Ocr(lang=...)
    loop->>loop.py: while running
    loop->>vision.py: grab_screenshot()
    vision.py-->>loop.py: PIL.Image
    loop->>vision.py: find_text(image, "text")
    vision.py-->>loop.py: OcrHit[]
    loop->>tasks/registry.py: run_task()
    tasks/registry.py->>driver.py: tap(x, y)
    tasks/registry.py-->>loop.py: TaskResult
    loop->>state.py: save_state()
```
