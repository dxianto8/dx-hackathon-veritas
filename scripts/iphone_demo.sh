#!/usr/bin/env bash
# Open SecondLook on a virtual iPhone (Xcode Simulator) and record a demo video.
#
#   1. In one Terminal:   source .venv/bin/activate && ANTHROPIC_API_KEY=your-key python app.py
#   2. In another:        bash scripts/iphone_demo.sh            (optional: a device name, e.g. "iPhone 16 Pro")
#
# The video is saved as secondlook-demo.mp4 in the current folder.
set -euo pipefail

URL="http://127.0.0.1:7860"
OUT="secondlook-demo.mp4"
WANT="${1:-}"

command -v xcrun >/dev/null || { echo "xcrun not found. Install Xcode, open it once, then try again."; exit 1; }
if ! curl -s -o /dev/null "$URL"; then
  echo "SecondLook isn't running at $URL."
  echo "Start it first in another Terminal:  source .venv/bin/activate && ANTHROPIC_API_KEY=your-key python app.py"
  exit 1
fi

# Pick an available iPhone: the one you named, otherwise the newest non-SE model.
UDID=$(xcrun simctl list devices available -j | WANT="$WANT" python3 -c '
import json, os, re, sys
want = os.environ["WANT"]
devs = []
for runtime, items in json.load(sys.stdin)["devices"].items():
    if "iOS" not in runtime:
        continue
    ver = tuple(int(x) for x in re.findall(r"\d+", runtime.split("iOS")[-1])[:2])
    for d in items:
        if d["name"].startswith("iPhone"):
            devs.append((ver, d["name"], d["udid"]))
if want:
    devs = [d for d in devs if d[1] == want]
else:
    devs = [d for d in devs if " SE" not in d[1]] or devs
if not devs:
    sys.exit("No matching iPhone simulator. In Xcode: Settings > Components, install an iOS runtime.")
print(sorted(devs)[-1][2])
')
NAME=$(xcrun simctl list devices | grep "$UDID" | sed -E 's/^ *(.*) \(.*/\1/' | head -1)
echo "Using $NAME"

xcrun simctl boot "$UDID" 2>/dev/null || true          # fine if it's already booted
open -a Simulator --args -CurrentDeviceUDID "$UDID"
xcrun simctl bootstatus "$UDID" -b >/dev/null
xcrun simctl ui "$UDID" appearance light 2>/dev/null || true
xcrun simctl status_bar "$UDID" override --time "9:41" --batteryState charged --batteryLevel 100 \
  --cellularMode active --cellularBars 4 --wifiBars 3 2>/dev/null || true
xcrun simctl openurl "$UDID" "$URL"

cat <<MSG

SecondLook is open in Safari on the virtual iPhone.
Tip: to show it as an app, tap Share > "Add to Home Screen" in Safari, then open it from the home screen.

Press Enter to START recording.
MSG
read -r
xcrun simctl io "$UDID" recordVideo --codec=h264 --force "$OUT" &
REC=$!
sleep 1
echo "Recording... do your demo, then press Enter to STOP."
read -r
kill -INT "$REC"
wait "$REC" 2>/dev/null || true
xcrun simctl status_bar "$UDID" clear 2>/dev/null || true
echo "Saved $(pwd)/$OUT"
