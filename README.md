# TapMeow

Tap your MacBook, get a meow. Lives in your menu bar as a cat emoji.

## What it does

- Cat emoji (🐱) sits in your macOS menu bar
- Click to start listening, tap your MacBook, hear a meow
- Click to pause, tap does nothing
- Uses your MacBook's built-in mic to detect percussive taps
- Filters out speech and ambient noise, only responds to sharp taps

## Run locally

```bash
# Clone
git clone https://github.com/tejassudsfp/TapMeow.git
cd TapMeow

# Install dependencies
pip3 install numpy sounddevice rumps

# Run
python3 tap_meow_app.py
```

macOS will ask for microphone permission on first launch. Grant it.

## Build the .app

```bash
# Install build dependencies
pip3 install pyinstaller

# Generate icons (optional, already included)
pip3 install Pillow
python3 make_icons.py

# Build
pyinstaller TapMeow.spec

# Output at dist/TapMeow.app
```

To share via AirDrop: `zip -r TapMeow.zip dist/TapMeow.app`

Recipients need to right-click > Open the first time (Gatekeeper, since it's not App Store signed).

## Run the original script (no menu bar)

```bash
python3 tap_meow.py
```

This runs in terminal with Ctrl+C to stop. The menu bar version (`tap_meow_app.py`) is the recommended way.

## Files

| File | What |
|---|---|
| `tap_meow_app.py` | Menu bar app (rumps) |
| `tap_meow.py` | Original terminal script |
| `meow.wav` | The meow sound |
| `make_icons.py` | Generates app icon from cat emoji |
| `icon.icns` | Pre-built app icon |
| `TapMeow.spec` | PyInstaller build spec |

## Requirements

- macOS (Apple Silicon)
- Python 3.10+
- Microphone access

## License

MIT
