#!/usr/bin/env python3
"""TapMeow - macOS menu bar app. Tap your MacBook, get a meow.

Audio runs in a subprocess so macOS mic indicator doesn't replace the cat.
"""

import sys
import os
import subprocess
import signal
import rumps


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


class TapMeowApp(rumps.App):
    def __init__(self):
        super().__init__("🐱", quit_button=None)
        self.audio_proc = None

        self.toggle_item = rumps.MenuItem("Start Listening", callback=self.toggle)
        self.quit_item = rumps.MenuItem("Quit", callback=self.quit_app)
        self.menu = [self.toggle_item, None, self.quit_item]

    def toggle(self, sender):
        if self.audio_proc and self.audio_proc.poll() is None:
            # Running, stop it
            self.audio_proc.send_signal(signal.SIGINT)
            self.audio_proc.wait()
            self.audio_proc = None
            sender.title = "Start Listening"
            self.title = "🐱"
        else:
            # Start the audio worker as a separate process
            worker = os.path.join(SCRIPT_DIR, "tap_meow_worker.py")
            self.audio_proc = subprocess.Popen(
                [sys.executable, worker],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            sender.title = "Pause"
            self.title = "😺"

    def quit_app(self, _):
        if self.audio_proc and self.audio_proc.poll() is None:
            self.audio_proc.send_signal(signal.SIGINT)
            self.audio_proc.wait()
        rumps.quit_application()


if __name__ == "__main__":
    TapMeowApp().run()
