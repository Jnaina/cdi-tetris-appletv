#!/bin/sh
# Build + sign + install CD-i Tetris (RetroArch tvOS + same_cdi core) on an Apple TV.
# usage: ./build-and-install.sh <TEAM_ID> <APPLE_TV_UDID>
set -e
TEAM="$1"; DEV="$2"
[ -n "$TEAM" ] && [ -n "$DEV" ] || { echo "usage: $0 <TEAM_ID> <APPLE_TV_UDID>"; exit 1; }
ROOT="$(cd "$(dirname "$0")" && pwd)"
IDENT="${SIGN_IDENTITY:?set SIGN_IDENTITY to your Apple Development signing identity hash (security find-identity -v -p codesigning)}"
cd "$ROOT/RetroArch/pkg/apple"
HP=$(find WebServer -name '*.h' -exec dirname {} \; | sort -u | sed 's|^|$(SRCROOT)/|' | tr '\n' ' ')
xcodebuild -project RetroArch_iOS13.xcodeproj -scheme "RetroArch tvOS Release" -sdk appletvos -configuration Release \
  -destination "id=$DEV" -allowProvisioningUpdates -allowProvisioningDeviceRegistration DEVELOPMENT_TEAM="$TEAM" \
  TVOS_DEPLOYMENT_TARGET=16.0 'GCC_PREPROCESSOR_DEFINITIONS=$(inherited) PULSTAR_AUTOLOAD=1' \
  "HEADER_SEARCH_PATHS=\$(inherited) $HP" -derivedDataPath "$ROOT/build-dev" build > "$ROOT/logs/build-dev.log" 2>&1 || { grep -E "error:" "$ROOT/logs/build-dev.log" | sort -u | head; exit 1; }
APP="$ROOT/build-dev/Build/Products/Release-appletvos/RetroArchTV.app"
# game disc image + BIOS go INSIDE the app
mkdir -p "$APP/roms" "$APP/system/same_cdi/bios"
cp "$ROOT/game/Tetris (USA, Europe).cue" "$ROOT/game/Tetris (USA, Europe).bin" "$APP/roms/"
cp "$ROOT/sysbios/cdimono1.zip" "$APP/system/same_cdi/bios/"
codesign --force -s "$IDENT" --entitlements "$ROOT/ents.plist" "$APP"
codesign --verify --deep --strict "$APP" && echo "signed OK"
xcrun devicectl device install app --device "$DEV" "$APP"
xcrun devicectl device process launch --device "$DEV" --terminate-existing com.jnaina.galaga88
