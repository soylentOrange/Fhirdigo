# Drittanbieter-Lizenzen

Fhirdigo selbst steht unter der [Apache License 2.0](LICENSE). Die folgenden Komponenten
werden zur Laufzeit verwendet bzw. von `build.py` (PyInstaller) in die eigenständige
Anwendung gebündelt. Bei Weitergabe der gebauten Anwendung (`.exe` / `.app`) sind die
Lizenztexte dieser Komponenten beizulegen; sie liegen den jeweiligen Paketen bei
(`*.dist-info/licenses/` bzw. `LICENSE` im Quellrepository).

## Laufzeit-Abhängigkeiten (im Build enthalten)

| Komponente | Lizenz | Quelle |
| :--- | :--- | :--- |
| customtkinter | MIT | https://github.com/TomSchimansky/CustomTkinter |
| darkdetect | BSD-3-Clause | https://github.com/albertosottile/darkdetect |
| packaging | Apache-2.0 OR BSD-2-Clause | https://github.com/pypa/packaging |
| requests | Apache-2.0 | https://github.com/psf/requests |
| urllib3 | MIT | https://github.com/urllib3/urllib3 |
| idna | BSD-3-Clause | https://github.com/kjd/idna |
| charset-normalizer | MIT | https://github.com/jawah/charset_normalizer |
| certifi | MPL-2.0 | https://github.com/certifi/python-certifi |
| tkinterdnd2 | MIT | https://github.com/Eliav2/tkinterdnd2 |
| tkdnd (native Bibliothek, über tkinterdnd2) | BSD-artig (Tcl-Lizenz) | https://github.com/petasis/tkdnd |
| Python (inkl. tkinter) | PSF-2.0 | https://www.python.org |
| Tcl/Tk | Tcl/Tk-Lizenz (BSD-artig) | https://www.tcl-lang.org |
| OpenSSL (über Python) | Apache-2.0 | https://www.openssl.org |

`certifi` (MPL-2.0) wird unverändert weitergegeben; der Quellcode ist unter dem oben
genannten Link verfügbar.

## Build-Werkzeuge (nicht Teil der Anwendung)

| Komponente | Lizenz | Hinweis |
| :--- | :--- | :--- |
| PyInstaller | GPL-2.0-or-later mit Bootloader-Ausnahme | Die Ausnahme erlaubt die Verbreitung der erzeugten Anwendung unter beliebiger Lizenz. |
| pyinstaller-hooks-contrib | Apache-2.0 / GPL-2.0 | nur zur Build-Zeit |
| altgraph | MIT | nur zur Build-Zeit |
| setuptools | MIT | nur zur Build-Zeit |

## Optionale bzw. in `tools/environment.yaml` aufgeführte Pakete

| Komponente | Lizenz |
| :--- | :--- |
| fhirpy | MIT |
| fhir.resources / fhir-core | BSD-3-Clause |
| python-dotenv | BSD-3-Clause |

## Grafiken

| Datei | Lizenz |
| :--- | :--- |
| `assets/icon.svg`, `icon.png`, `icon.ico`, `icon.icns` | Apache-2.0 (Bestandteil des Projekts) |
| `assets/bmbf_gefoerdert_vom.jpeg` | **nicht** unter Apache-2.0; Förderlogo des Bundesministeriums, Nutzung nur gemäß Förderrichtlinien |
