# TapMeow

Tap your MacBook, hear a meow.

Uses your built-in mic to detect percussive taps on the laptop body. Filters out speech, music, and ambient noise. Only reacts to sharp physical taps.

https://github.com/user-attachments/assets/placeholder

## Quick start

```bash
git clone https://github.com/tejassudsfp/TapMeow.git
cd TapMeow
pip3 install numpy sounddevice rumps
python3 tap_meow_app.py
```

macOS will ask for microphone permission. Grant it.

## Two ways to run

### Menu bar app

```bash
pip3 install numpy sounddevice rumps
python3 tap_meow_app.py
```

A cat emoji appears in your menu bar. Click it to start/pause listening. No Dock icon, stays out of your way.

| State | Icon | Behavior |
|---|---|---|
| Paused | 🐱 | Not listening |
| Listening | 😺 | Tap to meow |

> **Known issue (macOS Tahoe):** macOS replaces the cat emoji with a system mic indicator when listening starts. The menu bar icon and menu become inaccessible. Use `pkill -f tap_meow_app` to stop. This is a macOS privacy UI limitation, not a bug. Working on a fix. Terminal mode works perfectly.

### Terminal mode

```bash
pip3 install numpy sounddevice
python3 tap_meow.py
```

Starts listening immediately. Prints `MEOW!` on each tap. `Ctrl+C` to quit.

## Build a shareable .app

Bundle into a standalone macOS app. No Python needed on the recipient's machine.

```bash
pip3 install pyinstaller
pyinstaller TapMeow.spec
```

App lands in `dist/TapMeow.app`.

**Share via AirDrop:**

```bash
zip -r TapMeow.zip dist/TapMeow.app
```

Recipients right-click > Open the first time (bypasses Gatekeeper).

> Built for Apple Silicon. Won't run on Intel Macs.

## How it works

1. Opens a 44.1kHz audio stream from the built-in mic
2. Tracks background noise level over a sliding window
3. Three-layer tap detection filters out speech and ambient noise:
   - **Spectral flatness**: taps are broadband (flat spectrum), speech is narrowband
   - **Attack sharpness**: taps rise to peak in 1-5 samples, speech builds gradually
   - **Duration check**: if loud for 3+ consecutive blocks, it's speech not a tap
4. Plays `meow.wav` with a 1.5s cooldown between triggers
5. Skips 60 audio blocks after each tap to ignore the decay

## Regenerate the app icon

The cat emoji icon is pre-built (`icon.icns`). To regenerate:

```bash
pip3 install Pillow
python3 make_icons.py
```

Uses macOS native rendering (Swift/AppKit) for full-color emoji.

## Project structure

```
TapMeow/
├── tap_meow_app.py   # Menu bar app (rumps)
├── tap_meow_worker.py # Audio worker (separate process for menu bar app)
├── tap_meow.py       # Terminal script
├── meow.wav          # The meow sound
├── TapMeow.spec      # PyInstaller build config
├── make_icons.py     # Icon generator
├── icon.icns         # App icon (pre-built)
├── icon_512.png      # 512x512 source icon
├── menubar_icon.png  # 22x22 menu bar icon
├── CLAUDE.md         # Claude Code project context
├── LICENSE           # MIT
└── README.md
```

## Requirements

- macOS (Apple Silicon)
- Python 3.10+
- Microphone access

## License

MIT
