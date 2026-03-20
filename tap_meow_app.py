#!/usr/bin/env python3
"""TapMeow - macOS menu bar app. Tap your MacBook, get a meow."""

import sys
import os
import numpy as np
import sounddevice as sd
import threading
import time
import wave
from collections import deque

import rumps


def resource_path(filename):
    """Get path to bundled resource, works for dev and PyInstaller."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


# Audio detection settings
THRESHOLD = 0.15
COOLDOWN = 1.5
SAMPLE_RATE = 44100
BLOCKSIZE = 512
SPIKE_RATIO = 8.0
BG_WINDOW = 40
DECAY_BLOCKS = 60


def load_meow():
    """Load and prepare the meow sound."""
    meow_path = resource_path("meow.wav")
    with wave.open(meow_path, "rb") as wf:
        raw = wf.readframes(wf.getnframes())
        width = wf.getsampwidth()
        channels = wf.getnchannels()
        if width == 2:
            samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        elif width == 4:
            samples = np.frombuffer(raw, dtype=np.int32).astype(np.float32) / 2147483648.0
        else:
            samples = np.frombuffer(raw, dtype=np.uint8).astype(np.float32) / 128.0 - 1.0
        if channels == 2:
            samples = samples[::2]

    # Trim to 1.5 seconds
    max_samples = int(SAMPLE_RATE * 1.5)
    if len(samples) > max_samples:
        samples = samples[:max_samples]
    return samples


class TapMeowApp(rumps.App):
    def __init__(self):
        super().__init__("🐱", quit_button=None)

        self.listening = False
        self.stream = None
        self.meow_samples = load_meow()

        # Tap detection state
        self.last_trigger = 0
        self.trigger_lock = threading.Lock()
        self.bg_levels = deque(maxlen=BG_WINDOW)
        self.skip_blocks = 0

        self.toggle_item = rumps.MenuItem("Start Listening", callback=self.toggle)
        self.quit_item = rumps.MenuItem("Quit", callback=self.quit_app)
        self.menu = [self.toggle_item, None, self.quit_item]

    def toggle(self, sender):
        if self.listening:
            self.stop_listening()
            sender.title = "Start Listening"
            self.title = "🐱"
        else:
            self.start_listening()
            sender.title = "Pause"
            self.title = "😺"

    def start_listening(self):
        self.listening = True
        self.bg_levels.clear()
        self.skip_blocks = 0
        self.stream = sd.InputStream(
            callback=self.audio_callback,
            channels=1,
            samplerate=SAMPLE_RATE,
            blocksize=BLOCKSIZE,
        )
        self.stream.start()

    def stop_listening(self):
        self.listening = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

    def audio_callback(self, indata, frames, time_info, status):
        if not self.listening:
            return

        block = indata[:, 0]
        peak = np.max(np.abs(block))
        rms = np.sqrt(np.mean(block ** 2))

        if self.skip_blocks > 0:
            self.skip_blocks -= 1
            return

        if peak < THRESHOLD:
            self.bg_levels.append(rms)
            return

        if len(self.bg_levels) < 10:
            self.bg_levels.append(rms)
            return

        bg_avg = np.mean(self.bg_levels)
        if bg_avg < 0.0001:
            bg_avg = 0.0001

        ratio = peak / bg_avg

        if ratio >= SPIKE_RATIO:
            self.skip_blocks = DECAY_BLOCKS
            threading.Thread(target=self.play_meow, args=(peak,), daemon=True).start()
        else:
            self.bg_levels.append(rms)

    def play_meow(self, intensity):
        with self.trigger_lock:
            now = time.time()
            if now - self.last_trigger < COOLDOWN:
                return
            self.last_trigger = now

        sd.play(self.meow_samples, SAMPLE_RATE)

    def quit_app(self, _):
        self.stop_listening()
        rumps.quit_application()


if __name__ == "__main__":
    TapMeowApp().run()
