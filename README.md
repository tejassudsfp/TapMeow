# TapMeow

Tap your MacBook, get a meow. Two ways to run it.

## What it does

- Uses your MacBook's built-in mic to detect percussive taps
- Filters out speech and ambient noise, only responds to sharp taps
- Tap your laptop, hear a meow

## Run locally

### Option 1: Menu bar app (recommended)

Cat emoji sits in your macOS menu bar. Click to start/pause.

```bash
git clone https://github.com/tejassudsfp/TapMeow.git
cd TapMeow
pip3 install numpy sounddevice rumps
python3 tap_meow_app.py
```

- 🐱 appears in your menu bar
- Click it, hit "Start Listening"
- Tap your MacBook, hear a meow
- Click "Pause" to stop, "Quit" to exit

### Option 2: Terminal script

Runs in your terminal. No menu bar, no GUI. Ctrl+C to stop.

```bash
git clone https://github.com/tejassudsfp/TapMeow.git
cd TapMeow
pip3 install numpy sounddevice
python3 tap_meow.py
```

Starts listening immediately. Tap your MacBook, see "MEOW!" in the terminal and hear the sound.

## Build a shareable .app

Bundle it into a standalone macOS app you can AirDrop to friends.

```bash
pip3 install pyinstaller
pyinstaller TapMeow.spec
```

Output at `dist/TapMeow.app`. To share:

```bash
zip -r TapMeow.zip dist/TapMeow.app
```

Recipients need to right-click > Open the first time (not App Store signed).

Apple Silicon only. Won't run on Intel Macs.

## Files

| File | What |
|---|---|
| `tap_meow_app.py` | Menu bar app (rumps) |
| `tap_meow.py` | Terminal script |
| `meow.wav` | The meow sound |
| `make_icons.py` | Generates app icon from cat emoji |
| `icon.icns` | Pre-built app icon |
| `TapMeow.spec` | PyInstaller build spec |

## Requirements

- macOS (Apple Silicon)
- Python 3.10+
- Microphone access (macOS will prompt on first run)

## License

MIT
