# CD-i Tetris for Apple TV

A tvOS app that plays **your own** copy of the Philips CD-i game *Tetris (USA, Europe)* on an Apple TV, using
[RetroArch](https://github.com/libretro/RetroArch)'s tvOS front end and the libretro `same_cdi` core (MAME's CD-i driver).
The disc image and the CD-i BIOS are embedded in the app bundle at build time.

**This repository contains no game, disc image, BIOS or emulator binary.** You must supply those yourself, from media and
hardware you own. It only holds the glue: a small RetroArch patch, the build/install script, and an icon generator
(an original drawing of falling blocks).

![icon](preview/icon.png)

## What the patch does (`patches/ui_cocoatouch-cdi.patch`, against RetroArch v1.22.2)
- Auto-loads `same.cdi.libretro` with the embedded `roms/Tetris (USA, Europe).cue` at launch and writes a speed-first config
  (RetroArch paces the core, PAL 50 Hz timing, larger audio buffer).
- Logs emulated frames per second to `Caches/fps.log`.
- The Philips player menu waits for PLAY CD-I. The app watches the picture and taps A once when the grey menu is on screen
  (at most twice, 30 s apart); it stops for good on any real controller press and after 7 minutes, so nothing is injected into the game.

## Build
1. `git clone --branch v1.22.2 https://github.com/libretro/RetroArch RetroArch` and `cd RetroArch && patch -p1 < ../patches/ui_cocoatouch-cdi.patch`.
2. Download `same_cdi_libretro_tvos.dylib` from `https://buildbot.libretro.com/nightly/apple/tvos-arm64/latest/` (unzip) into `RetroArch/pkg/apple/tvOS/modules/`.
3. In `RetroArch/pkg/apple/RetroArch_iOS13.xcodeproj/project.pbxproj` set `TVOS_BUNDLE_IDENTIFIER` to your own bundle id, and set `CFBundleDisplayName` in `pkg/apple/tvOS/Info.plist`.
4. Put your disc (`Tetris (USA, Europe).cue` + `.bin`) in `game/` and a MAME `cdimono1.zip` (cdi200.rom plus the servo and slave ROMs) in `sysbios/`.
5. `python3 make_art_cdi.py` (needs Pillow), copy `ents.plist.template` to `ents.plist` and fill in your team id and bundle id.
6. `./build-and-install.sh <TEAM_ID> <APPLE_TV_UDID>` (set `SIGN_IDENTITY` to your signing identity hash).

## Notes
- Tested on an Apple TV 4K (1st generation, A10X): steady 50 FPS.
- Controls: D-pad and the two face buttons (Cross/Circle on a PS5 pad) map to the CD-i controller's directions and buttons 1/2.
- No JIT is used or needed (the 68k core is an interpreter).
- RetroArch is GPLv3; the patch is a derivative of `ui/drivers/ui_cocoatouch.m` and carries the same license.
