# idle_outpost_bot

Android automation scaffold for the Idle Outpost game.

## Stack
- **Control**: Appium 2 + UiAutomator2 driver (running on `192.168.50.220:4723`)
- **Vision**: PaddleOCR (Korean) + screenshot diffing
- **State**: JSON at `~/.local/share/idle-outpost-bot/state.json`
- **Notifications**: Slack via `IDLE_OUTPOST_SLACK_WEBHOOK`

## Infrastructure already provisioned on .220
- Android SDK at `/opt/android-sdk` (cmdline-tools, platform-tools, emulator, Android 13 Play Store image)
- AVD `idle_outpost` (Pixel 5, 4GB RAM)
- Emulator running as systemd unit `idle-outpost-emu.service`
- Appium 2 server running as systemd unit `idle-outpost-appium.service` on port 4723

```sh
# emulator + appium control
ssh root@192.168.50.220 systemctl status idle-outpost-emu idle-outpost-appium
ssh root@192.168.50.220 systemctl restart idle-outpost-emu
ssh root@192.168.50.220 adb devices
```

## CLI

```sh
uv pip install -e ".[bot]"

# 1. find the package after installing the game on the emulator
python -m idle_outpost_bot discover

# 2. set IDLE_OUTPOST_PACKAGE / IDLE_OUTPOST_ACTIVITY in .env

# 3. capture current screen + OCR for config tuning
python -m idle_outpost_bot calibrate --label main_screen

# 4. fill in idle_outpost_bot/config/screens.yaml with detect_text and button coords

# 5. dry-run a single iteration
IDLE_OUTPOST_DRY_RUN=1 python -m idle_outpost_bot once

# 6. run the loop
python -m idle_outpost_bot run

# inspect state
python -m idle_outpost_bot status
```

## Installing Idle Outpost on the .220 emulator

The emulator is headless. To install:

1. **APK route**: download an Idle Outpost APK and `adb -s emulator-5554 install /path/to.apk`.
2. **Play Store route**: temporarily run the emulator with `-no-window` removed on a desktop with X forwarding (`ssh -X`) or use `scrcpy`:
   ```sh
   ssh -L 5555:127.0.0.1:5555 root@192.168.50.220 'adb tcpip 5555'
   adb connect 192.168.50.220:5555
   scrcpy
   ```
   Sign in to Google, install Idle Outpost, then disconnect scrcpy.

After installation, run `python -m idle_outpost_bot discover` to verify the package is detected.
