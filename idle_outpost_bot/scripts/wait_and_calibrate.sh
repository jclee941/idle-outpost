#!/usr/bin/env bash
# Usage: bash idle_outpost_bot/scripts/wait_and_calibrate.sh
set -euo pipefail

REMOTE_HOST="${REMOTE_HOST:-192.168.50.220}"
ADB_REMOTE="ADB_SERVER_SOCKET=tcp:${REMOTE_HOST}:5037 adb"
PKG="com.rockbite.zombieoutpost"
ENV_FILE="$(dirname "$0")/../../.env"
SCREEN_DIR="$(dirname "$0")/../../.calibrate_dumps"

mkdir -p "$SCREEN_DIR"

echo "==> waiting for $PKG install (poll every 10s)..."
for i in $(seq 1 360); do
  if ssh "root@${REMOTE_HOST}" "adb shell pm list packages 2>/dev/null | grep -q $PKG"; then
    echo "    detected after ${i} polls"
    break
  fi
  sleep 10
done

if ! ssh "root@${REMOTE_HOST}" "adb shell pm list packages 2>/dev/null | grep -q $PKG"; then
  echo "ERROR: $PKG not installed after 1 hour" >&2
  exit 1
fi

echo "==> resolving main activity"
ACTIVITY=$(ssh "root@${REMOTE_HOST}" "adb shell cmd package resolve-activity --brief $PKG" \
  | tail -1 | tr -d '\r' | cut -d/ -f2)
echo "    activity=$ACTIVITY"

echo "==> updating .env"
python3 - <<PY
from pathlib import Path
env = Path("$ENV_FILE")
text = env.read_text(encoding="utf-8")
out_lines: list[str] = []
seen_pkg = seen_act = False
for line in text.splitlines():
    if line.startswith("IDLE_OUTPOST_PACKAGE="):
        out_lines.append("IDLE_OUTPOST_PACKAGE=$PKG"); seen_pkg = True
    elif line.startswith("IDLE_OUTPOST_ACTIVITY="):
        out_lines.append("IDLE_OUTPOST_ACTIVITY=$ACTIVITY"); seen_act = True
    else:
        out_lines.append(line)
if not seen_pkg:
    out_lines.append("IDLE_OUTPOST_PACKAGE=$PKG")
if not seen_act:
    out_lines.append("IDLE_OUTPOST_ACTIVITY=$ACTIVITY")
env.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
print(env)
PY

echo "==> launching game"
ssh "root@${REMOTE_HOST}" "adb shell am start -n $PKG/$ACTIVITY"
sleep 8

echo "==> screenshot loop (10 frames @ 5s, capture different game states)"
for n in $(seq 1 10); do
  remote="/sdcard/calibrate_${n}.png"
  ssh "root@${REMOTE_HOST}" "adb shell screencap -p $remote"
  scp "root@${REMOTE_HOST}:$remote" "${SCREEN_DIR}/frame_${n}.png" >/dev/null
  echo "    saved frame_${n}.png"
  sleep 5
done

echo "==> done. screenshots in: $SCREEN_DIR"
ls -la "$SCREEN_DIR"
