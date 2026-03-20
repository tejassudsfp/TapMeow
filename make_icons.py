#!/usr/bin/env python3
"""Generate TapMeow app icon (.icns) using macOS native emoji rendering."""

import subprocess
import os
import tempfile

BASE = os.path.dirname(os.path.abspath(__file__))

# Use macOS Swift to render the emoji natively with full color
swift_code = '''
import AppKit

func renderEmoji(_ emoji: String, size: CGFloat, outputPath: String) {
    let img = NSImage(size: NSSize(width: size, height: size))
    img.lockFocus()

    let attrs: [NSAttributedString.Key: Any] = [
        .font: NSFont.systemFont(ofSize: size * 0.85)
    ]
    let str = NSAttributedString(string: emoji, attributes: attrs)
    let strSize = str.size()
    let x = (size - strSize.width) / 2
    let y = (size - strSize.height) / 2
    str.draw(at: NSPoint(x: x, y: y))

    img.unlockFocus()

    guard let tiffData = img.tiffRepresentation,
          let bitmap = NSBitmapImageRep(data: tiffData),
          let pngData = bitmap.representation(using: .png, properties: [:]) else {
        print("Failed to render")
        return
    }

    try! pngData.write(to: URL(fileURLWithPath: outputPath))
    print("Saved \\(outputPath)")
}

let base = CommandLine.arguments[1]
renderEmoji("🐱", size: 512, outputPath: base + "/icon_512.png")
renderEmoji("🐱", size: 22, outputPath: base + "/menubar_icon.png")
'''

# Write and run Swift script
swift_path = os.path.join(BASE, "_make_icon.swift")
with open(swift_path, "w") as f:
    f.write(swift_code)

result = subprocess.run(
    ["swift", swift_path, BASE],
    capture_output=True, text=True
)
print(result.stdout)
if result.stderr:
    print(result.stderr)

os.remove(swift_path)

# Convert to .icns using iconset
icon_png = os.path.join(BASE, "icon_512.png")
iconset_dir = os.path.join(BASE, "TapMeow.iconset")
os.makedirs(iconset_dir, exist_ok=True)

sizes = [16, 32, 64, 128, 256, 512]
for s in sizes:
    out = os.path.join(iconset_dir, f"icon_{s}x{s}.png")
    subprocess.run(["sips", "-z", str(s), str(s), icon_png, "--out", out],
                   capture_output=True)
    if s <= 256:
        out2x = os.path.join(iconset_dir, f"icon_{s}x{s}@2x.png")
        s2 = s * 2
        subprocess.run(["sips", "-z", str(s2), str(s2), icon_png, "--out", out2x],
                       capture_output=True)

icns_path = os.path.join(BASE, "icon.icns")
result = subprocess.run(["iconutil", "-c", "icns", iconset_dir, "-o", icns_path],
                        capture_output=True, text=True)
if result.returncode == 0:
    print(f"Saved {icns_path}")
else:
    print(f"iconutil error: {result.stderr}")

# Cleanup iconset dir
import shutil
shutil.rmtree(iconset_dir, ignore_errors=True)

print("Done!")
