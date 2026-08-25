#!/usr/bin/env python3
"""
Build-Skript zur Erstellung einer eigenständig lauffähigen Fhirdigo-Anwendung mit PyInstaller.

Aufruf:
    python build.py
"""

import os
import sys
import platform
import subprocess

def main():
    print("=" * 60)
    print("🚀 Fhirdigo Build-Skript (PyInstaller)")
    print(f"   Betriebssystem: {platform.system()} ({platform.machine()})")
    print(f"   Python Version: {platform.python_version()}")
    print("=" * 60)

    # Prüfen, ob PyInstaller installiert ist
    try:
        import PyInstaller
        print(f"✅ PyInstaller gefunden (Version {PyInstaller.__version__})")
    except ImportError:
        print("❌ PyInstaller ist nicht installiert.")
        print("   Installiere PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Basis-Parameter
    app_name = "Fhirdigo"
    main_script = "IndigoSync.py"
    sep = ";" if platform.system() == "Windows" else ":"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        f"--name={app_name}",
        "--collect-all=customtkinter",
        "--collect-all=tkinterdnd2",
    ]

    # Assets-Ordner hinzufügen, falls vorhanden
    if os.path.exists("assets"):
        cmd.append(f"--add-data=assets{sep}assets")

    # Icon hinzufügen
    if platform.system() == "Darwin" and os.path.exists("assets/icon.icns"):
        cmd.append("--icon=assets/icon.icns")
    elif os.path.exists("assets/icon.ico"):
        cmd.append("--icon=assets/icon.ico")
    elif os.path.exists("assets/icon.png"):
        cmd.append("--icon=assets/icon.png")

    # Plattformspezifische Optionen
    if platform.system() == "Darwin":  # macOS
        print("🍏 Erstelle macOS .app Bundle mit FHIR-Flammen-Icon...")
        cmd.extend(["--onedir"])
    elif platform.system() == "Windows":
        print("🪟 Erstelle Windows .exe mit FHIR-Flammen-Icon...")
        cmd.extend(["--onefile"])
    else:  # Linux / andere
        print("🐧 Erstelle Linux Executable...")
        cmd.extend(["--onefile"])

    cmd.append(main_script)

    print(f"\n📦 Starte Build-Befehl:\n   {' '.join(cmd)}\n")
    try:
        subprocess.check_call(cmd)
        print("\n" + "=" * 60)
        print("🎉 Build erfolgreich abgeschlossen!")
        if platform.system() == "Darwin":
            print(f"📁 Die Anwendung liegt in: dist/{app_name}.app")
        elif platform.system() == "Windows":
            print(f"📁 Die Anwendung liegt in: dist/{app_name}.exe")
        else:
            print(f"📁 Die Anwendung liegt in: dist/{app_name}")
        print("=" * 60)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build fehlgeschlagen mit Fehlercode: {e.returncode}")
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()

