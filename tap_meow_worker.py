#!/usr/bin/env python3
"""Audio worker for TapMeow. Runs as a separate process.
Handles mic input, tap detection, and meow playback.
Stops cleanly on SIGINT."""

import os
import numpy as np
import sounddevice as sd
import threading
import time
import wave
from collections import deque

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MEOW_PATH = os.path.join(SCRIPT_DIR, "meow.wav")

SAMPLE_RATE = 44100
BLOCKSIZE = 512
COOLDOWN = 1.5
PEAK_THRESHOLD = 0.15
SPIKE_RATIO = 8.0
FLATNESS_THRESHOLD = 0.3
DURATION_BLOCKS = 3
BG_WINDOW = 40
DECAY_BLOCKS = 60

# Load meow
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
        meow = meow[::2]

max_samples = int(SAMPLE_RATE * 1.5)
if len(meow) > max_samples:
    meow = meow[:max_samples]

last_trigger = 0
lock = threading.Lock()
bg_levels = deque(maxlen=BG_WINDOW)
skip_blocks = 0
loud_streak = 0


def spectral_flatness(block):
    fft = np.abs(np.fft.rfft(block))
    fft = fft[1:] + 1e-10
    geo_mean = np.exp(np.mean(np.log(fft)))
    arith_mean = np.mean(fft)
    return geo_mean / (arith_mean + 1e-10)


def attack_sharpness(block):
    abs_block = np.abs(block)
    peak_idx = np.argmax(abs_block)
    peak_val = abs_block[peak_idx]
    if peak_val < 0.01 or peak_idx == 0:
        return 0.0
    threshold_10pct = peak_val * 0.1
    start_idx = peak_idx
    for i in range(peak_idx - 1, -1, -1):
        if abs_block[i] < threshold_10pct:
            start_idx = i
            break
    rise_samples = peak_idx - start_idx
    return max(0.0, 1.0 - (rise_samples / 50.0))


def play_meow():
    global last_trigger
    with lock:
        now = time.time()
        if now - last_trigger < COOLDOWN:
            return
        last_trigger = now
    sd.play(meow, SAMPLE_RATE)


def callback(indata, frames, time_info, status):
    global skip_blocks, loud_streak

    block = indata[:, 0]
    peak = np.max(np.abs(block))
    rms = np.sqrt(np.mean(block ** 2))

    if skip_blocks > 0:
        skip_blocks -= 1
        return
    if peak < PEAK_THRESHOLD:
        bg_levels.append(rms)
        loud_streak = 0
        return
    if len(bg_levels) < 10:
        bg_levels.append(rms)
        return

    bg_avg = np.mean(bg_levels)
    if bg_avg < 0.0001:
        bg_avg = 0.0001
    ratio = peak / bg_avg

    if ratio < SPIKE_RATIO:
        bg_levels.append(rms)
        loud_streak = 0
        return

    loud_streak += 1
    if loud_streak > DURATION_BLOCKS:
        bg_levels.append(rms)
        return

    flatness = spectral_flatness(block)
    if flatness < FLATNESS_THRESHOLD:
        return

    sharpness = attack_sharpness(block)
    if sharpness < 0.5:
        return

    skip_blocks = DECAY_BLOCKS
    loud_streak = 0
    threading.Thread(target=play_meow, daemon=True).start()


try:
    with sd.InputStream(
        callback=callback, channels=1,
        samplerate=SAMPLE_RATE, blocksize=BLOCKSIZE,
    ):
        while True:
            time.sleep(0.1)
except KeyboardInterrupt:
    pass
