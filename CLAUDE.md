# TapMeow - Claude Code Instructions

## What this is

A macOS app that detects taps on a MacBook using the built-in mic and plays a meow sound. Two versions: a rumps menu bar app (`tap_meow_app.py`) and a plain terminal script (`tap_meow.py`).

## Project structure

- `tap_meow_app.py` - Menu bar app using rumps. Cat emoji in menu bar, start/pause toggle, quit.
- `tap_meow.py` - Terminal version. Runs in foreground, Ctrl+C to stop.
- `meow.wav` - Sound file. Both scripts load this from the same directory.
- `make_icons.py` - Generates `icon.icns` and `icon_512.png` from cat emoji using macOS native rendering (Swift/AppKit).
- `TapMeow.spec` - PyInstaller spec for building `dist/TapMeow.app`.
- `icon.icns` - Pre-built app icon.

## How it works

1. Opens an audio input stream via `sounddevice` (44100 Hz, 512-sample blocks)
2. Tracks background RMS noise level over a sliding window
3. When a block's peak exceeds `THRESHOLD` (0.15) AND the peak-to-background ratio exceeds `SPIKE_RATIO` (8.0), it's a tap
4. After a tap, skips `DECAY_BLOCKS` (60) blocks to avoid retriggering on the decay
5. Plays `meow.wav` with a 1.5s cooldown between triggers

## Rules

- `meow.wav` must always be loaded via relative path (next to the script), never hardcoded absolute paths.
- The menu bar app (`tap_meow_app.py`) uses `sys._MEIPASS` for PyInstaller bundle paths, falling back to `__file__` directory.
- Detection parameters (THRESHOLD, SPIKE_RATIO, COOLDOWN, DECAY_BLOCKS) are tuned for MacBook built-in mics. Don't change without testing.
- The .app bundle must have `LSUIElement: true` in Info.plist (no Dock icon) and `NSMicrophoneUsageDescription`.

## Dependencies

- `numpy` - audio signal processing
- `sounddevice` - mic input and audio playback
- `rumps` - macOS menu bar app framework (menu bar version only)
- `pyinstaller` - .app bundling (build only)
- `Pillow` - icon generation (build only)

## Building

```bash
pip3 install numpy sounddevice rumps pyinstaller
pyinstaller TapMeow.spec
# Output: dist/TapMeow.app
```

## Running

```bash
# Menu bar version
python3 tap_meow_app.py

# Terminal version
python3 tap_meow.py
```
