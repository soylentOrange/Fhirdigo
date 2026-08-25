#!/usr/bin/env python3
"""
Erstellt Anwendungs-Icons mit der Flamme (🔥) für macOS (.icns), Windows (.ico) und Linux (.png).
"""

import os
import sys
import struct
import subprocess
import platform

def create_flame_icons():
    os.makedirs("assets", exist_ok=True)
    png_path = "assets/icon.png"
    ico_path = "assets/icon.ico"
    icns_path = "assets/icon.icns"

    # Erstelle hochauflösendes PNG mit dem Flammen-Symbol 🔥
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()

        canvas = tk.Canvas(root, width=512, height=512, bg="white")
        canvas.pack()
        # Flammen-Emoji zentriert rendern
        canvas.create_text(256, 256, text="🔥", font=("Apple Color Emoji", 320))
        root.update()

        ps_path = "assets/temp_flame.ps"
        canvas.postscript(file=ps_path, colormode="color", width=512, height=512)
        root.destroy()

        # PostScript nach PNG konvertieren
        if platform.system() == "Darwin":
            subprocess.run(["sips", "-s", "format", "png", ps_path, "--out", png_path], check=True, capture_output=True)
        else:
            # Fallback
            subprocess.run(["magick", ps_path, png_path], check=True, capture_output=True)

        if os.path.exists(ps_path):
            os.remove(ps_path)

        print(f"✅ {png_path} erstellt!")
    except Exception as e:
        print(f"⚠️ Hinweis bei der PNG-Generierung: {e}")

    # Erstelle Windows .ico Datei
    if os.path.exists(png_path):
        with open(png_path, "rb") as f:
            png_data = f.read()
        ico_header = struct.pack("<HHH", 0, 1, 1)
        ico_entry = struct.pack("<BBBBHHII", 0, 0, 0, 0, 1, 32, len(png_data), 22)
        with open(ico_path, "wb") as f:
            f.write(ico_header + ico_entry + png_data)
        print(f"✅ {ico_path} erstellt!")

    # Erstelle macOS .icns Datei
    if platform.system() == "Darwin" and os.path.exists(png_path):
        iconset_dir = "assets/Fhirdigo.iconset"
        os.makedirs(iconset_dir, exist_ok=True)
        for size in [16, 32, 64, 128, 256, 512]:
            subprocess.run(["sips", "-z", str(size), str(size), png_path, "--out", f"{iconset_dir}/icon_{size}x{size}.png"], capture_output=True)
            if size <= 256:
                subprocess.run(["sips", "-z", str(size*2), str(size*2), png_path, "--out", f"{iconset_dir}/icon_{size}x{size}@2x.png"], capture_output=True)
        subprocess.run(["iconutil", "-c", "icns", iconset_dir, "-o", icns_path], capture_output=True)
        subprocess.run(["rm", "-rf", iconset_dir])
        print(f"✅ {icns_path} erstellt!")

if __name__ == "__main__":
    create_flame_icons()
