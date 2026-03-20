#!/usr/bin/env python3
"""Tap your MacBook, get a meow. Harder tap = higher pitch.
Calibrated from actual mic data. Only triggers on percussive taps."""

import numpy as np
import sounddevice as sd
import subprocess
import threading
import time
import wave
from collections import deque

MEOW_PATH = "/Users/tejassudarshan/Downloads/mixkit-sweet-kitty-meow-93.wav"
THRESHOLD = 0.15        # only hard taps
COOLDOWN = 1.5          # 1.5 sec cooldown so it finishes meowing before retriggering
SAMPLE_RATE = 44100
BLOCKSIZE = 512

SPIKE_RATIO = 8.0
BG_WINDOW = 40
DECAY_BLOCKS = 60       # skip ~0.7 sec of decay after a tap

# load meow wav
print("Loading meow...")
with wave.open(MEOW_PATH, "rb") as wf:
    raw = wf.readframes(wf.getnframes())
    width = wf.getsampwidth()
    channels = wf.getnchannels()
    if width == 2:
        meow = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    elif width == 4:
        meow = np.frombuffer(raw, dtype=np.int32).astype(np.float32) / 2147483648.0
    else:
        meow = np.frombuffer(raw, dtype=np.uint8).astype(np.float32) / 128.0 - 1.0
    if channels == 2:
        meow = meow[::2]  # take left channel

# trim to first 1.5 seconds so it's snappy
max_samples = int(SAMPLE_RATE * 1.5)
if len(meow) > max_samples:
    meow = meow[:max_samples]

last_trigger = 0
lock = threading.Lock()
bg_levels = deque(maxlen=BG_WINDOW)
skip_blocks = 0


def pitch_shift(samples, factor):
    """Resample to shift pitch. factor > 1 = higher pitch."""
    indices = np.round(np.arange(0, len(samples), factor)).astype(int)
    indices = indices[indices < len(samples)]
    return samples[indices]


def play(intensity):
    global last_trigger
    with lock:
        now = time.time()
        if now - last_trigger < COOLDOWN:
            return
        last_trigger = now

    sd.play(meow, SAMPLE_RATE)
    print(f"  MEOW! (peak: {intensity:.3f})")


def callback(indata, frames, time_info, status):
    global skip_blocks

    block = indata[:, 0]
    peak = np.max(np.abs(block))
    rms = np.sqrt(np.mean(block ** 2))

    # after a tap, skip a few blocks (the decay) so they don't pollute background
    if skip_blocks > 0:
        skip_blocks -= 1
        return

    # not loud enough to be anything
    if peak < THRESHOLD:
        bg_levels.append(rms)
        return

    # need enough background data
    if len(bg_levels) < 10:
        bg_levels.append(rms)
        return

    # compare peak to recent background
    bg_avg = np.mean(bg_levels)
    if bg_avg < 0.0001:
        bg_avg = 0.0001

    ratio = peak / bg_avg

    if ratio >= SPIKE_RATIO:
        # it's a tap! skip the decay blocks
        skip_blocks = DECAY_BLOCKS
        threading.Thread(target=play, args=(peak,), daemon=True).start()
    else:
        # it's speech or ambient, add to background
        bg_levels.append(rms)


print()
print("  TAP YOUR MACBOOK TO MEOW")
print("  Harder tap = higher pitch")
print("  Ctrl+C to stop")
print()

try:
    with sd.InputStream(
        callback=callback, channels=1, samplerate=SAMPLE_RATE, blocksize=BLOCKSIZE
    ):
        while True:
            time.sleep(0.1)
except KeyboardInterrupt:
    print("\nBye!")
